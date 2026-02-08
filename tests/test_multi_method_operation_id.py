import warnings

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_multi_method_unique_operation_ids():
    """Test that routes with multiple methods generate unique operation IDs.

    Regression test for https://github.com/fastapi/fastapi/issues/13175
    """
    app = FastAPI()

    @app.api_route("/multi", methods=["GET", "POST"])
    def multi_method():
        return {"message": "Hello World"}

    client = TestClient(app)

    # Should not emit a duplicate operation ID warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get("/openapi.json")
        assert response.status_code == 200
        duplicate_warnings = [
            x for x in w if "Duplicate Operation ID" in str(x.message)
        ]
        assert duplicate_warnings == [], (
            f"Unexpected duplicate operation ID warnings: {duplicate_warnings}"
        )

    openapi_schema = response.json()
    paths = openapi_schema["paths"]

    # The /multi path should have both GET and POST operations
    assert "get" in paths["/multi"]
    assert "post" in paths["/multi"]

    get_op_id = paths["/multi"]["get"]["operationId"]
    post_op_id = paths["/multi"]["post"]["operationId"]

    # The operation IDs must be different
    assert get_op_id != post_op_id, (
        f"GET and POST should have different operation IDs, "
        f"but both are '{get_op_id}'"
    )

    # Each operation ID should contain the respective method name
    assert "get" in get_op_id.lower()
    assert "post" in post_op_id.lower()


def test_multi_method_with_add_api_route():
    """Test add_api_route with multiple methods also generates unique IDs."""
    app = FastAPI()

    def clear():
        return {"status": "cleared"}

    app.add_api_route("/clear", clear, methods=["POST", "DELETE"])

    client = TestClient(app)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get("/openapi.json")
        assert response.status_code == 200
        duplicate_warnings = [
            x for x in w if "Duplicate Operation ID" in str(x.message)
        ]
        assert duplicate_warnings == [], (
            f"Unexpected duplicate operation ID warnings: {duplicate_warnings}"
        )

    openapi_schema = response.json()
    paths = openapi_schema["paths"]

    assert "post" in paths["/clear"]
    assert "delete" in paths["/clear"]

    post_op_id = paths["/clear"]["post"]["operationId"]
    delete_op_id = paths["/clear"]["delete"]["operationId"]

    assert post_op_id != delete_op_id, (
        f"POST and DELETE should have different operation IDs, "
        f"but both are '{post_op_id}'"
    )

    assert "post" in post_op_id.lower()
    assert "delete" in delete_op_id.lower()


def test_single_method_unchanged():
    """Ensure single-method routes are not affected by the fix."""
    app = FastAPI()

    @app.get("/items")
    def get_items():
        return []

    @app.post("/items")
    def create_item():
        return {}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()
    paths = openapi_schema["paths"]

    get_op_id = paths["/items"]["get"]["operationId"]
    post_op_id = paths["/items"]["post"]["operationId"]

    # Single method routes should still have the method in the operation ID
    assert get_op_id == "get_items_items_get"
    assert post_op_id == "create_item_items_post"


def test_three_methods():
    """Test route with three methods generates three unique operation IDs."""
    app = FastAPI()

    @app.api_route("/resource", methods=["GET", "PUT", "DELETE"])
    def resource():
        return {"ok": True}

    client = TestClient(app)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get("/openapi.json")
        assert response.status_code == 200
        duplicate_warnings = [
            x for x in w if "Duplicate Operation ID" in str(x.message)
        ]
        assert duplicate_warnings == [], (
            f"Unexpected duplicate operation ID warnings: {duplicate_warnings}"
        )

    openapi_schema = response.json()
    paths = openapi_schema["paths"]

    get_op_id = paths["/resource"]["get"]["operationId"]
    put_op_id = paths["/resource"]["put"]["operationId"]
    delete_op_id = paths["/resource"]["delete"]["operationId"]

    # All three must be distinct
    op_ids = {get_op_id, put_op_id, delete_op_id}
    assert len(op_ids) == 3, f"Expected 3 unique operation IDs, got {op_ids}"

    assert "get" in get_op_id.lower()
    assert "put" in put_op_id.lower()
    assert "delete" in delete_op_id.lower()
