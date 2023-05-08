#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from abc import ABC, abstractmethod
from typing import Any, Dict


class Observer(ABC):  # pragma: no cover
    """
    Observer contract, this will provide the interface to trace, do metrics and logs.
    """
    @abstractmethod
    def trace(self, name: str, context: Dict[str, Any], high_level: bool = False):
        """
        Trace a transaction.
        :param high_level: Used for the high level trace, which is the trace generated
         when a request is received
        :param name: The name of the span we will create
        :param context: The context for the trace, usually a raw request.
        :return: None
        """
