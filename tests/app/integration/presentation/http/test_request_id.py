import uuid

from fastapi.testclient import TestClient


def test_request_id_header_always_present(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    uuid.UUID(request_id)


def test_request_id_preserved(client: TestClient) -> None:
    request_id = "test-request-id"
    response = client.get("/api/v1/health", headers={"X-Request-Id": request_id})
    assert response.headers.get("x-request-id") == request_id
