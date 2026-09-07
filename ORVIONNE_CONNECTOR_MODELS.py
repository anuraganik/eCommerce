from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ConnectorType(StrEnum):
    postgres = "postgres"
    mysql = "mysql"
    sqlserver = "sqlserver"
    googledrive = "googledrive"
    onedrive = "onedrive"
    sharepoint = "sharepoint"
    slack = "slack"
    github = "github"
    jira = "jira"
    confluence = "confluence"
    gmail = "gmail"
    outlook = "outlook"
    dropbox = "dropbox"
    localagent = "localagent"
    document_storage = "document_storage"


class ConnectorHealth(StrEnum):
    healthy = "Healthy"
    warning = "Warning"
    syncing = "Syncing"
    disconnected = "Disconnected"
    error = "Error"
    disabled = "Disabled"


class ConnectorPermissionLevel(StrEnum):
    metadata_only = "metadata_only"
    read_only = "read_only"
    read = "read"
    write = "write"
    admin = "admin"


class SyncMode(StrEnum):
    manual = "manual"
    scheduled = "scheduled"
    incremental = "incremental"
    webhook = "webhook"


@dataclass(frozen=True)
class ConnectorIdentity:
    id: str | None
    workspace_id: str
    owner_id: str | None
    type: str
    name: str


@dataclass(frozen=True)
class ConnectorMetadata:
    connector_type: str
    display_name: str
    description: str
    category: str
    supports_incremental_sync: bool = False
    supports_webhooks: bool = False
    supported_permissions: tuple[ConnectorPermissionLevel, ...] = (
        ConnectorPermissionLevel.read_only,
    )


@dataclass(frozen=True)
class ConnectorPermissions:
    scopes: tuple[str, ...]
    level: ConnectorPermissionLevel = ConnectorPermissionLevel.read_only
    workspace_id: str | None = None


@dataclass(frozen=True)
class ConnectorResult:
    ok: bool
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryResult:
    schema: dict[str, Any]
    discovered_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class SyncRequest:
    mode: SyncMode
    cursor: str | None = None
    requested_by: str | None = None


@dataclass(frozen=True)
class SyncResult:
    health: ConnectorHealth
    synced_at: datetime
    items_synced: int = 0
    cursor: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    resources: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SearchResult:
    results: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectorResourceRef:
    provider_resource_id: str
    resource_type: str
    title: str
    mime_type: str | None = None
    size: int | None = None
    source_url: str | None = None
    parent_path: str | None = None
    author: str | None = None
    participants: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    modified_at: datetime | None = None
    provider_version: str | None = None
    content_hash: str | None = None
    permissions_metadata: dict[str, Any] = field(default_factory=dict)
    provider_metadata: dict[str, Any] = field(default_factory=dict)
    sync_cursor: str | None = None
    deleted: bool = False
