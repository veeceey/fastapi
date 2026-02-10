import json

import pytest
from fastapi import Depends, FastAPI, Header, WebSocket, WebSocketDisconnect, status
from fastapi.testclient import TestClient


def make_app():
    app = FastAPI()

    async def dependency_with_validation(x_required_header: str = Header()):
        pass  # pragma: no cover

    @app.websocket("/ws")
    async def websocket_endpoint(
        websocket: WebSocket, _: None = Depends(dependency_with_validation)
    ):
        pass  # pragma: no cover

    return app


def test_websocket_validation_close_reason_is_valid_json():
    """
    The default WebSocket validation exception handler should send the close
    reason as a valid JSON string so that clients can parse it, not as a Python
    repr of a list (which uses single quotes and Python-specific literals like
    None/True/False instead of null/true/false).
    """
    app = make_app()
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws"):
            pass  # pragma: no cover
    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
    reason = exc_info.value.reason
    # The reason must be a valid JSON string that can be parsed
    errors = json.loads(reason)
    assert isinstance(errors, list)
    assert len(errors) > 0
    # Each error should have the standard validation error fields
    assert "loc" in errors[0]
    assert "msg" in errors[0]
    assert "type" in errors[0]
