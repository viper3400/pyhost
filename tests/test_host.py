from types import SimpleNamespace

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


def test_mounts_structural_plugin_without_host_plugin_class():
    app = FastAPI()
    app.get("/")(lambda: {"plugin": "structural"})
    plugin = SimpleNamespace(
        id="structural",
        name="Structural",
        description="A plugin without a PyHost dependency",
        version="1.0.0",
        path="/structural",
        app_factory=lambda: app,
    )

    with TestClient(create_app([plugin])) as client:
        assert client.get("/health").json() == {"status": "ok", "plugins": ["structural"]}
        assert client.get("/structural/").json() == {"plugin": "structural"}


def test_rejects_entry_without_required_plugin_fields():
    try:
        create_app([object()])
    except TypeError as exc:
        assert "missing required attributes" in str(exc)
    else:
        raise AssertionError("Invalid plugin was accepted")
