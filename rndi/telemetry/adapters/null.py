#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, List

from opentelemetry.trace import Span
from rndi.telemetry.contracts import Observer


class DummySpan:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def provide_none_telemetry_adapter(_: dict, __: List[Callable[[], None]] = None) -> Observer:
    return NoneObserverAdapter()


class NoneObserverAdapter(Observer):
    @contextmanager
    def trace(self, name: str, context: Dict[str, Any]) -> Iterable[Span]:
        with DummySpan() as span:
            yield span
