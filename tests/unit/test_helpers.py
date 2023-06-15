#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#

from opentelemetry.sdk import trace
from rndi.telemetry.adapters.azure import (
    generate_trace_id,
    get_transaction_id_for_product_action,
    hydrate_span_with_product_action_attributes,
    hydrate_span_with_request_attributes,
    is_background_event_request,
    is_custom_event_request,
    is_product_action_request,
)

ASSET_REQUEST = {
    'id': 'PR-0000-0000-0000-001',
    'status': 'pending',
    'type': 'purchase',
    'asset': {
        'id': 'AST-0000-0000-0000-001',
        'connection': {
            'id': 'CN-0000-0000-0000-001',
            'vendor': {
                'id': 'VR-0000-0000-0000-001',
            },
        },
        'product': {
            'id': 'PRD-0000-0000-0000-001',
        },
        'marketplace': {
            'id': 'MP-0000-0000-0000-001',
        },
        'contract': {
            'id': 'CT-0000-0000-0000-001',
        },
    },
}

TIER_CONFIG_REQUEST = {
    'id': 'TCR-0000-0000-0000-001',
    'status': 'pending',
    'type': 'setup',
    'configuration': {
        'id': 'AST-0000-0000-0000-001',
        'connection': {
            'id': 'CN-0000-0000-0000-001',
            'vendor': {
                'id': 'VR-0000-0000-0000-001',
            },
        },
        'product': {
            'id': 'PRD-0000-0000-0000-001',
        },
        'marketplace': {
            'id': 'MP-0000-0000-0000-001',
        },
        'contract': {
            'id': 'CT-0000-0000-0000-001',
        },
    },
}


def test_generate_trace_id_should_generate_a_valid_trace_id():
    # Arrange
    request_id = 'PR-1234-5432-9876-1234'
    # Act
    trace_id = generate_trace_id(request_id)
    # Assert
    assert len(str(trace_id)) == 38
    assert trace_id == 14369405212557582948295945592260865725
    assert isinstance(trace_id, int)


def test_generate_trace_id_should_generate_the_same_trace_id_for_the_same_request_id():
    request_id = 'PR-1234-5432-9876-1234'
    first_trace = generate_trace_id(request_id)
    second_trace = generate_trace_id(request_id)
    assert first_trace == second_trace


def test_generate_trace_id_should_generate_the_same_trace_id_for_8_bit():
    request_id = 'PR-1234-5432-9876-1234'
    first_trace = generate_trace_id(request_id, 8)
    second_trace = generate_trace_id(request_id, 8)
    assert first_trace == second_trace


def test_hydrate_span_should_successfully_hydrate_asset_request():
    tracer_provider = trace.TracerProvider()
    tracer = tracer_provider.get_tracer(__name__)
    span = tracer.start_span("root")
    hydrate_span_with_request_attributes(span, ASSET_REQUEST)

    assert span.attributes.get('request_id') == "PR-0000-0000-0000-001"
    assert span.attributes.get('request_status') == "pending"
    assert span.attributes.get('request_type') == "purchase"


def test_hydrate_span_should_successfully_hydrate_tier_config_request():
    tracer_provider = trace.TracerProvider()
    tracer = tracer_provider.get_tracer(__name__)
    span = tracer.start_span("root")
    hydrate_span_with_request_attributes(span, TIER_CONFIG_REQUEST)

    assert span.attributes.get('request_id') == "TCR-0000-0000-0000-001"
    assert span.attributes.get('request_status') == "pending"
    assert span.attributes.get('request_type') == "setup"


def test_hydrate_span_with_product_action_attributes_should_successfully_hydrate_asset_id():
    tracer_provider = trace.TracerProvider()
    tracer = tracer_provider.get_tracer(__name__)
    span = tracer.start_span("root")

    hydrate_span_with_product_action_attributes(span, {
        'jwt_payload': {
            'asset_id': '12345',
        },
    })

    assert span.attributes.get('asset_id') == "12345"


def test_hydrate_span_with_product_action_attributes_should_successfully_hydrate_with_configuration_id():
    tracer_provider = trace.TracerProvider()
    tracer = tracer_provider.get_tracer(__name__)
    span = tracer.start_span("root")

    hydrate_span_with_product_action_attributes(span, {
        'jwt_payload': {
            'configuration_id': '12345',
        },
    })

    assert span.attributes.get('configuration_id') == "12345"


def test_hydrate_span_with_product_action_attributes_should_be_none_if_no_jwt_payload_provided():
    tracer_provider = trace.TracerProvider()
    tracer = tracer_provider.get_tracer(__name__)
    span = tracer.start_span("root")

    hydrate_span_with_product_action_attributes(span, {})

    assert span.attributes.get('configuration_id') is None
    assert span.attributes.get('asset_id') is None


def test_get_transaction_id_for_product_action_should_successfully_return_none_if_invalid_payload():
    transaction_id = get_transaction_id_for_product_action({})

    assert transaction_id is None


def test_get_transaction_id_for_product_action_should_successfully_return_configuration_id():
    transaction_id = get_transaction_id_for_product_action({
        'jwt_payload': {
            'configuration_id': '12345',
        },
    })

    assert transaction_id == '12345'


def test_get_transaction_id_for_product_action_should_successfully_return_asset_id():
    transaction_id = get_transaction_id_for_product_action({
        'jwt_payload': {
            'asset_id': '12345',
        },
    })

    assert transaction_id == '12345'


def test_is_product_action_request_should_return_false_if_jwt_payload_is_not_none_but_empty():
    is_product_action = is_product_action_request({
        'jwt_payload': {},
    })

    assert is_product_action is False


def test_is_product_action_request_should_return_false_if_jwt_payload_is_none():
    is_product_action = is_product_action_request({})

    assert is_product_action is False


def test_is_product_action_request_should_return_true_if_jwt_payload_has_asset_id():
    is_product_action = is_product_action_request({
        "jwt_payload": {
            "asset_id": "12345",
        },
    })

    assert is_product_action is True


def test_is_product_action_request_should_return_true_if_jwt_payload_has_configuration_id():
    is_product_action = is_product_action_request({
        "jwt_payload": {
            "configuration_id": "12345",
        },
    })

    assert is_product_action is True


def test_is_background_event_request_should_return_true_if_id_is_present():
    is_background_event = is_background_event_request({
        "id": "12345",
    })

    assert is_background_event is True


def test_is_background_event_request_should_return_false_if_id_is_not_present():
    is_background_event = is_background_event_request({})

    assert is_background_event is False


def test_is_custom_event_request_should_return_true_if_body_is_present():
    is_custom_event = is_custom_event_request({
        "body": {},
    })

    assert is_custom_event is True


def test_is_custom_event_request_should_return_false_if_body_is_not_present():
    is_custom_event = is_custom_event_request({})

    assert is_custom_event is False
