"""Independent validation for an ORVIONNE plan before persistence or execution."""

from app.intelligence.planner import policies
from app.intelligence.planner.models import (
    ApprovalRequirement,
    CapabilitySet,
    PlanBlueprint,
    ValidationIssue,
    ValidationResult,
)


def validate_plan(blueprint: PlanBlueprint, capabilities: CapabilitySet) -> ValidationResult:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if not blueprint.steps:
        return ValidationResult(
            valid=False,
            errors=(ValidationIssue("empty_plan", "A plan must contain at least one step."),),
        )

    sequences = [step.sequence for step in blueprint.steps]
    if len(sequences) != len(set(sequences)):
        errors.append(
            ValidationIssue("duplicate_sequence", "Step sequence numbers must be unique.")
        )
    sequence_set = set(sequences)

    for step in blueprint.steps:
        for dependency in step.dependencies:
            if dependency not in sequence_set:
                errors.append(
                    ValidationIssue(
                        "unresolved_dependency",
                        f"Step {step.sequence} depends on missing step {dependency}.",
                        step.sequence,
                    )
                )
            elif dependency >= step.sequence:
                errors.append(
                    ValidationIssue(
                        "forward_dependency",
                        f"Step {step.sequence} cannot depend on step {dependency}, "
                        "which does not come strictly before it.",
                        step.sequence,
                    )
                )

        if step.action_id is not None and not capabilities.is_permitted(step.action_id):
            errors.append(
                ValidationIssue(
                    "unauthorized_capability",
                    f"Step {step.sequence} references '{step.action_id}', which is not a "
                    "permitted capability for this user/workspace.",
                    step.sequence,
                )
            )

        if (
            not policies.is_executable_this_release(step.risk_level)
            and step.approval_requirement != ApprovalRequirement.required
        ):
            errors.append(
                ValidationIssue(
                    "missing_approval_requirement",
                    f"Step {step.sequence} has risk {step.risk_level.value} and must be "
                    "marked as requiring approval before it may ever run.",
                    step.sequence,
                )
            )

        if step.timeout_seconds <= 0 or step.timeout_seconds > 300:
            warnings.append(
                ValidationIssue(
                    "unusual_timeout",
                    f"Step {step.sequence} has an unusual timeout of {step.timeout_seconds}s.",
                    step.sequence,
                )
            )

    return ValidationResult(valid=not errors, errors=tuple(errors), warnings=tuple(warnings))
