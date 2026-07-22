from django.test import TestCase

from assessments.models import Assessment, AssessmentEvent
from assessments.services import transition_assessment

from .factories import make_assessment


class WorkflowTests(TestCase):
    def setUp(self):
        self.assessment = make_assessment()

    def test_draft_can_move_to_review(self):
        transition_assessment(self.assessment, Assessment.Status.IN_REVIEW)
        self.assertEqual(self.assessment.status, Assessment.Status.IN_REVIEW)

    def test_review_can_be_completed(self):
        self.assessment.status = Assessment.Status.IN_REVIEW
        self.assessment.save()
        transition_assessment(self.assessment, Assessment.Status.COMPLETED)
        self.assertEqual(self.assessment.status, Assessment.Status.COMPLETED)

    def test_completed_assessment_can_be_reopened_for_review(self):
        self.assessment.status = Assessment.Status.COMPLETED
        self.assessment.save()
        transition_assessment(self.assessment, Assessment.Status.IN_REVIEW)
        self.assertEqual(self.assessment.status, Assessment.Status.IN_REVIEW)

    def test_invalid_transition_does_not_modify_state(self):
        with self.assertRaisesMessage(ValueError, "not allowed"):
            transition_assessment(self.assessment, Assessment.Status.COMPLETED)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, Assessment.Status.DRAFT)

    def test_transition_creates_audit_event(self):
        transition_assessment(self.assessment, Assessment.Status.IN_REVIEW)
        event = AssessmentEvent.objects.get(assessment=self.assessment)
        self.assertEqual(event.event_type, "status_changed")
        self.assertEqual(event.detail, {"from": "draft", "to": "in_review"})
