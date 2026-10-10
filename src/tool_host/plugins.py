from dataclasses import dataclass
from typing import Any, AsyncContextManager, Callable, Protocol


class PluginLike(Protocol):
    id: str
    name: str
    description: str
    version: str
    path: str
    app_factory: Callable[[], Any]


@dataclass(frozen=True)
class Plugin:
    id: str
    name: str
    description: str
    version: str
    path: str
    app_factory: Callable[[], Any]
    lifespan: Callable[[Any], AsyncContextManager[None]] | None = None


ENTRY_POINT_GROUP = "tool_host.plugins"
