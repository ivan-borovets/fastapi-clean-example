from typing import Any

from tests.sanity.inbound.http.request_body_examples import collect_request_body_examples


def test_every_request_body_example_is_valid_against_its_schema(openapi_document: dict[str, Any]) -> None:
    examples = collect_request_body_examples(openapi_document)

    assert examples.invalid == []


def test_every_request_body_example_uses_only_schema_fields(openapi_document: dict[str, Any]) -> None:
    examples = collect_request_body_examples(openapi_document)

    assert examples.with_unknown_fields == []


def test_every_request_body_has_an_example_with_all_schema_fields(openapi_document: dict[str, Any]) -> None:
    examples = collect_request_body_examples(openapi_document)

    assert examples.operations_without_complete_example == []
