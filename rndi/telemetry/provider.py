#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from logging import LoggerAdapter
from typing import Callable, Dict, List, Optional

from rndi.telemetry.adapters.azure import provide_azure_insights_observer_telemetry_adapter
from rndi.telemetry.adapters.null import provide_none_telemetry_adapter
from rndi.telemetry.contracts import Observer


def provide_telemetry_observer(
        config: dict,
        logger: LoggerAdapter,
        drivers: Optional[Dict[str, Callable[[dict], Observer]]] = None,
        automatic_instrumentation: Optional[List[Callable[[], None]]] = None,
):
    supported: Dict[str, Callable[[dict], Observer]] = {
        'insights': provide_azure_insights_observer_telemetry_adapter,
        'none': provide_none_telemetry_adapter,
    }

    if isinstance(drivers, dict):
        supported.update(drivers)

    driver = config.get('TELEMETRY_DRIVER', 'none')
    provider = supported.get(driver, automatic_instrumentation)

    if provider is None:
        def _unsupported_driver(_: dict) -> Observer:
            raise ValueError(f"Unsupported cache driver {driver}")

        provider = _unsupported_driver

    try:
        adapter = provider(config)
        logger.debug(f"Telemetry Observer configured with {driver} driver.")
    except Exception as e:
        adapter = provide_none_telemetry_adapter(config)
        logger.error(
            f"Telemetry Observer failure, disabling observability with driver {driver} due to: {e}",
        )

    return adapter
