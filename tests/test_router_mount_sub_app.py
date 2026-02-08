"""
Test mounting sub-applications under APIRouter.

This tests the fix for issue #10180.
"""

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient


def test_mount_sub_app_on_router_with_prefix():
    """Test that mounting a sub-app on an APIRouter with a prefix works."""
    app = FastAPI()
    api_router = APIRouter(prefix="/api")

    @api_router.get("/app")
    def read_main():
        return {"message": "Hello from main app"}

    # Create sub-application
    subapi = FastAPI()

    @subapi.get("/sub")
    def read_sub():
        return {"message": "Hello from sub API"}

    # Mount sub-application under the router (BEFORE including the router)
    api_router.mount("/subapi", subapi)

    # Include router in app
    app.include_router(api_router)

    client = TestClient(app)

    # Test regular router endpoint
    response = client.get("/api/app")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from main app"}

    # Test mounted sub-application endpoint
    response = client.get("/api/subapi/sub")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from sub API"}


def test_mount_sub_app_on_router_without_prefix():
    """Test that mounting a sub-app on an APIRouter without a prefix works."""
    app = FastAPI()
    api_router = APIRouter()

    @api_router.get("/app")
    def read_main():
        return {"message": "Hello from main app"}

    # Create sub-application
    subapi = FastAPI()

    @subapi.get("/sub")
    def read_sub():
        return {"message": "Hello from sub API"}

    # Mount sub-application under the router
    api_router.mount("/subapi", subapi)

    # Include router in app
    app.include_router(api_router)

    client = TestClient(app)

    # Test regular router endpoint
    response = client.get("/app")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from main app"}

    # Test mounted sub-application endpoint
    response = client.get("/subapi/sub")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from sub API"}


def test_mount_sub_app_on_router_with_additional_prefix():
    """Test that mounting a sub-app on an APIRouter with additional prefix on include_router."""
    app = FastAPI()
    api_router = APIRouter(prefix="/v1")

    @api_router.get("/app")
    def read_main():
        return {"message": "Hello from main app"}

    # Create sub-application
    subapi = FastAPI()

    @subapi.get("/sub")
    def read_sub():
        return {"message": "Hello from sub API"}

    # Mount sub-application under the router
    api_router.mount("/subapi", subapi)

    # Include router in app with additional prefix
    app.include_router(api_router, prefix="/api")

    client = TestClient(app)

    # Test regular router endpoint
    response = client.get("/api/v1/app")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from main app"}

    # Test mounted sub-application endpoint
    response = client.get("/api/v1/subapi/sub")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from sub API"}


def test_mount_static_files_on_router():
    """Test that mounting StaticFiles on an APIRouter works."""
    from starlette.staticfiles import StaticFiles
    import tempfile
    import os

    app = FastAPI()
    api_router = APIRouter(prefix="/api")

    @api_router.get("/app")
    def read_main():
        return {"message": "Hello from main app"}

    # Create a temporary directory with a test file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Mount static files under the router
        api_router.mount("/static", StaticFiles(directory=tmpdir), name="static")

        # Include router in app
        app.include_router(api_router)

        client = TestClient(app)

        # Test regular router endpoint
        response = client.get("/api/app")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from main app"}

        # Test mounted static files
        response = client.get("/api/static/test.txt")
        assert response.status_code == 200
        assert response.text == "test content"


def test_nested_routers_with_mounted_sub_app():
    """Test that mounting a sub-app works with nested routers."""
    app = FastAPI()
    top_router = APIRouter(prefix="/top")
    nested_router = APIRouter(prefix="/nested")

    @nested_router.get("/app")
    def read_main():
        return {"message": "Hello from nested router"}

    # Create sub-application
    subapi = FastAPI()

    @subapi.get("/sub")
    def read_sub():
        return {"message": "Hello from sub API"}

    # Mount sub-application under the nested router
    nested_router.mount("/subapi", subapi)

    # Include nested router in top router
    top_router.include_router(nested_router)

    # Include top router in app
    app.include_router(top_router)

    client = TestClient(app)

    # Test regular nested router endpoint
    response = client.get("/top/nested/app")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from nested router"}

    # Test mounted sub-application endpoint
    response = client.get("/top/nested/subapi/sub")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from sub API"}
