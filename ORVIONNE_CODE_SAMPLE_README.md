# ORVIONNE — Interview Code Sample

This branch contains a curated technical sample from the ORVIONNE project for interview review. It shows real implementation patterns across the backend, connector framework, autonomous planning, local-first desktop logic, device-side safety and tests.

## Code included

- `ORVIONNE_BACKEND_PYPROJECT.toml` — Python/FastAPI backend stack and tooling
- `ORVIONNE_CONNECTOR_BASE.py` — abstract connector contract
- `ORVIONNE_CONNECTOR_MODELS.py` — normalized connector domain models
- `ORVIONNE_CONNECTOR_REGISTRY.py` — plugin-style connector registration/discovery
- `ORVIONNE_CONNECTOR_SECURITY.py` — network validation, SSRF controls and safe indexing checks
- `ORVIONNE_PLANNER_MODELS.py` — planner domain objects
- `ORVIONNE_PLAN_VALIDATOR.py` — independent pre-execution validation
- `ORVIONNE_PLANNER_POLICIES.py` — risk, approvals, privacy and prompt-injection controls
- `ORVIONNE_DESKTOP_EXPERIENCE_ENGINE.ts` — local-first/offline adaptive UX logic
- `ORVIONNE_AGENT_PATH_SAFETY.py` — representative local-agent path and read-safety logic
- `ORVIONNE_PLANNER_SECURITY_TESTS.py` — representative safety tests

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
+ pgvector
   |
Redis / MinIO

Autonomous Planner
capability discovery -> validation -> risk/approval -> controlled execution
```

## Engineering themes

Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, pgvector, Redis, MinIO, TypeScript, React, connector SDK architecture, tenant-aware authorization, fail-safe risk classification, human approval gates, AI privacy modes, prompt-injection containment, local-first desktop behavior, path traversal prevention and test-driven safety constraints.

This is an interview code sample rather than a production deployment package.

**Author:** Anik Ahmed — ORVIONNE / Auranik Group Europe
