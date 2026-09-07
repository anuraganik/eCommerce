"""In-memory domain objects used by the ORVIONNE planner before persistence."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.models.execution_plan import (
    ApprovalRequirement,
    FailurePolicy,
    GoalCategory,
    PlanRiskLevel,
)


@dataclass(frozen=True)
class GoalAnalysis:
    raw_goal: str
    normalized_goal: str
    category: GoalCategory
    confidence: float
    entities: tuple[str, ...] = ()
    time_range: tuple[datetime | None, datetime | None] = (None, None)
    requested_output: str = "answer"
    possible_sources: tuple[str, ...] = ()
    sensitivity: str = "normal"
    urgency: str = "normal"
    implies_action: bool = False
    needs_clarification: bool = False
    clarification_reason: str | None = None
    clarification_question: str | None = None


@dataclass(frozen=True)
class Capability:
    """A discovered and permitted capability available to the planner."""

    kind: str
    capability_id: str
    name: str
    description: str
    read_only: bool
    risk_level: PlanRiskLevel
    connector_id: uuid.UUID | None = None
    connector_type: str | None = None
    device_id: uuid.UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilitySet:
    actions: tuple[Capability, ...] = ()
    knowledge_sources: tuple[Capability, ...] = ()
    workflows: tuple[Capability, ...] = ()
    devices: tuple[Capability, ...] = ()

    def all(self) -> tuple[Capability, ...]:
        return self.actions + self.knowledge_sources + self.workflows + self.devices

    def find(self, capability_id: str) -> Capability | None:
        return next((c for c in self.all() if c.capability_id == capability_id), None)

    def is_permitted(self, capability_id: str) -> bool:
        return self.find(capability_id) is not None


@dataclass(frozen=True)
class StepBlueprint:
    sequence: int
    name: str
    description: str
    action_id: str | None
    input_mapping: dict[str, Any]
    output_variable: str | None
    dependencies: tuple[int, ...]
    risk_level: PlanRiskLevel
    read_only: bool
    connector_id: uuid.UUID | None = None
    device_id: uuid.UUID | None = None
    action_version: str = "1.0.0"
    required_permissions: tuple[str, ...] = ()
    approval_requirement: ApprovalRequirement = ApprovalRequirement.none
    timeout_seconds: int = 30
    retry_policy: dict[str, Any] = field(
        default_factory=lambda: {"max_attempts": 1, "backoff_seconds": 0}
    )
    failure_policy: FailurePolicy = FailurePolicy.abort
    verification_policy: dict[str, Any] | None = None


@dataclass(frozen=True)
class PlanBlueprint:
    goal_analysis: GoalAnalysis
    steps: tuple[StepBlueprint, ...]
    required_capabilities: tuple[str, ...]
    required_connectors: tuple[str, ...]
    required_permissions: tuple[str, ...]
    risk_level: PlanRiskLevel
    requires_approval: bool
    generation_method: str
    estimated_duration_ms: int
    estimated_token_usage: int
    estimated_external_cost: float
    data_classification: str = "internal"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    step_sequence: int | None = None


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[ValidationIssue, ...] = ()
    warnings: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True)
class VerificationCheck:
    name: str
    passed: bool
    details: str = ""


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    checks: tuple[VerificationCheck, ...]

    @property
    def failed_checks(self) -> tuple[VerificationCheck, ...]:
        return tuple(check for check in self.checks if not check.passed)


@dataclass(frozen=True)
class ClarificationNeeded:
    question: str
    reason: str
    options: tuple[str, ...] | None = None


@dataclass(frozen=True)
class AIPolicy:
    mode: str
    external_llm_allowed: bool
    max_context_chars: int
    provider_override: str | None = None
