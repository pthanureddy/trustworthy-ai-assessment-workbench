from django.test import TestCase

from assessments.forms import ResponseForm
from assessments.models import Response


class ResponseFormTests(TestCase):
    def test_rationale_is_required_for_applicable_answer(self):
        form = ResponseForm(data={"answer": Response.Answer.YES, "rationale": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("rationale", form.errors)

    def test_not_applicable_answer_can_omit_rationale(self):
        form = ResponseForm(data={"answer": Response.Answer.NOT_APPLICABLE, "rationale": ""})
        self.assertTrue(form.is_valid())

    def test_target_date_must_be_a_valid_date(self):
        form = ResponseForm(data={"answer": Response.Answer.NO, "rationale": "Gap", "target_date": "not-a-date"})
        self.assertFalse(form.is_valid())
        self.assertIn("target_date", form.errors)
