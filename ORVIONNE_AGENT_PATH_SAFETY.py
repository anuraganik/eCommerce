"""Representative excerpt from the ORVIONNE local device agent.

The full private agent handles pairing, heartbeat, device-scoped credentials and
server-dispatched read-only actions. This excerpt focuses on local filesystem
safety: approved roots, path traversal prevention, extension allowlists and
hard file-size limits.
"""

import base64
import hashlib
import mimetypes
from pathlib import Path
from typing import Any

HARD_MAX_READ_BYTES = 25 * 1024 * 1024


class PathSafetyError(ValueError):
    """Requested path escaped its approved root or failed a local safety check."""


def resolve_within_root(root_path: str, relative_path: str) -> Path:
    root = Path(root_path).expanduser()
    if not root.is_absolute() and root_path:
        raise PathSafetyError("Approved root must be an absolute path.")
    if Path(relative_path).is_absolute():
        raise PathSafetyError("Absolute paths are not allowed inside an approved root.")

    resolved_root = root.resolve(strict=False)
    candidate = (root / relative_path).resolve(strict=False)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise PathSafetyError("Path escapes the approved root.") from exc
    return candidate


def is_extension_allowed(path: Path, allowed_file_types: list[str] | None) -> bool:
    if not allowed_file_types:
        return True
    suffix = path.suffix.lower().lstrip(".")
    return suffix in {ext.lower().lstrip(".") for ext in allowed_file_types}


def action_read_file_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    path = resolve_within_root(payload["root_path"], payload["relative_path"])
    if not path.is_file():
        raise PathSafetyError("File not found within the approved folder.")
    stat = path.stat()
    mime_type, _ = mimetypes.guess_type(path.name)
    return {
        "name": path.name,
        "size": stat.st_size,
        "modified_at_epoch": stat.st_mtime,
        "mime_type": mime_type,
    }


def action_read_approved_file(payload: dict[str, Any]) -> dict[str, Any]:
    path = resolve_within_root(payload["root_path"], payload["relative_path"])
    if not path.is_file():
        raise PathSafetyError("File not found within the approved folder.")
    if not is_extension_allowed(path, payload.get("allowed_file_types")):
        raise PathSafetyError("File type is not in the approved allowlist.")

    size = path.stat().st_size
    max_bytes = payload.get("max_file_size_bytes") or HARD_MAX_READ_BYTES
    max_bytes = min(max_bytes, HARD_MAX_READ_BYTES)
    if size > max_bytes:
        raise PathSafetyError(f"File exceeds the approved size limit ({max_bytes} bytes).")

    data = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(path.name)
    return {
        "name": path.name,
        "size": size,
        "mime_type": mime_type,
        "content_base64": base64.b64encode(data).decode("ascii"),
        "content_sha256": hashlib.sha256(data).hexdigest(),
    }
