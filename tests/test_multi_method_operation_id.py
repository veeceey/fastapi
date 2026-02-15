from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_multi_method_unique_operation_ids():
    """Routes registered with multiple methods should get distinct operationIds."""
    app = FastAPI()

    @app.api_route("/items", methods=["GET", "POST"])
    def items():
        return {"message": "items"}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    path_ops = schema["paths"]["/items"]
    get_op_id = path_ops["get"]["operationId"]
    post_op_id = path_ops["post"]["operationId"]

    assert get_op_id != post_op_id, (
        f"GET and POST should have different operationIds, both got '{get_op_id}'"
    )
    assert get_op_id == "items_items_get"
    assert post_op_id == "items_items_post"


def test_multi_method_three_methods():
    """Verify operationId uniqueness with three methods on one route."""
    app = FastAPI()

    @app.api_route("/resource", methods=["GET", "PUT", "DELETE"])
    def resource():
        return {}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    path_ops = schema["paths"]["/resource"]
    op_ids = {method: path_ops[method]["operationId"] for method in path_ops}

    # All operation IDs should be unique
    assert len(set(op_ids.values())) == len(op_ids), (
        f"Expected unique operationIds, got: {op_ids}"
    )
    assert op_ids["get"] == "resource_resource_get"
    assert op_ids["put"] == "resource_resource_put"
    assert op_ids["delete"] == "resource_resource_delete"


def test_single_method_unchanged():
    """Single-method routes should keep existing operationId format."""
    app = FastAPI()

    @app.get("/single")
    def single():
        return {}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    op_id = schema["paths"]["/single"]["get"]["operationId"]
    assert op_id == "single_single_get"


def test_add_api_route_multi_method():
    """add_api_route with multiple methods should also produce unique operationIds."""
    app = FastAPI()

    def handler():
        return {"ok": True}

    app.add_api_route("/endpoint", handler, methods=["POST", "DELETE"])

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    path_ops = schema["paths"]["/endpoint"]
    post_op_id = path_ops["post"]["operationId"]
    delete_op_id = path_ops["delete"]["operationId"]

    assert post_op_id != delete_op_id
    assert post_op_id == "handler_endpoint_post"
    assert delete_op_id == "handler_endpoint_delete"
