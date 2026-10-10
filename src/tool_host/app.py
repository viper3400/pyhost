import os
import re
from html import escape
from contextlib import AsyncExitStack, asynccontextmanager
from importlib.metadata import entry_points
from typing import Iterable

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse, Response
from .plugins import ENTRY_POINT_GROUP, Plugin


def discover_plugins() -> list[Plugin]:
    discovered: list[Plugin] = []
    for point in entry_points(group=ENTRY_POINT_GROUP):
        plugin = point.load()
        if not isinstance(plugin, Plugin):
            raise TypeError(f"Plugin entry point {point.name!r} must expose a Plugin instance")
        discovered.append(plugin)
    return discovered


def create_app(plugins: Iterable[Plugin] | None = None) -> FastAPI:
    loaded_plugins = list(discover_plugins() if plugins is None else plugins)
    ids: set[str] = set()
    paths: set[str] = set()
    for plugin in loaded_plugins:
        if not plugin.id or plugin.id in ids:
            raise ValueError(f"Duplicate or empty plugin id: {plugin.id!r}")
        if not plugin.path.startswith("/") or plugin.path == "/" or plugin.path.endswith("/"):
            raise ValueError(f"Plugin {plugin.id!r} path must be an absolute non-root path without trailing slash")
        if plugin.path in paths:
            raise ValueError(f"Duplicate plugin mount path: {plugin.path!r}")
        ids.add(plugin.id)
        paths.add(plugin.path)

    apps = [(plugin, plugin.app_factory()) for plugin in loaded_plugins]

    configured_prefix = os.getenv("TOOL_HOST_BASE_PATH", "").strip().rstrip("/")
    if configured_prefix and (
        not re.fullmatch(r"/(?:[A-Za-z0-9._~-]+/)*[A-Za-z0-9._~-]*", configured_prefix)
        or ".." in configured_prefix.split("/")
        or "//" in configured_prefix
    ):
        raise ValueError("TOOL_HOST_BASE_PATH must be a URL path prefix, e.g. '/suburl'")

    @asynccontextmanager
    async def lifespan(host: FastAPI):
        async with AsyncExitStack() as stack:
            for plugin, plugin_app in apps:
                if plugin.lifespan:
                    await stack.enter_async_context(plugin.lifespan(plugin_app))
            yield

    host = FastAPI(title="Tool Host", lifespan=lifespan)

    @host.get("/static/app.css", name="host_stylesheet")
    def host_stylesheet():
        return Response(
            "body{margin:0;background:#f1f5f9;color:#0f172a;font:16px system-ui,sans-serif}"
            "main{max-width:56rem;margin:auto;padding:3rem 1.5rem}"
            "header{background:white;border-radius:1.5rem;padding:2rem;margin-bottom:2rem}"
            ".cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1rem}"
            ".card{display:flex;gap:1rem;align-items:center;padding:1.25rem;border:1px solid #cbd5e1;"
            "border-radius:1rem;background:white;color:inherit;text-decoration:none}"
            ".card:hover{border-color:#6366f1;box-shadow:0 8px 24px #c7d2fe}"
            ".icon{display:grid;place-items:center;width:3rem;height:3rem;border-radius:.75rem;"
            "background:#eef2ff;color:#4338ca;font-weight:700}"
            ".description{color:#64748b;font-size:.9rem;margin-top:.25rem}"
            ".empty{padding:3rem;text-align:center;border:1px dashed #94a3b8;border-radius:1rem;color:#64748b}"
            ,
            media_type="text/css",
        )

    @host.middleware("http")
    async def forwarded_prefix(request: Request, call_next):
        prefix = request.headers.get("x-forwarded-prefix", "").strip() or configured_prefix
        if prefix and re.fullmatch(r"/(?:[A-Za-z0-9._~-]+/)*[A-Za-z0-9._~-]*", prefix):
            segments = prefix.split("/")
            if ".." not in segments and "//" not in prefix:
                prefix = prefix.rstrip("/")
                request.scope["root_path"] = prefix
                path = request.scope["path"]
                if path != prefix and not path.startswith(prefix + "/"):
                    request.scope["path"] = prefix + path
                    request.scope["raw_path"] = prefix.encode() + request.scope.get("raw_path", path.encode())
        return await call_next(request)

    @host.get("/", response_class=HTMLResponse, name="home")
    def home(request: Request):
        root_path = escape(request.scope.get("root_path", ""), quote=True)
        plugin_cards = "".join(
            f'<a class="card" href="{root_path}{escape(plugin.path, quote=True)}/">'
            f'<span class="icon">{escape(plugin.name[:1].upper())}</span>'
            f'<span><strong>{escape(plugin.name)}</strong>'
            f'<span class="description">{escape(plugin.description)}</span></span>'
            '<span aria-hidden="true">→</span></a>'
            for plugin in loaded_plugins
        )
        empty_state = (
            '<div class="empty">'
            'No tools are available yet.</div>'
        )
        stylesheet_url = f'{root_path}/static/app.css'
        return (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Tools</title>'
            f'<link rel="stylesheet" href="{stylesheet_url}"></head>'
            '<body><main>'
            '<header><small>Workspace</small>'
            '<h1>Your tools, in one place.</h1>'
            '<p>Choose a tool to get started. Each workspace is ready when you are.</p>'
            '</header><section class="cards" aria-label="Available tools">'
            f'{plugin_cards or empty_state}'
            '</section></main></body></html>'
        )
    host.get("/health", name="health")(
        lambda: {"status": "ok", "plugins": [plugin.id for plugin in loaded_plugins]}
    )
    for plugin, plugin_app in apps:
        host.mount(plugin.path, plugin_app, name=plugin.id)
    return host
