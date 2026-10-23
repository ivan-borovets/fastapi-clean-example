from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import best_match
from jsonschema.protocols import Validator

JSON_MEDIA_TYPE: Final[str] = "application/json"
SCHEMA_REF_PREFIX: Final[str] = "#/components/schemas/"


@dataclass(frozen=True, slots=True)
class RequestBodyExample:
    operation: str
    name: str
    value: Any
    schema_fields: set[str]
    schema_validator: Validator

    @property
    def label(self) -> str:
        return f"{self.operation} ({self.name})"

    @property
    def violation(self) -> str | None:
        error = best_match(self.schema_validator.iter_errors(self.value))
        if error is None:
            return None

        return f"{error.json_path} {error.message}"

    @property
    def unknown_fields(self) -> list[str]:
        return sorted(self.value_fields - self.schema_fields)

    @property
    def has_all_schema_fields(self) -> bool:
        return self.schema_fields <= self.value_fields

    @property
    def value_fields(self) -> set[str]:
        if isinstance(self.value, dict):
            return set(self.value)

        return set()


@dataclass(frozen=True, slots=True)
class RequestBodyExamples:
    examples: list[RequestBodyExample]

    @property
    def invalid(self) -> list[str]:
        violating = [example for example in self.examples if example.violation is not None]

        return sorted(f"{example.label}: {example.violation}" for example in violating)

    @property
    def with_unknown_fields(self) -> list[str]:
        with_unknown_fields = [example for example in self.examples if example.unknown_fields]

        return sorted(f"{example.label}: {example.unknown_fields}" for example in with_unknown_fields)

    @property
    def operations_without_complete_example(self) -> list[str]:
        operations = {example.operation for example in self.examples}
        with_complete_example = {example.operation for example in self.examples if example.has_all_schema_fields}

        return sorted(operations - with_complete_example)


def collect_request_body_examples(openapi_document: dict[str, Any]) -> RequestBodyExamples:
    format_checker = make_format_checker()
    collected: list[RequestBodyExample] = []
    for path, operations in openapi_document["paths"].items():
        for method, operation in operations.items():
            content = operation.get("requestBody", {}).get("content", {}).get(JSON_MEDIA_TYPE, {})
            examples = content.get("examples", {})
            schema = content.get("schema")
            if not examples or schema is None:
                continue

            schema_fields = collect_schema_fields(schema, openapi_document)
            schema_validator = Draft202012Validator(
                rooted_body_schema(openapi_document, path, method),
                format_checker=format_checker,
            )
            collected.extend(
                RequestBodyExample(
                    operation=f"{method.upper()} {path}",
                    name=name,
                    value=example["value"],
                    schema_fields=schema_fields,
                    schema_validator=schema_validator,
                )
                for name, example in examples.items()
                if "value" in example
            )

    return RequestBodyExamples(collected)


def make_format_checker() -> FormatChecker:
    checker = FormatChecker()
    checker.checks("date-time")(check_date_time)

    return checker


def check_date_time(value: object) -> bool:
    if not isinstance(value, str):
        return True

    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False

    return True


def collect_schema_fields(body_schema: dict[str, Any], openapi_document: dict[str, Any]) -> set[str]:
    ref = body_schema.get("$ref")
    if ref is None:
        return set(body_schema.get("properties", {}))

    schemas = openapi_document.get("components", {}).get("schemas", {})
    resolved: dict[str, Any] = schemas.get(ref.removeprefix(SCHEMA_REF_PREFIX), {})

    return set(resolved.get("properties", {}))


def rooted_body_schema(openapi_document: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    tokens = ("paths", path, method, "requestBody", "content", JSON_MEDIA_TYPE, "schema")
    pointer = "/".join(token.replace("~", "~0").replace("/", "~1") for token in tokens)  # RFC 6901

    return {**openapi_document, "$ref": f"#/{pointer}"}
