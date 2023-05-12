#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from contextlib import contextmanager
from typing import Any, Dict, Iterable

from opentelemetry.trace import Span
from rndi.telemetry.contracts import Observer


class DummySpan:  # pragma: no cover
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def provide_none_telemetry_adapter(_: dict) -> Observer:  # pragma: no cover
    return NoneObserverAdapter()


class NoneObserverAdapter(Observer):  # pragma: no cover
    @contextmanager
    def trace(self, name: str, context: Dict[str, Any]) -> Iterable[Span]:
        with DummySpan() as span:
            yield span
