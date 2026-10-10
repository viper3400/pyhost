from fastapi import FastAPI

from tool_host.plugins import Plugin


def create_app() -> FastAPI:
    app = FastAPI(title="Hello plugin")

    @app.get("/")
    async def hello():
        return {"message": "Hello from an independently installed plugin!"}

    return app


PLUGIN = Plugin(
    id="hello",
    name="Hello",
    description="A tiny example showing the PyHost plugin contract",
    version="1.0.0",
    path="/hello",
    app_factory=create_app,
)
