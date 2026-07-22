from datetime import date

from django.test import TestCase

from assessments.models import Requirement, Response
from assessments.services import build_action_items, calculate_results, report_payload

from .factories import make_assessment, make_framework, make_question


class ScoringTests(TestCase):
    def setUp(self):
        self.assessment = make_assessment()
        self.framework = make_framework()
        self.requirement = Requirement.objects.create(
            framework=self.framework,
            code="ROB",
            title="Robustness",
            description="Test robustness",
            sort_order=1,
        )

    def test_empty_assessment_has_zero_coverage_and_no_readiness_score(self):
        make_question("ROB-01", requirement=self.requirement)
        result = calculate_results(self.assessment)
        self.assertEqual(result["coverage_percent"], 0)
        self.assertIsNone(result["readiness_percent"])

    def test_weighted_readiness_distinguishes_question_weights(self):
        high = make_question("ROB-01", weight=3, requirement=self.requirement)
        low = make_question("ROB-02", weight=1, requirement=self.requirement)
        Response.objects.create(
            assessment=self.assessment, question=high, answer=Response.Answer.YES, rationale="Tested"
        )
        Response.objects.create(
            assessment=self.assessment, question=low, answer=Response.Answer.NO, rationale="Missing"
        )
        result = calculate_results(self.assessment)
        self.assertEqual(result["coverage_percent"], 100)
        self.assertEqual(result["readiness_percent"], 75)

    def test_partial_answer_receives_half_weight(self):
        question = make_question("ROB-01", weight=3, requirement=self.requirement)
        Response.objects.create(
            assessment=self.assessment,
            question=question,
            answer=Response.Answer.PARTIAL,
            rationale="Some scenarios covered",
        )
        self.assertEqual(calculate_results(self.assessment)["readiness_percent"], 50)

    def test_not_applicable_counts_as_answered_but_not_scored(self):
        question = make_question("ROB-01", requirement=self.requirement)
        Response.objects.create(
            assessment=self.assessment,
            question=question,
            answer=Response.Answer.NOT_APPLICABLE,
            rationale="",
        )
        result = calculate_results(self.assessment)
        self.assertEqual(result["coverage_percent"], 100)
        self.assertIsNone(result["readiness_percent"])
        self.assertEqual(result["dimensions"][0]["applicable"], 0)

    def test_inactive_questions_are_excluded(self):
        question = make_question("ROB-01", requirement=self.requirement)
        question.active = False
        question.save()
        self.assertEqual(calculate_results(self.assessment)["question_count"], 0)

    def test_action_items_include_no_and_partial_answers_only(self):
        questions = [make_question(f"ROB-0{i}", requirement=self.requirement) for i in range(1, 4)]
        Response.objects.create(
            assessment=self.assessment,
            question=questions[0],
            answer=Response.Answer.NO,
            rationale="Missing",
            owner="Security lead",
            target_date=date(2026, 9, 1),
        )
        Response.objects.create(
            assessment=self.assessment,
            question=questions[1],
            answer=Response.Answer.PARTIAL,
            rationale="Incomplete",
        )
        Response.objects.create(
            assessment=self.assessment,
            question=questions[2],
            answer=Response.Answer.YES,
            rationale="Complete",
        )
        actions = build_action_items(self.assessment)
        self.assertEqual([item["priority"] for item in actions], ["high", "medium"])
        self.assertEqual(actions[0]["owner"], "Security lead")
        self.assertEqual(actions[0]["target_date"], "2026-09-01")

    def test_report_payload_contains_context_results_and_disclaimer(self):
        question = make_question("ROB-01", requirement=self.requirement)
        Response.objects.create(
            assessment=self.assessment,
            question=question,
            answer=Response.Answer.YES,
            rationale="Passed release tests",
            evidence_reference="TEST-REPORT-04",
        )
        payload = report_payload(self.assessment)
        self.assertEqual(payload["assessment"]["system_name"], "Decision support system")
        self.assertEqual(payload["responses"][0]["evidence_reference"], "TEST-REPORT-04")
        self.assertIn("not a legal compliance determination", payload["disclaimer"])
