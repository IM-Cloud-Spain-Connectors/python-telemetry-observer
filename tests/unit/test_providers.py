#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#

from unittest.mock import Mock

from rndi.telemetry.adapters.null import NoneObserver
from rndi.telemetry.contracts import Observer
from rndi.telemetry.provider import provide_telemetry_observer


def test_telemetry_provider_should_provide_a_none_observer_on_no_driver_specified():
    observer = provide_telemetry_observer({
        'package': 'test-package',
    }, Mock())

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserver)


def test_telemetry_provider_should_provide_a_none_observer_on_unsupported_driver():
    observer = provide_telemetry_observer({
        'package': 'test-package',
        'TELEMETRY_DRIVER': 'unsupported',
    }, Mock())

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserver)


def test_telemetry_provider_should_be_extended_with_supported_drivers():
    observer = provide_telemetry_observer({
        'package': 'test-package',
        'TELEMETRY_DRIVER': 'devops',
    }, Mock(), {
        'devops': NoneObserver,
    })

    assert isinstance(observer, Observer)
    assert isinstance(observer, NoneObserver)
