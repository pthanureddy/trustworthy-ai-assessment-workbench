from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AssessmentForm, ResponseForm
from .models import Assessment, AssessmentEvent, Question, Response
from .services import build_action_items, calculate_results, report_payload, transition_assessment


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "assessments/dashboard.html", {"assessments": Assessment.objects.all()})


def assessment_create(request: HttpRequest) -> HttpResponse:
    form = AssessmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assessment = form.save()
        AssessmentEvent.objects.create(assessment=assessment, event_type="created", detail={})
        messages.success(request, "Assessment created. Add rationale and evidence for each answer.")
        return redirect("assessment-detail", pk=assessment.pk)
    return render(request, "assessments/assessment_form.html", {"form": form})


def assessment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    assessment = get_object_or_404(Assessment, pk=pk)
    questions = Question.objects.filter(active=True).select_related("requirement").prefetch_related("references")
    response_map = {response.question_id: response for response in assessment.responses.all()}
    grouped: list[dict] = []
    current_requirement = None
    for question in questions:
        if current_requirement is None or current_requirement["id"] != question.requirement_id:
            current_requirement = {
                "id": question.requirement_id,
                "code": question.requirement.code,
                "title": question.requirement.title,
                "questions": [],
            }
            grouped.append(current_requirement)
        current_requirement["questions"].append({"question": question, "response": response_map.get(question.id)})
    return render(
        request,
        "assessments/assessment_detail.html",
        {
            "assessment": assessment,
            "groups": grouped,
            "results": calculate_results(assessment),
            "actions": build_action_items(assessment),
        },
    )


def response_edit(request: HttpRequest, assessment_pk: int, question_pk: int) -> HttpResponse:
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    question = get_object_or_404(Question.objects.prefetch_related("references"), pk=question_pk, active=True)
    instance = Response.objects.filter(assessment=assessment, question=question).first()
    form = ResponseForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        response = form.save(commit=False)
        response.assessment = assessment
        response.question = question
        response.save()
        AssessmentEvent.objects.create(
            assessment=assessment,
            event_type="response_recorded",
            detail={"question": question.code, "answer": response.answer},
        )
        messages.success(request, f"Saved response for {question.code}.")
        return redirect("assessment-detail", pk=assessment.pk)
    return render(
        request,
        "assessments/response_form.html",
        {"assessment": assessment, "question": question, "form": form},
    )


@require_POST
def assessment_transition(request: HttpRequest, pk: int) -> HttpResponse:
    assessment = get_object_or_404(Assessment, pk=pk)
    try:
        transition_assessment(assessment, request.POST.get("status", ""))
        messages.success(request, f"Assessment moved to {assessment.get_status_display()}.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("assessment-detail", pk=pk)


def assessment_report(request: HttpRequest, pk: int) -> JsonResponse:
    assessment = get_object_or_404(Assessment, pk=pk)
    response = JsonResponse(report_payload(assessment), json_dumps_params={"indent": 2})
    response["Content-Disposition"] = f'attachment; filename="assessment-{pk}.json"'
    return response
