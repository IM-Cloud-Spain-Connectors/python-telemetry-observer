#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#

from opentelemetry.sdk import trace
from rndi.telemetry.adapters.azure import generate_trace_id, hydrate_span_with_request_attributes

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
