#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def instrument_requests():  # pragma: no cover
    RequestsInstrumentor().instrument()


def instrument_pgsql():  # pragma: no cover
    Psycopg2Instrumentor().instrument()
