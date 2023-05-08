#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from typing import Any, Dict

from rndi.telemetry.contracts import Observer


def provide_none_telemetry_adapter(_: dict) -> Observer:
    return NoneObserver()


class NoneObserver(Observer):
    def trace(self, name: str, context: Dict[str, Any], high_level: bool = False):
        return None
