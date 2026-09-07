from collections.abc import Callable
from importlib import import_module
from pkgutil import iter_modules

import app.connectors.utils as connector_utils
from app.connectors.base import Connector

ConnectorFactory = Callable[[], Connector]


class ConnectorRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, ConnectorFactory] = {}

    def register(self, connector_type: str, factory: ConnectorFactory) -> None:
        if connector_type in self._factories:
            raise ValueError(f"Connector type already registered: {connector_type}")
        self._factories[connector_type] = factory

    def decorator(self, connector_type: str) -> Callable[[type[Connector]], type[Connector]]:
        def _register(connector_class: type[Connector]) -> type[Connector]:
            self.register(connector_type, connector_class)
            return connector_class

        return _register

    def get(self, connector_type: str) -> Connector:
        ensure_builtin_connectors_loaded()
        try:
            return self._factories[connector_type]()
        except KeyError as exc:
            raise ValueError(f"Unsupported connector type: {connector_type}") from exc

    def registered_types(self) -> tuple[str, ...]:
        ensure_builtin_connectors_loaded()
        return tuple(sorted(self._factories))

    def metadata(self) -> dict[str, str]:
        ensure_builtin_connectors_loaded()
        return {
            connector_type: factory().metadata().display_name
            for connector_type, factory in sorted(self._factories.items())
        }


connector_registry = ConnectorRegistry()
_builtins_loaded = False


def register_connector(connector_type: str) -> Callable[[type[Connector]], type[Connector]]:
    return connector_registry.decorator(connector_type)


def ensure_builtin_connectors_loaded() -> None:
    global _builtins_loaded
    if _builtins_loaded:
        return

    _builtins_loaded = True
    for module in iter_modules(connector_utils.__path__):
        if not module.ispkg:
            import_module(f"{connector_utils.__name__}.{module.name}")
