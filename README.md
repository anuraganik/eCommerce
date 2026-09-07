# ORVIONNE — Technical Interview Code Sample

**Private AI · Connector Platform · Local-First Intelligence · Controlled Automation**

This branch is a curated code sample from the ORVIONNE project prepared for technical interview review. It shows implementation patterns across Python/FastAPI backend engineering, database and SaaS connectors, AI provider abstraction, autonomous planning and safety, local-first TypeScript logic, device-side access controls and tests.

## Recommended review path

1. [`ORVIONNE_CONNECTOR_BASE.py`](./ORVIONNE_CONNECTOR_BASE.py) — reusable integration contract
2. [`ORVIONNE_POSTGRES_CONNECTOR.py`](./ORVIONNE_POSTGRES_CONNECTOR.py) — real read-only PostgreSQL connector
3. [`ORVIONNE_CONNECTOR_SECURITY.py`](./ORVIONNE_CONNECTOR_SECURITY.py) — SSRF/network/content safety
4. [`ORVIONNE_PLANNER_POLICIES.py`](./ORVIONNE_PLANNER_POLICIES.py) — risk, approvals, AI privacy and prompt-injection defense
5. [`ORVIONNE_PLAN_VALIDATOR.py`](./ORVIONNE_PLAN_VALIDATOR.py) — independent plan validation
6. [`ORVIONNE_DESKTOP_EXPERIENCE_ENGINE.ts`](./ORVIONNE_DESKTOP_EXPERIENCE_ENGINE.ts) — local-first/offline TypeScript experience engine
7. [`ORVIONNE_AGENT_PATH_SAFETY.py`](./ORVIONNE_AGENT_PATH_SAFETY.py) — device-side path traversal and read controls
8. [`ORVIONNE_PLANNER_SECURITY_TESTS.py`](./ORVIONNE_PLANNER_SECURITY_TESTS.py) — representative safety tests

## Additional backend samples

- [`ORVIONNE_BACKEND_PYPROJECT.toml`](./ORVIONNE_BACKEND_PYPROJECT.toml) — Python 3.12 / FastAPI stack and tooling
- [`ORVIONNE_AUTH_SECURITY.py`](./ORVIONNE_AUTH_SECURITY.py) — bcrypt password handling and JWT access tokens
- [`ORVIONNE_AI_PROVIDER_BASE.py`](./ORVIONNE_AI_PROVIDER_BASE.py) — normalized LLM provider interface
- [`ORVIONNE_AI_OLLAMA_PROVIDER.py`](./ORVIONNE_AI_OLLAMA_PROVIDER.py) — local inference provider
- [`ORVIONNE_AI_PROVIDER_SELECTOR.py`](./ORVIONNE_AI_PROVIDER_SELECTOR.py) — workspace/deployment-aware provider selection
- [`ORVIONNE_CONNECTOR_MODELS.py`](./ORVIONNE_CONNECTOR_MODELS.py) — normalized integration domain models
- [`ORVIONNE_CONNECTOR_REGISTRY.py`](./ORVIONNE_CONNECTOR_REGISTRY.py) — plugin-style registration and discovery
- [`ORVIONNE_CONNECTOR_INGESTION.py`](./ORVIONNE_CONNECTOR_INGESTION.py) — connector-driven encrypted document ingestion
- [`ORVIONNE_PLANNER_MODELS.py`](./ORVIONNE_PLANNER_MODELS.py) — capability, step and plan domain objects

## Architecture represented

```text
                    Next.js / React UI
                            |
                            v
                      FastAPI API
                 Auth · RBAC · Audit
                   /             \
                  v               v
         Knowledge Engine      Connector SDK
         docs · vectors        DB · SaaS · Agent
              |                     |
              v                     v
      PostgreSQL + pgvector    Local Device Agent
              |               approved read-only access
              v
         Redis / MinIO

                  AI Provider Layer
             mock / cloud / local Ollama
                         |
                         v
                 Autonomous Planner
        capability discovery -> validation
          -> risk / approval -> execution
```

## What this sample demonstrates

- Python 3.12, FastAPI and SQLAlchemy architecture
- PostgreSQL and pgvector foundations
- Redis and MinIO integration patterns
- JWT authentication and bcrypt password handling
- Connector SDK / registry architecture
- Read-only database transactions and schema discovery
- Network and metadata-service protection
- Workspace-aware and permission-aware capability design
- AI provider abstraction with local inference support
- Fail-safe action risk classification
- Human approval gates for higher-risk actions
- Stale-approval protection
- Local-only, metadata-only and external-AI privacy modes
- Context minimization and secret-like-content redaction
- Prompt-injection containment for retrieved content
- Offline/local-first desktop behavior in TypeScript
- Local filesystem path traversal prevention
- File-type and hard-size controls for device access
- Test-driven safety constraints

## Product context

ORVIONNE is a local-first private intelligence platform designed to connect business documents, databases, APIs and internal systems to AI while maintaining controlled access, workspace isolation and auditable behavior.

**Core principle:** Your AI. Your data. Your infrastructure.

## Scope of this repository

This is a technical interview sample rather than the production deployment repository. Operational configuration and deployment-specific material are intentionally outside this branch.

**Author:** Anik Ahmed  
**Project:** ORVIONNE / Auranik Group Europe
