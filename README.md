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

A plugin distribution exports an object in the entry-point group
`tool_host.plugins`. The object must provide the fields below. PyHost validates
those fields when loading the entry point, calls `app_factory` once, and mounts
the resulting ASGI application at `path`. Plugins do not need to depend on
PyHost or import its classes.

```python
from types import SimpleNamespace

PLUGIN = SimpleNamespace(
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

The `Plugin` dataclass remains available for convenience to plugins that choose
to depend on PyHost, but it is not required by the contract.

## Example plugin

See [`examples/hello_plugin`](examples/hello_plugin) for a minimal installable
plugin and its complete entry-point declaration.
