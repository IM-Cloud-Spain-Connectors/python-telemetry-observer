#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from opentelemetry import trace
from opentelemetry.context import Context
from rndi.telemetry.adapters.azure import generate_trace_id, get_context, DevOpsExtensionAzureInsightsObserverAdapter
from rndi.telemetry.adapters.null import NoneObserverAdapter


def test_none_observer_adapter_should_do_nothing():
    observer = NoneObserverAdapter()
    observer.trace('test', {})
    # Just assert that no exception is thrown
    assert True


def test_get_context_should_set_context_in_trace():
    context = get_context('for-some-request')
    assert isinstance(context, Context)
    assert generate_trace_id('for-some-request') == context.get(next(iter(context)), {})._context.trace_id
    assert generate_trace_id('for-some-request', 8) == context.get(next(iter(context)), {})._context.span_id

def test_insights_adapter_return_dummy_span_on_unknown_request_format():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('product_action', {}) as span:
        assert span is None

def test_insights_adapter_should_create_non_recording_span_on_background_event_request():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('background_event', {
        'id': 'PR-1234-1234-1324'
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)

def test_insights_adapter_should_create_non_recording_span_on_product_action_request_for_asset():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('background_event', {
        'jwt_payload': {
            'asset_id': '1234'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)


def test_insights_adapter_should_create_non_recording_span_on_product_action_request_for_tier_configuration():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('background_event', {
        'jwt_payload': {
            'configuration_id': '1234'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)


def test_insights_adapter_should_create_default_span_on_product_action_on_nested_trace_call_for_tier_configuration():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('product_action_for_tier_configuration_parent_trace', {
        'jwt_payload': {
            'configuration_id': '1234'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)
        with adapter.trace('product_action_for_tier_configuration_technical_transaction', {
            'jwt_payload': {
                'configuration_id': '1234'
            }
        }) as nested_span:
            assert nested_span is not None
            assert isinstance(nested_span, trace.Span)

def test_insights_adapter_should_create_default_span_on_product_action_on_nested_trace_call_for_asset():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('product_action_for_asset_parent_trace', {
        'jwt_payload': {
            'asset_id': '1234'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)
        with adapter.trace('product_action_for_asset_technical_transaction', {
            'jwt_payload': {
                'asset_id': '1234'
            }
        }) as nested_span:
            assert nested_span is not None
            assert isinstance(nested_span, trace.Span)


def test_insights_adapter_should_create_parent_trace_for_custom_event():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('custom_event_parent_trace', {
        'body': {
            'first-key': 'first-value',
            'second-key': 'second-value'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)


def test_insights_adapter_should_create_nested_trace_for_custom_event():
    adapter = DevOpsExtensionAzureInsightsObserverAdapter(
        'fake-connection-string',
        trace.get_tracer('TELEMETRY_SERVICE_NAME'),
    )

    with adapter.trace('custom_event_parent_trace', {
        'body': {
            'first-key': 'first-value',
            'second-key': 'second-value'
        }
    }) as span:
        assert span is not None
        assert isinstance(span, trace.NonRecordingSpan)

        with adapter.trace('custom_event_nested_technical_transaction', {
            'body': {
                'first-key': 'first-value',
                'second-key': 'second-value'
            }
        }) as nested_span:
            assert nested_span is not None
            assert isinstance(nested_span, trace.Span)
