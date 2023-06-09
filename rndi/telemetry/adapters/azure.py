#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import hashlib
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import sampling, Tracer, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.trace import NonRecordingSpan, Span, SpanContext
from pkg_resources import DistributionNotFound, get_distribution
from rndi.connect.business_objects.adapters import Request
from rndi.telemetry.adapters.null import DummySpan
from rndi.telemetry.contracts import Observer


def generate_trace_id(request_id: str, length: int = 16):
    """
    - Calculate the hash SHA-256 for a string
    - Take the first 16 bytes (128 bits) of the hash
    - Convert the 16 bytes to integer
    :param length:
    :param request_id: The id
    :return:
    """
    hash_object = hashlib.sha256(request_id.encode('utf-8'))
    return int.from_bytes(hash_object.digest()[:length], byteorder='big')


def hydrate_span_with_product_action_attributes(span: Span, body):
    """
    Given a Product Action Body, hydrate the span attributes with the body of this action.
    This allows us to generate better panels into an Azure Insights Application Workbook
    """
    try:
        attributes = {}
        # if there is an asset_id or a configuration_id in the body, add it to attributes
        jwt_payload = body.get('jwt_payload')

        if jwt_payload is None:
            return

        asset_id = jwt_payload.get('asset_id')
        configuration_id = jwt_payload.get('configuration_id')

        if asset_id is not None:
            attributes['asset_id'] = asset_id

        if configuration_id is not None:
            attributes['configuration_id'] = configuration_id

        span.set_attributes(attributes)
    except Exception:
        """We don't want to break the execution at any cost"""
        return


def hydrate_span_with_request_attributes(span, request: dict):
    """
    Given a request and a span, hydrate the span attributes with the request attributes
    we wanted to track, so we can use them in the Azure Monitor
    :param span:
    :param request:
    :return:
    """
    try:
        request = Request(request)
        if request.is_asset_request():
            span.set_attributes({
                'vendor_id': request.asset().connection('vendor', {}).get('id'),
                'product_id': request.asset().product('id'),
                'marketplace_id': request.asset().marketplace('id'),
                'contract_id': request.asset().contract('id'),
                'connection_id': request.asset().connection('id'),
                'asset_id': request.asset().id(),
                'request_id': request.id(),
                'request_status': request.status(),
                'request_type': request.type(),
            })

        if request.is_tier_config_request():
            span.set_attributes({
                'vendor_id': request.tier_configuration().connection('vendor', {}).get('id'),
                'product_id': request.tier_configuration().product('id'),
                'marketplace_id': request.tier_configuration().marketplace('id'),
                'connection_id': request.tier_configuration().connection('id'),
                'tier_config_id': request.tier_configuration().id(),
                'request_id': request.id(),
                'request_status': request.status(),
                'request_type': request.type(),
            })
    except Exception:
        """We don't want to break the execution at any cost"""
        return


def get_context(request_id: str):
    return trace.set_span_in_context(NonRecordingSpan(
        SpanContext(
            trace_id=generate_trace_id(request_id),
            span_id=generate_trace_id(request_id, 8),
            is_remote=False,
        )))


def provide_azure_insights_observer_telemetry_adapter(
        config: dict,
        automatic_instrumentation: List[Callable[[], None]],
        exporter: Optional[SpanExporter] = None,
) -> Observer:
    try:
        tracer_provider = TracerProvider(
            sampler=sampling.ALWAYS_ON,
            resource=Resource.create({
                "service.name": config.get('TELEMETRY_SERVICE_NAME'),
                "service.version": get_distribution(config.get('TELEMETRY_SERVICE_NAME')).version,
                "connect.extension-runner": get_distribution("connect-extension-runner").version,
                "connect.openapi-client": get_distribution("connect-openapi-client").version,
            }),
        )
    except DistributionNotFound:
        tracer_provider = TracerProvider(
            sampler=sampling.ALWAYS_ON,
            resource=Resource.create({
                "service.name": config.get('TELEMETRY_SERVICE_NAME'),
                "service.version": config.get('TELEMETRY_SERVICE_VERSION'),
                "connect.extension-runner": config.get('TELEMETRY_CONNECT_EXTENSION_RUNNER_VERSION'),
                "connect.openapi-client": config.get('TELEMETRY_CONNECT_OPEN_API_VERSION'),
            }),
        )

    if exporter is None:
        exporter = AzureMonitorTraceExporter.from_connection_string(
            config.get('INSIGHTS_CONNECTION_STRING'),
        )

    trace.set_tracer_provider(tracer_provider)
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)

    return DevOpsExtensionAzureInsightsObserverAdapter(
        connection_string=config.get('INSIGHTS_CONNECTION_STRING'),
        automatic_instrumentation=automatic_instrumentation,
        tracer=trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )


