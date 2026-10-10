# Agent guidance

## Project overview

PyHost is a FastAPI host that discovers independently packaged ASGI plugins
through the `tool_host.plugins` Python entry-point group and mounts each plugin
at its declared URL path. The shared plugin contract is defined in
`src/tool_host/plugins.py`.

## Plugin system

- A plugin distribution exports a `Plugin` instance from the
  `tool_host.plugins` entry-point group in its `pyproject.toml`.
- A `Plugin` provides a unique, non-empty `id`, display metadata, an absolute
  non-root `path` without a trailing slash, and a zero-argument `app_factory`.
- Optional plugin resources should be managed with the plugin's async
  `lifespan` factory.
- The host discovers entry points in the active Python environment. For local
  workspace development, install all workspace packages with
  `uv sync --all-packages`.
- Use `examples/hello_plugin` as the reference implementation. Keep plugin
  code independent of host internals; plugins should depend on the public
  `tool_host.plugins` contract.
- Add or update tests in `tests/` when changing plugin discovery, validation,
  mounting, or host behavior.

## Development and tests

- Run the host with `uv run --package pyhost pyhost`.
- Run tests with `uv run pytest` (install the test extra if needed).
- Respect the Python version specified by `.python-version` and
  `pyproject.toml`.
- Do not commit `.env` files or secrets. Configuration is supplied through
  process environment variables unless a launcher explicitly loads an env
  file.

## Commits

Use Conventional Commits for commit messages, in the form
`<type>(optional-scope): <imperative summary>`, for example:

- `feat: add plugin health endpoint`
- `fix(host): handle forwarded URL prefixes`
- `test: cover plugin path validation`
- `docs: explain plugin entry points`
- `chore: update development tooling`

Use a concise, lowercase summary and choose a type that reflects the change
(commonly `feat`, `fix`, `docs`, `test`, `refactor`, or `chore`).
