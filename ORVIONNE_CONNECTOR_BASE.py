from abc import ABC, abstractmethod
from typing import Any

from app.connectors.models import (
    ConnectorHealth,
    ConnectorMetadata,
    ConnectorPermissions,
    ConnectorResourceRef,
    ConnectorResult,
    DiscoveryResult,
    SearchResult,
    SyncRequest,
    SyncResult,
)


class Connector(ABC):
    """Base contract every ORVIONNE integration must implement."""

    connector_type: str

    @abstractmethod
    def authenticate(self, config: dict[str, Any]) -> ConnectorResult:
        """Validate credentials, tokens, or local access material."""

    @abstractmethod
    def test_connection(self, config: dict[str, Any]) -> ConnectorResult:
        """Verify the source is reachable without mutating external state."""

    @abstractmethod
    def discover(self, config: dict[str, Any]) -> DiscoveryResult:
        """Return source metadata such as schema, folders, or capabilities."""

    @abstractmethod
    def sync(self, config: dict[str, Any], request: SyncRequest | None = None) -> SyncResult:
        """Synchronize source metadata or content according to connector policy."""

    def incremental_sync(
        self, config: dict[str, Any], request: SyncRequest | None = None
    ) -> SyncResult:
        return self.sync(config, request)

    @abstractmethod
    def search(self, config: dict[str, Any], query: str, limit: int) -> SearchResult:
        """Search connector-managed data within the caller's workspace."""

    @abstractmethod
    def permissions(self, config: dict[str, Any]) -> ConnectorPermissions:
        """Return the connector's effective permission envelope."""

    @abstractmethod
    def health(self, config: dict[str, Any]) -> ConnectorHealth:
        """Return the current health state."""

    @abstractmethod
    def disconnect(self, config: dict[str, Any]) -> ConnectorResult:
        """Cleanly disconnect connector-managed state."""

    @abstractmethod
    def metadata(self) -> ConnectorMetadata:
        """Return static connector catalog metadata."""

    def refresh_credentials(self, config: dict[str, Any]) -> ConnectorResult:
        """Refresh short-lived credentials. No-op by default."""
        return ConnectorResult(ok=True, message="No credential refresh required.")

    def revoke_credentials(self, config: dict[str, Any]) -> ConnectorResult:
        """Revoke stored credentials at the provider. Defaults to disconnect()."""
        return self.disconnect(config)

    def get_sync_cursor(self, config: dict[str, Any]) -> str | None:
        return config.get("sync_cursor")

    def set_sync_cursor(self, config: dict[str, Any], cursor: str | None) -> None:
        return None

    def select_resources(
        self, config: dict[str, Any], resource_ids: list[str]
    ) -> ConnectorResult:
        config["selected_resource_ids"] = resource_ids
        return ConnectorResult(ok=True, message="Resources selected.")

    def list_resources(
        self, config: dict[str, Any], cursor: str | None = None
    ) -> list[ConnectorResourceRef]:
        raise NotImplementedError(f"{self.connector_type} does not support list_resources().")

    def fetch_resource(self, config: dict[str, Any], provider_resource_id: str) -> bytes:
        raise NotImplementedError(f"{self.connector_type} does not support fetch_resource().")

    def normalize_resource(self, raw: dict[str, Any]) -> ConnectorResourceRef:
        raise NotImplementedError(f"{self.connector_type} does not support normalize_resource().")

    def validate_scope(self, config: dict[str, Any], required_scopes: tuple[str, ...]) -> bool:
        return True
