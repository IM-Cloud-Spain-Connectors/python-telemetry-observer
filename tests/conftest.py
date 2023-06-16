import typing

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


@pytest.fixture
def mocked_span_exporter():
    class MockedSpanExporter(SpanExporter):
        def export(
                self, spans: typing.Sequence[ReadableSpan],
        ) -> SpanExportResult:
            pass

    return MockedSpanExporter()
