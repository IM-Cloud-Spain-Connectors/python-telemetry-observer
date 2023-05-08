# Python Telemetry Observer

[![Test](https://github.com/IM-Cloud-Spain-Connectors/python-telemetry-observer/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/python-connect-api-facades/actions/workflows/test.yml)

This package provides a set of contracts and adapters to provide telemetry observers for
different telemetry drivers.


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
    - NoneObserver: A no-op observer that does nothing, useful when no observer is needed, 
or to be used as a fallback observer.
    - DevOpsExtensionAzureInsightsObserver: An observer that sends telemetry to Azure Insights.

### Azure Insights Observer

The simpler way to provide the observer for Azure Insights is to use the 
`provide_telemetry_observer` function:
```python
from rndi.telemetry.provider import provide_telemetry_observer

observer = provide_telemetry_observer({
    'TELEMETRY_DRIVER': 'insights'
}, logger)
```
Additional arguments for the observer can be passed, for example we can specify the automatic
instrumentation we want to use, we provide a list of automatic instrumentation options with
OpenTelemetry:
- instrument_requests
- instrument_pgsql

```python
from rndi.telemetry.provider import provide_telemetry_observer
from rndi.telemetry.instrumentors import instrument_requests, instrument_pgsql

def instrument_my_own_automatic_instrumentation():
    """
    Do some instrumentation here.
    """

instrumentations = [
    instrument_requests,
    instrument_pgsql,
    instrument_my_own_automatic_instrumentation
]

observer = provide_telemetry_observer({
    'TELEMETRY_DRIVER': 'insights'
    }, 
    logger,
    automatic_instrumentation=instrumentations
)
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

observer = provide_telemetry_observer({
    'TELEMETRY_DRIVER': 'insights'
    }, 
    logger,
    {
        'my_custom_driver': provide_my_custom_driver
    }
)
```

## Usage

### High Level Operations
The Observer contract's `trace` method can receive the argument `high_level` to indicate
if this trace should be considered a high level operation.
This means this operation will use the `id` property given in the context (usually a request id)
and will compute the trace_id in base of this ID, so we achieve correlation between calls to the 
same request in different timelines.
```python
from typing import Dict, Any
...
def process_asset_purchase(self, request: Dict[str, Any]):
    with self.observer.trace('asset.process.purchase', request, True):
        """
        Do some stuff here.
        """
...
```

### Normal transactions
If no `high_level` argument is provided, the trace will be considered a normal transaction,
and it will just use the context of the current execution, allowing the trace to be correlated
with the High level operation that must have been created before.
If no high level operation was created in the start of the execution, this trace will be not correlated.

```python
from typing import Dict, Any
...
def process_asset_purchase(self, request: Dict[str, Any]):
    with self.observer.trace('Process Asset Purchase', request, True):
         with self.observer.trace('Some transaction', request):
            """
            Do some stuff here.
            """
...