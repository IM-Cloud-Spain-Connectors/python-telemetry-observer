#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#

from unittest.mock import Mock

from rndi.telemetry.adapters.azure import (
    DevOpsExtensionAzureInsightsObserverAdapter,
    provide_azure_insights_observer_telemetry_adapter,
)
from rndi.telemetry.adapters.null import NoneObserverAdapter
from rndi.telemetry.contracts import Observer
from rndi.telemetry.provider import provide_telemetry_observer


def test_telemetry_provider_should_provide_a_none_observer_adapter_on_no_driver_specified():
    observer = provide_telemetry_observer({
        'TELEMETRY_SERVICE_NAME': 'test-package',
    }, Mock())

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserverAdapter)


def test_telemetry_provider_should_provide_a_none_observer_adapter_on_unsupported_driver():
    observer = provide_telemetry_observer({
        'TELEMETRY_SERVICE_NAME': 'test-package',
        'TELEMETRY_DRIVER': 'unsupported',
    }, Mock())

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserverAdapter)


def test_telemetry_provider_should_be_extended_with_supported_drivers():
    observer = provide_telemetry_observer({
        'TELEMETRY_SERVICE_NAME': 'test-package',
        'TELEMETRY_DRIVER': 'devops',
    }, Mock(), {
        'devops': NoneObserverAdapter,
    })

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserverAdapter)


def test_insights_adapter_provider_should_provide_a_insights_adapter_successfully(mocked_span_exporter):
    adapter = provide_azure_insights_observer_telemetry_adapter({
        'TELEMETRY_SERVICE_NAME': 'test-package',
        'TELEMETRY_DRIVER': 'devops',
        'INSIGHTS_CONNECTION_STRING': 'fake-string',
    }, [], mocked_span_exporter)

    assert isinstance(adapter, Observer)
    assert isinstance(adapter, DevOpsExtensionAzureInsightsObserverAdapter)
