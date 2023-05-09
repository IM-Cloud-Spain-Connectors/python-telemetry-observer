# Python Telemetry Observer

[![Test](https://github.com/IM-Cloud-Spain-Connectors/python-telemetry-observer/actions/workflows/test.yml/badge.svg)](https://github.com/IM-Cloud-Spain-Connectors/python-telemetry-observer/actions/workflows/test.yml)

This package provides a set of contracts and adapters to provide telemetry observers for different
telemetry drivers.

## Installation

The easiest way to install the Telemetry Observer library is to get the latest version from PyPI:

```bash
# using poetry
poetry add rndi-python-telemetry-observer
# using pip
pip install rndi-python-telemetry-observer
```

## The Contracts

This package provides the following contracts or interfaces:

* Observer

## The Adapters

This package provides the following adapters:

- NoneObserverAdapter: A no-op observer that does nothing, useful when no observer is needed, or to
  be used as a fallback observer.
- DevOpsExtensionAzureInsightsObserverAdapter: An observer that sends telemetry to Azure Insights.

## Default Drivers

| Name     | Description                                                                                                                 |
|----------|-----------------------------------------------------------------------------------------------------------------------------|
| insights | The Insights driver will instrument the application to provide telemetry to the Azure Insights                              |
| none     | This driver will do nothing and is just a way to stop using implementations for telemetry without the need of changing code |

### Observer Adapter

To provide the telemetry observer adapter, we expose the `provide_telemetry_observer` function,
which accepts the following arguments:

| name                      | description                                                       | required | type                                  |
|---------------------------|-------------------------------------------------------------------|----------|:--------------------------------------|
| config                    | The configuration to specify the telemetry driver and other stuff | yes      | dict                                  |
| logger                    | The logger to provide for the adapter                             | yes      | LoggerAdapter                         |
| drivers                   | The drivers to extend the default ones                            | no       | Dict[str, Callable[[dict], Observer]] |
| automatic_instrumentation | The automatic instrumentation to perform                          | no       | List[Callable[[], None]]              |

The `config` argument is a dictionary must have the following keys

| name             | description                          |
|------------------|--------------------------------------|
| TELEMETRY_DRIVER | The driver to use for the Telemetry. |

### Azure Insights Driver

When using the Azure DevOps Insights Driver you have to provide the following config:

| Name                       | Description                                                                                                                                                  | Default  |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| INSIGHTS_CONNECTION_STRING | The Azure Insights Connection string.                                                                                                                        | Required |
| TELEMETRY_SERVICE_NAME     | The service name. Must be the exact name as your extension name in pyproject.toml. This will be the role.name in the Insights System properties for a trace. | Required |

```python
from rndi.telemetry.provider import provide_telemetry_observer
from rndi.telemetry.instrumentors import instrument_requests
config = {
    'TELEMETRY_DRIVER': 'insights',
    'TELEMETRY_SERVICE_NAME':'my-connector',
    'INSIGHTS_CONNECTION_STRING': 'The-instrumentation-key'
} 
instrumentations = [
    instrument_requests,
]
drivers = {}
observer = provide_telemetry_observer(config, logger, drivers, instrumentations)
```

Additional arguments for the observer can be passed, for example we can specify the automatic
instrumentation we want to use, we provide a list of automatic instrumentation options with
OpenTelemetry:

- instrument_requests
- instrument_pgsql

```python
from rndi.telemetry.provider import provide_telemetry_observer


def instrument_my_own_automatic_instrumentation():
    """
    Do some instrumentation here.
    """


config = {
    'TELEMETRY_DRIVER': 'insights'
}
instrumentations = None
drivers = None

observer = provide_telemetry_observer(config, logger, drivers, instrumentations)
```

You can also provide your own custom drivers to extend the options provided out of the box:

```python
from typing import Dict, Any
from rndi.telemetry.provider import provide_telemetry_observer
from rndi.telemetry.contracts import Observer


class MyObserver(Observer):
    def trace(self, name: str, context: Dict[str, Any], high_level: bool = False):
        """
        Create your own trace implementation here.
        """


def provide_my_custom_driver() -> Observer:
    return MyObserver()


config = {
    'TELEMETRY_DRIVER': 'my_custom_driver'
}
drivers = {
    'my_custom_driver': provide_my_custom_driver
}

instrumentations = None

observer = provide_telemetry_observer(config, logger, drivers, instrumentations)
```

## Usage

### Business Transactions

The first trace created will be the business transaction, this trace will be the root of the trace
tree, and will be the one that will be used to group all Technical Transactions.
The observer will be responsible for creating the trace for a business transaction or a technical
transaction.
For example the in the DevOpsExtensionAzureInsightsObserverAdapter if you call the trace method for
the first time, it will create a business transaction trace with a Context, but if you call it a
second time it will just be a Techinical transaction trace.

```python
from typing import Dict, Any

...


def process_asset_purchase(self, request: Dict[str, Any]):
    with self.observer.trace('asset.process.purchase', request):
        """
        Do some stuff here.
        """


...
```

### Technical transactions

Any trace generated inside other trace, will be a Technical Transaction. Just put the trace wherever
you need it.

```python
from typing import Dict, Any

...


def process_asset_purchase(self, request: Dict[str, Any]):
    with self.observer.trace('Process Asset Purchase', request):
        with self.observer.trace('Some transaction', request):
            """
            Do some stuff here.
            """


...
```