def get_transaction_id_for_product_action(request: dict):
    """
    Get the transaction id for a product action
    :return:
    """
    if request.get('jwt_payload', {}).get('configuration_id'):
        return request.get('jwt_payload', {}).get('configuration_id')

    if request.get('jwt_payload', {}).get('asset_id'):
        return request.get('jwt_payload', {}).get('asset_id')

    return None


def is_product_action_request(request: dict) -> bool:
    """
    We assume a product action WILL 100% of the times include the JWT_PAYLOAD, and no other
    integration will do that so if this property exists, it is a product action.
    """
    has_jwt_payload = request.get('jwt_payload') is not None
    has_configuration_id = request.get('jwt_payload', {}).get('configuration_id') is not None
    has_asset_id = request.get('jwt_payload', {}).get('asset_id') is not None

    return has_jwt_payload and (has_configuration_id or has_asset_id)


def is_background_event_request(request: dict) -> bool:
    """
    For normal background events we will just look for the request id
    """
    return request.get('id') is not None


def is_custom_event_request(request: dict):
    """
    Use always after a fallback check for the other methods, if none was success, check if body is present.
    If it is, we can assume it is a custom event.
    """
    return request.get('body') is not None


class DevOpsExtensionAzureInsightsObserverAdapter(Observer):
    def __init__(
            self,
            connection_string: str,
            tracer: Tracer,
            automatic_instrumentation: Optional[List[Callable]] = None,
    ):
        self.tracer = tracer
        self.connection_string = connection_string
        self.business_transaction: Optional[Span] = None
        if not automatic_instrumentation:
            automatic_instrumentation = []

        for instrument in automatic_instrumentation:
            instrument()

    @contextmanager
    def trace(self, name: str, context: Dict[str, Any]) -> Iterator[Span]:
        """
        For Business Transactions we expect an identifier to be present in the context, it is
        needed because we need to correlate the high level operation with the low level
        operations that are being executed in the background.
        We don't want the observer to crash the entire application if we could not generate
        a trace_id for the high level operation, so just in case an 'id' is not provided in the
        context we will just yield None and the observer will not do anything.
        That way we will not cause the side effect of crashing the application, and instead
        we will just lose observability for that runtime execution.
        """
        if self.business_transaction is None:
            if is_background_event_request(context):
                with self.tracer.start_as_current_span(
                        name,
                        context=get_context(context.get('id')),
                ) as span:
                    self.business_transaction = span
                    hydrate_span_with_request_attributes(span, context)
                    yield span
                return

            if is_product_action_request(context):
                with self.tracer.start_as_current_span(
                        name,
                        context=get_context(get_transaction_id_for_product_action(context)),
                ) as span:
                    self.business_transaction = span
                    hydrate_span_with_product_action_attributes(span, context)
                    yield span
                return

            if is_custom_event_request(context):
                with self.tracer.start_as_current_span(
                        name,
                        context=get_context(context.get('body').__str__()),
                ) as span:
                    self.business_transaction = span
                    yield span
                return
            # if no possible option was found, just return a dummy span who will not generate traces.
            with DummySpan() as span:
                yield span
        else:
            with self.tracer.start_as_current_span(name) as span:
                hydrate_span_with_request_attributes(span, context)
                yield span
