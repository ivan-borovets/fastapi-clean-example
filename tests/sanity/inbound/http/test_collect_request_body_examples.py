"""Guards the collector itself: broken collection would leave the OpenAPI invariants green on an empty list."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Final
from uuid import UUID

import pytest
from fastapi import Body, FastAPI
from pydantic import BaseModel

from tests.sanity.inbound.http.request_body_examples import collect_request_body_examples

ENDPOINT_PATH: Final[str] = "/endpoint/"
ENDPOINT_OPERATION: Final[str] = f"POST {ENDPOINT_PATH}"
ENDPOINT_IDENTIFIER: Final[str] = str(UUID(int=0))
ENDPOINT_CREATED_AT: Final[str] = "2026-01-01T00:00:00Z"
ENDPOINT_NAME: Final[str] = "endpoint_name"
ENDPOINT_COUNT: Final[int] = 1
EXAMPLE_NAME: Final[str] = "minimal"
EXAMPLE_SUMMARY: Final[str] = "Minimal request"
EXAMPLE_LABEL: Final[str] = f"{ENDPOINT_OPERATION} ({EXAMPLE_NAME})"
EXAMPLE_EXTERNAL_VALUE: Final[str] = "https://example.test/request-body.json"


class EndpointRequestSchema(BaseModel):
    identifier: UUID
    created_at: datetime
    name: str
    count: int


class EndpointKind(StrEnum):
    FIRST = "first"


def make_document_with_example(example_value: Any) -> dict[str, Any]:
    app = FastAPI()

    @app.post(ENDPOINT_PATH)
    async def endpoint(
        request_schema: Annotated[
            EndpointRequestSchema,
            Body(openapi_examples=make_openapi_examples(example_value)),
        ],
    ) -> EndpointRequestSchema:
        return request_schema

    return app.openapi()


def make_document_with_nullable_body(example_value: Any) -> dict[str, Any]:
    app = FastAPI()

    @app.post(ENDPOINT_PATH)
    async def endpoint(
        request_schema: Annotated[
            EndpointRequestSchema | None,
            Body(openapi_examples=make_openapi_examples(example_value)),
        ],
    ) -> EndpointRequestSchema | None:
        return request_schema

    return app.openapi()


def make_document_with_enum_body(example_value: Any) -> dict[str, Any]:
    app = FastAPI()

    @app.post(ENDPOINT_PATH)
    async def endpoint(
        kind: Annotated[
            EndpointKind,
            Body(openapi_examples=make_openapi_examples(example_value)),
        ],
    ) -> EndpointKind:
        return kind

    return app.openapi()


def make_document_with_external_example() -> dict[str, Any]:
    app = FastAPI()

    @app.post(ENDPOINT_PATH)
    async def endpoint(
        request_schema: Annotated[
            EndpointRequestSchema,
            Body(openapi_examples={EXAMPLE_NAME: {"externalValue": EXAMPLE_EXTERNAL_VALUE}}),
        ],
    ) -> EndpointRequestSchema:
        return request_schema

    return app.openapi()


def make_openapi_examples(example_value: Any) -> dict[str, Any]:
    return {
        EXAMPLE_NAME: {
            "summary": EXAMPLE_SUMMARY,
            "value": example_value,
        },
    }


def test_collects_example_declared_with_body_openapi_examples() -> None:
    document = make_document_with_example(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
            "count": ENDPOINT_COUNT,
        },
    )

    examples = collect_request_body_examples(document)

    assert [example.label for example in examples.examples] == [EXAMPLE_LABEL]


def test_reports_example_with_wrong_field_type() -> None:
    document = make_document_with_example(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
            "count": "not_a_number",
        },
    )

    examples = collect_request_body_examples(document)

    violations = examples.invalid
    assert len(violations) == 1
    assert violations[0].startswith(EXAMPLE_LABEL)


def test_reports_example_with_malformed_uuid() -> None:
    document = make_document_with_example(
        {
            "identifier": "not_a_uuid",
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
            "count": ENDPOINT_COUNT,
        },
    )

    examples = collect_request_body_examples(document)

    violations = examples.invalid
    assert len(violations) == 1
    assert violations[0].startswith(EXAMPLE_LABEL)


def test_reports_example_with_malformed_date_time() -> None:
    document = make_document_with_example(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": "not_a_date_time",
            "name": ENDPOINT_NAME,
            "count": ENDPOINT_COUNT,
        },
    )

    examples = collect_request_body_examples(document)

    violations = examples.invalid
    assert len(violations) == 1
    assert violations[0].startswith(EXAMPLE_LABEL)


def test_reports_example_with_field_outside_schema() -> None:
    document = make_document_with_example(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
            "count": ENDPOINT_COUNT,
            "extra": True,
        },
    )

    examples = collect_request_body_examples(document)

    assert examples.with_unknown_fields == [f"{EXAMPLE_LABEL}: ['extra']"]


def test_reports_operation_without_complete_example() -> None:
    document = make_document_with_example(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
        },
    )

    examples = collect_request_body_examples(document)

    assert examples.operations_without_complete_example == [ENDPOINT_OPERATION]


def test_reports_example_with_wrong_field_type_in_nullable_body() -> None:
    document = make_document_with_nullable_body(
        {
            "identifier": ENDPOINT_IDENTIFIER,
            "created_at": ENDPOINT_CREATED_AT,
            "name": ENDPOINT_NAME,
            "count": "not_a_number",
        },
    )

    examples = collect_request_body_examples(document)

    violations = examples.invalid
    assert len(violations) == 1
    assert violations[0].startswith(EXAMPLE_LABEL)


def test_reports_enum_body_example_outside_declared_values() -> None:
    document = make_document_with_enum_body("second")

    examples = collect_request_body_examples(document)

    violations = examples.invalid
    assert len(violations) == 1
    assert violations[0].startswith(EXAMPLE_LABEL)


def test_reports_no_unknown_fields_for_enum_body_example() -> None:
    document = make_document_with_enum_body(EndpointKind.FIRST)

    examples = collect_request_body_examples(document)

    assert examples.with_unknown_fields == []


def test_skips_example_given_by_external_value() -> None:
    document = make_document_with_external_example()

    examples = collect_request_body_examples(document)

    assert examples.examples == []


def test_raises_when_document_has_no_paths() -> None:
    with pytest.raises(KeyError):
        collect_request_body_examples({})
