# ORVIONNE — Private AI Platform

This is a sanitized public portfolio overview of ORVIONNE / Auranik AI. Production credentials, secret files, deployment configuration, and internal operational details are intentionally excluded.

## Overview

ORVIONNE is a local-first private intelligence platform designed to let organizations use AI with their own documents, databases, APIs, and internal systems while keeping access controlled and auditable.

**Core principle:** Your AI. Your data. Your infrastructure.

## What the project demonstrates

- FastAPI backend with JWT authentication, workspace-scoped RBAC, tenant isolation, and API versioning
- Next.js / React / TypeScript web console
- PostgreSQL + pgvector semantic search
- Redis queue/cache foundation
- MinIO private object storage
- Document ingestion and grounded knowledge retrieval
- Reusable Connector SDK for databases, SaaS tools, documents, and local integrations
- Autonomous planner foundation with validation, risk scoring, approvals, and controlled execution
- ORVIONNE local device agent with secure pairing, heartbeat, approved-root validation, and read-only file actions
- Dockerized local and production architecture

## High-level architecture

```text
Next.js Web UI
      |
      v
FastAPI API
Auth · RBAC · Audit
   |           |
   v           v
Knowledge     Connector SDK
Engine        DB · SaaS · Agent
   |                 |
   v                 v
PostgreSQL        ORVIONNE Agent
pgvector          approved read-only local access
   |
 MinIO / Redis
```

## Security highlights

- Workspace-scoped authorization and tenant-isolated queries
- Secrets loaded through environment variables or secret files rather than embedded in source code
- Connector credentials separated from ordinary application data
- Local agent file access restricted to approved roots and validated again on the device
- No arbitrary shell-command execution in the local agent
- Approval gates for higher-risk planner actions
- Sensitive values excluded from logs, prompts, API responses, and this showcase

## Technology stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, pgvector, Redis, MinIO  
**Frontend:** Next.js, React, TypeScript  
**AI:** provider abstraction, local-model support, cloud-provider integration foundation, vector retrieval  
**Infrastructure:** Docker Compose, containerized services  
**Security:** JWT, bcrypt, RBAC, audit logging, device-scoped credentials

## Selected code areas in the private development repository

```text
apps/api/app/connectors/                 Connector platform and safety model
apps/api/app/intelligence/planner/       Autonomous planning and risk controls
apps/api/app/services/                   Service/business layer
apps/api/tests/                          Backend tests
apps/web/                                Next.js application
apps/agent/orvionne_agent.py             Local device agent
apps/desktop/                            Local-first desktop work
apps/mobile/                             Mobile work
docs/                                    Architecture and engineering documentation
```

## Portfolio note

The production repository is private. This public showcase is intentionally limited to a technical overview until a standalone sanitized repository is published.

## Author

Anik Ahmed — software / cloud / technical support engineer and builder of ORVIONNE under Auranik Group Europe.
