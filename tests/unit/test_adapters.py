#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#

from opentelemetry.context import Context
from rndi.telemetry.adapters.azure import generate_trace_id, get_context
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
