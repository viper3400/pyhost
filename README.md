# PyHost

PyHost is a small FastAPI/ASGI host that discovers installed plugins through
the `tool_host.plugins` Python entry-point group and mounts each plugin app at
its declared URL path. It is independently installable; it does not depend on
FeedVanta or any particular plugin.

## Install and run

Once published, add the host distribution and run it with:

```sh
uv add pyhost
uv run pyhost --host 0.0.0.0 --port 8000
```

The CLI loads `.env` from the current working directory by default. Set a
different file with `--env-file /path/to/host.env`; variables already present
in the process environment take precedence. This setting is for host-level
configuration such as `TOOL_HOST_BASE_PATH`.

The host only sees plugins installed in the same Python environment. In a
workspace checkout, from this directory run:

```sh
uv sync --all-packages
uv run --package pyhost pyhost
```

## Plugin contract

A plugin distribution exports one `Plugin` instance in the entry-point group
`tool_host.plugins`. PyHost loads that object when starting, calls its
`app_factory` once, and mounts the resulting ASGI application at `path`.

```python
from tool_host.plugins import Plugin

PLUGIN = Plugin(
    id="hello",
    name="Hello",
    description="A minimal example plugin",
    version="1.0.0",
    path="/hello",
    app_factory=create_app,
    lifespan=optional_lifespan,
)
```

Contract fields:

- `id`: unique machine-readable ID; also used as the mount name.
- `name`, `description`, `version`: display and release metadata.
- `path`: absolute, non-root URL path with no trailing slash.
- `app_factory`: zero-argument callable returning an ASGI app (normally FastAPI).
- `lifespan`: optional async context-manager factory receiving the created app;
  use it to start and stop plugin resources.

Register the exported object in the plugin distribution's `pyproject.toml`:

```toml
[project.entry-points."tool_host.plugins"]
hello = "hello_plugin.plugin:PLUGIN"
```

The `Plugin` class lives in this `pyhost` distribution. Plugins should depend
on `pyhost` for that contract, but must not import host internals beyond
`tool_host.plugins`.

## Example plugin

See [`examples/hello_plugin`](examples/hello_plugin) for a minimal installable
plugin and its complete entry-point declaration.
