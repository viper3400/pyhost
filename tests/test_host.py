from fastapi import FastAPI
from fastapi.testclient import TestClient

from tool_host.app import create_app
from tool_host.plugins import Plugin


def test_mounts_plugin_app():
    app = FastAPI()
    app.get("/")(lambda: {"plugin": "sample"})
    plugin = Plugin(
        id="sample",
        name="Sample",
        description="A sample plugin",
        version="1.0.0",
        path="/sample",
        app_factory=lambda: app,
    )

    with TestClient(create_app([plugin])) as client:
        assert client.get("/health").json() == {"status": "ok", "plugins": ["sample"]}
        assert client.get("/sample/").json() == {"plugin": "sample"}
