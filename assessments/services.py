from dataclasses import asdict, dataclass
from typing import Any

from django.db import transaction

from .models import Assessment, AssessmentEvent, Question, Response

ANSWER_VALUE = {
    Response.Answer.YES: 1.0,
    Response.Answer.PARTIAL: 0.5,
    Response.Answer.NO: 0.0,
}


@dataclass(frozen=True)
class DimensionResult:
    code: str
    title: str
    answered: int
    applicable: int
    total: int
    coverage_percent: int
    readiness_percent: int | None


def _percent(numerator: float, denominator: float) -> int:
    return round((numerator / denominator) * 100) if denominator else 0


def calculate_results(assessment: Assessment) -> dict[str, Any]:
    questions = list(Question.objects.filter(active=True).select_related("requirement").prefetch_related("references"))
    response_map = {response.question_id: response for response in assessment.responses.select_related("question")}
    grouped: dict[int, dict[str, Any]] = {}
    total_weight = 0
    earned_weight = 0.0
    answered_count = 0

    for question in questions:
        requirement = question.requirement
        bucket = grouped.setdefault(
            requirement.id,
            {
                "code": requirement.code,
                "title": requirement.title,
                "total": 0,
                "answered": 0,
                "applicable": 0,
                "weight": 0,
                "earned": 0.0,
            },
        )
        bucket["total"] += 1
        response = response_map.get(question.id)
        if response is None:
            continue
        answered_count += 1
        bucket["answered"] += 1
        if response.answer == Response.Answer.NOT_APPLICABLE:
            continue
        bucket["applicable"] += 1
        bucket["weight"] += question.weight
        bucket["earned"] += question.weight * ANSWER_VALUE[response.answer]
        total_weight += question.weight
        earned_weight += question.weight * ANSWER_VALUE[response.answer]

    dimensions = []
    for bucket in grouped.values():
        readiness = _percent(bucket["earned"], bucket["weight"]) if bucket["weight"] else None
        dimensions.append(
            asdict(
                DimensionResult(
                    code=bucket["code"],
                    title=bucket["title"],
                    answered=bucket["answered"],
                    applicable=bucket["applicable"],
                    total=bucket["total"],
                    coverage_percent=_percent(bucket["answered"], bucket["total"]),
                    readiness_percent=readiness,
                )
            )
        )

    return {
        "question_count": len(questions),
        "answered_count": answered_count,
        "coverage_percent": _percent(answered_count, len(questions)),
        "readiness_percent": _percent(earned_weight, total_weight) if total_weight else None,
        "dimensions": dimensions,
    }


def build_action_items(assessment: Assessment) -> list[dict[str, Any]]:
    actions = []
    responses = assessment.responses.filter(answer__in=[Response.Answer.NO, Response.Answer.PARTIAL]).select_related(
        "question", "question__requirement"
    )
    for response in responses:
        priority = "high" if response.answer == Response.Answer.NO else "medium"
        actions.append(
            {
                "question_code": response.question.code,
                "dimension": response.question.requirement.title,
                "priority": priority,
                "action": response.question.guidance,
                "owner": response.owner,
                "target_date": response.target_date.isoformat() if response.target_date else None,
            }
        )
    return actions


ALLOWED_TRANSITIONS = {
    Assessment.Status.DRAFT: {Assessment.Status.IN_REVIEW},
    Assessment.Status.IN_REVIEW: {Assessment.Status.DRAFT, Assessment.Status.COMPLETED},
    Assessment.Status.COMPLETED: {Assessment.Status.IN_REVIEW},
}


@transaction.atomic
def transition_assessment(assessment: Assessment, target_status: str) -> Assessment:
    if target_status not in ALLOWED_TRANSITIONS.get(assessment.status, set()):
        raise ValueError(f"Transition from {assessment.status} to {target_status} is not allowed")
    previous = assessment.status
    assessment.status = target_status
    assessment.save(update_fields=["status", "updated_at"])
    AssessmentEvent.objects.create(
        assessment=assessment,
        event_type="status_changed",
        detail={"from": previous, "to": target_status},
    )
    return assessment


def report_payload(assessment: Assessment) -> dict[str, Any]:
    responses = []
    queryset = assessment.responses.select_related("question", "question__requirement").prefetch_related(
        "question__references"
    )
    for response in queryset.order_by("question__requirement__sort_order", "question__code"):
        responses.append(
            {
                "question_code": response.question.code,
                "dimension": response.question.requirement.title,
                "answer": response.answer,
                "rationale": response.rationale,
                "evidence_reference": response.evidence_reference,
                "owner": response.owner,
                "target_date": response.target_date.isoformat() if response.target_date else None,
                "regulatory_references": [ref.code for ref in response.question.references.all()],
            }
        )
    return {
        "assessment": {
            "id": assessment.pk,
            "organisation_name": assessment.organisation_name,
            "system_name": assessment.system_name,
            "intended_purpose": assessment.intended_purpose,
            "lifecycle_stage": assessment.lifecycle_stage,
            "organisation_role": assessment.organisation_role,
            "status": assessment.status,
            "updated_at": assessment.updated_at.isoformat(),
        },
        "results": calculate_results(assessment),
        "responses": responses,
        "action_items": build_action_items(assessment),
        "disclaimer": "This self-assessment supports internal readiness work and is not a legal compliance determination.",
    }
