from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.connectors.base import Connector
from app.connectors.models import (
    ConnectorHealth,
    ConnectorMetadata,
    ConnectorPermissionLevel,
    ConnectorPermissions,
    ConnectorResult,
    ConnectorType,
    DiscoveryResult,
    SearchResult,
    SyncMode,
    SyncRequest,
    SyncResult,
)
from app.connectors.permissions import read_only_permissions
from app.connectors.registry import register_connector


@register_connector(ConnectorType.postgres)
class PostgresSDKConnector(Connector):
    connector_type = ConnectorType.postgres

    def authenticate(self, config: dict[str, Any]) -> ConnectorResult:
        return self.test_connection(config)

    def test_connection(self, config: dict[str, Any]) -> ConnectorResult:
        with self._connect(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return ConnectorResult(ok=True, message="PostgreSQL connection healthy.")

    def discover(self, config: dict[str, Any]) -> DiscoveryResult:
        query = """
            SELECT table_schema, table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name, ordinal_position
        """
        tables: dict[tuple[str, str], dict[str, Any]] = {}
        with self._connect(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(query)
                for row in cursor.fetchall():
                    key = (row["table_schema"], row["table_name"])
                    table = tables.setdefault(
                        key,
                        {
                            "schema": row["table_schema"],
                            "name": row["table_name"],
                            "columns": [],
                        },
                    )
                    table["columns"].append(
                        {"name": row["column_name"], "type": row["data_type"]}
                    )
        return DiscoveryResult(schema={"tables": list(tables.values())})

    def sync(self, config: dict[str, Any], request: SyncRequest | None = None) -> SyncResult:
        discovery = self.discover(config)
        return SyncResult(
            health=ConnectorHealth.healthy,
            synced_at=discovery.discovered_at,
            items_synced=len(discovery.schema.get("tables", [])),
            cursor=request.cursor if request and request.mode == SyncMode.incremental else None,
            metadata={"schema": discovery.schema},
        )

    def search(self, config: dict[str, Any], query: str, limit: int) -> SearchResult:
        with self._connect(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SET LOCAL statement_timeout = %s", (config["timeout_ms"],))
                cursor.execute(query)
                rows = cursor.fetchmany(limit)
        return SearchResult(results=[dict(row) for row in rows])

    def permissions(self, config: dict[str, Any]) -> ConnectorPermissions:
        return read_only_permissions(
            "schema:read",
            "query:select",
            workspace_id=config.get("workspace_id"),
        )

    def health(self, config: dict[str, Any]) -> ConnectorHealth:
        try:
            self.test_connection(config)
        except Exception:
            return ConnectorHealth.error
        return ConnectorHealth.healthy

    def disconnect(self, config: dict[str, Any]) -> ConnectorResult:
        return ConnectorResult(ok=True, message="PostgreSQL connector disconnected.")

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            connector_type=ConnectorType.postgres,
            display_name="PostgreSQL",
            description="Read-only PostgreSQL database connector.",
            category="database",
            supports_incremental_sync=True,
            supported_permissions=(ConnectorPermissionLevel.read_only,),
        )

    def _connect(self, config: dict[str, Any]):
        return psycopg.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database_name"],
            user=config["username"],
            password=config["password"],
            sslmode=config.get("ssl_mode", "prefer"),
            row_factory=dict_row,
            connect_timeout=10,
        )
