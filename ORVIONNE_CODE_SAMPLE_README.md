# ORVIONNE — Interview Code Sample

This branch contains a curated technical sample from the ORVIONNE project for interview review. It shows real implementation patterns across the backend, connector framework, database integration, AI provider abstraction, autonomous planning, local-first desktop logic, device-side safety and tests.

## Start here

For a quick review, open these files in this order:

1. `ORVIONNE_CONNECTOR_BASE.py` — integration architecture
2. `ORVIONNE_POSTGRES_CONNECTOR.py` — a real read-only database connector
3. `ORVIONNE_PLANNER_POLICIES.py` — risk, privacy and prompt-injection controls
4. `ORVIONNE_PLAN_VALIDATOR.py` — independent pre-execution safety validation
5. `ORVIONNE_DESKTOP_EXPERIENCE_ENGINE.ts` — TypeScript local-first UX logic
6. `ORVIONNE_AGENT_PATH_SAFETY.py` — device-side filesystem safeguards
7. `ORVIONNE_PLANNER_SECURITY_TESTS.py` — representative safety tests

## Full code included

### Backend / platform
- `ORVIONNE_BACKEND_PYPROJECT.toml` — Python/FastAPI backend stack and tooling
- `ORVIONNE_AI_PROVIDER_BASE.py` — normalized LLM provider interface
- `ORVIONNE_AI_OLLAMA_PROVIDER.py` — local inference provider
- `ORVIONNE_AI_PROVIDER_SELECTOR.py` — deployment/workspace-aware provider selection

### Connector SDK / integrations
- `ORVIONNE_CONNECTOR_BASE.py` — abstract connector contract
- `ORVIONNE_CONNECTOR_MODELS.py` — normalized connector domain models
- `ORVIONNE_CONNECTOR_REGISTRY.py` — plugin-style connector registration/discovery
- `ORVIONNE_CONNECTOR_SECURITY.py` — network validation, SSRF controls and safe indexing checks
- `ORVIONNE_POSTGRES_CONNECTOR.py` — PostgreSQL schema discovery, health checks and read-only query execution

### Autonomous planning / AI safety
- `ORVIONNE_PLANNER_MODELS.py` — planner domain objects and capability model
- `ORVIONNE_PLAN_VALIDATOR.py` — dependency, authorization, risk and timeout validation
- `ORVIONNE_PLANNER_POLICIES.py` — risk classification, approval gating, AI privacy modes, context minimization and prompt-injection defense

### Desktop / local device
- `ORVIONNE_DESKTOP_EXPERIENCE_ENGINE.ts` — local-first/offline adaptive UX logic
- `ORVIONNE_AGENT_PATH_SAFETY.py` — approved-root resolution, path traversal prevention, file allowlists and hard read limits

### Tests
- `ORVIONNE_PLANNER_SECURITY_TESTS.py` — representative fail-safe risk, stale-approval, injection, redaction and local-only-policy tests

## Architecture represented

```text
Next.js / React UI
        |
        v
FastAPI API
Auth · RBAC · Audit
   |             |
   v             v
Knowledge      Connector SDK
Engine         DB · SaaS · Local Agent
   |                |
   v                v
PostgreSQL       Device Agent
+ pgvector       approved read-only access
   |
Redis / MinIO

AI Provider Layer
mock / cloud / local Ollama
        |
        v
Autonomous Planner
capability discovery -> validation -> risk/approval -> controlled execution
```

## Engineering themes

Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, pgvector, Redis, MinIO, TypeScript, React, local-model integration, connector SDK architecture, tenant-aware authorization, read-only database transactions, network/metadata-service protection, fail-safe risk classification, human approval gates, AI privacy modes, context redaction, prompt-injection containment, local-first desktop behavior, path traversal prevention and test-driven safety constraints.

This is an interview code sample rather than a production deployment package.

**Author:** Anik Ahmed — ORVIONNE / Auranik Group Europe
