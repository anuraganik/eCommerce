"""Connector-sourced document ingestion with encrypted object storage."""

import uuid
from contextlib import suppress

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connector_resource import ConnectorResource
from app.models.data_connector import DataConnector
from app.models.document import Document, DocumentProcessingStep, DocumentStatus
from app.models.encryption import EncryptedObjectStatus
from app.services.crypto.exceptions import EncryptedObjectNotFoundError
from app.services.crypto.service import (
    encrypt_and_store,
    get_active_encrypted_object,
    opaque_object_key,
)
from app.services.documents.indexing import (
    STEP_PROGRESS,
    log_processing_step,
    mark_failed,
    set_processing_step,
)
from app.services.documents.storage import delete_original_file


def create_connector_document(
    db: Session,
    *,
    connector: DataConnector,
    resource: ConnectorResource,
    filename: str,
    content_type: str,
    data: bytes,
) -> Document:
    document_id = uuid.uuid4()
    object_id = uuid.uuid4()
    storage_path = opaque_object_key(connector.workspace_id, object_id)
    document = Document(
        id=document_id,
        workspace_id=connector.workspace_id,
        uploaded_by=connector.created_by,
        filename=filename,
        content_type=content_type,
        storage_path=storage_path,
        file_size=len(data),
        status=DocumentStatus.uploading,
        processing_step=DocumentProcessingStep.uploading,
        progress_percent=STEP_PROGRESS[DocumentProcessingStep.uploading],
        chunk_count=0,
        chunks_count=0,
        extracted_text_chars=0,
        document_metadata={
            "source": "connector",
            "connector_type": connector.type,
            "connector_id": str(connector.id),
            "provider_resource_id": resource.provider_resource_id,
        },
        source_connector_id=connector.id,
        source_resource_id=resource.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    log_processing_step(document, "connector document created")

    try:
        encrypt_and_store(
            db,
            workspace_id=connector.workspace_id,
            document_id=document_id,
            resource_type="document",
            storage_bucket=settings.minio_bucket,
            content_type=content_type,
            data=data,
            object_id=object_id,
        )
        db.commit()
    except Exception:
        mark_failed(db, document, "Connector content storage failed.")
        raise

    set_processing_step(db, document, DocumentProcessingStep.stored)
    return document


def remove_connector_document(db: Session, document: Document) -> None:
    storage_path = document.storage_path
    with suppress(EncryptedObjectNotFoundError):
        encrypted_object = get_active_encrypted_object(
            db,
            workspace_id=document.workspace_id,
            resource_type="document",
            resource_id=document.id,
        )
        encrypted_object.status = EncryptedObjectStatus.tombstoned
        db.add(encrypted_object)

    db.delete(document)
    db.commit()

    with suppress(Exception):
        delete_original_file(storage_path)
