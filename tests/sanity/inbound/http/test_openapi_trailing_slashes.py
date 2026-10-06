from typing import Any


def test_all_public_routes_have_trailing_slash(openapi_document: dict[str, Any]) -> None:
    paths = openapi_document["paths"]

    without_trailing_slash = sorted(path for path in paths if not path.endswith("/"))

    assert without_trailing_slash == []
