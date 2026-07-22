from django.test import TestCase
from django.urls import reverse

from assessments.models import Assessment, AssessmentEvent, Response

from .factories import make_assessment, make_question


class ViewTests(TestCase):
    def test_dashboard_lists_assessment(self):
        assessment = make_assessment()
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, assessment.system_name)

    def test_create_assessment_records_event_and_redirects(self):
        response = self.client.post(
            reverse("assessment-create"),
            {
                "organisation_name": "Small Company AB",
                "system_name": "Routing assistant",
                "intended_purpose": "Prioritise incoming support cases for review.",
                "lifecycle_stage": Assessment.LifecycleStage.PILOT,
                "organisation_role": Assessment.OrganisationRole.DEPLOYER,
            },
        )
        assessment = Assessment.objects.get(system_name="Routing assistant")
        self.assertRedirects(response, reverse("assessment-detail", args=[assessment.pk]))
        self.assertTrue(AssessmentEvent.objects.filter(assessment=assessment, event_type="created").exists())

    def test_detail_groups_questions_and_shows_score(self):
        assessment = make_assessment()
        question = make_question()
        Response.objects.create(assessment=assessment, question=question, answer=Response.Answer.YES, rationale="Done")
        response = self.client.get(reverse("assessment-detail", args=[assessment.pk]))
        self.assertContains(response, question.code)
        self.assertContains(response, "100%")

    def test_response_form_saves_evidence_and_audit_event(self):
        assessment = make_assessment()
        question = make_question()
        response = self.client.post(
            reverse("response-edit", args=[assessment.pk, question.pk]),
            {
                "answer": Response.Answer.PARTIAL,
                "rationale": "Only the pilot dataset is covered.",
                "evidence_reference": "DATA-REVIEW-2",
                "owner": "Data lead",
                "target_date": "2026-09-30",
            },
        )
        self.assertRedirects(response, reverse("assessment-detail", args=[assessment.pk]))
        saved = Response.objects.get(assessment=assessment, question=question)
        self.assertEqual(saved.evidence_reference, "DATA-REVIEW-2")
        self.assertTrue(AssessmentEvent.objects.filter(assessment=assessment, event_type="response_recorded").exists())

    def test_transition_endpoint_rejects_get(self):
        assessment = make_assessment()
        response = self.client.get(reverse("assessment-transition", args=[assessment.pk]))
        self.assertEqual(response.status_code, 405)

    def test_transition_endpoint_changes_status(self):
        assessment = make_assessment()
        response = self.client.post(
            reverse("assessment-transition", args=[assessment.pk]),
            {"status": Assessment.Status.IN_REVIEW},
        )
        self.assertRedirects(response, reverse("assessment-detail", args=[assessment.pk]))
        assessment.refresh_from_db()
        self.assertEqual(assessment.status, Assessment.Status.IN_REVIEW)

    def test_json_report_is_downloadable(self):
        assessment = make_assessment()
        response = self.client.get(reverse("assessment-report", args=[assessment.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["assessment"]["system_name"], assessment.system_name)
        self.assertIn("attachment", response.headers["Content-Disposition"])
