from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from assessments.models import Framework, Question, RegulatoryReference, Requirement


class SeedCommandTests(TestCase):
    def test_seed_loads_versioned_content_and_mappings(self):
        output = StringIO()
        call_command("seed_framework", stdout=output)
        self.assertEqual(Framework.objects.get().version, "2026.1")
        self.assertEqual(Requirement.objects.count(), 7)
        self.assertEqual(Question.objects.filter(active=True).count(), 21)
        self.assertEqual(RegulatoryReference.objects.count(), 9)
        self.assertGreater(Question.objects.get(code="HUM-02").references.count(), 1)
        self.assertIn("21 questions", output.getvalue())

    def test_seed_is_idempotent(self):
        call_command("seed_framework", verbosity=0)
        call_command("seed_framework", verbosity=0)
        self.assertEqual(Framework.objects.count(), 1)
        self.assertEqual(Requirement.objects.count(), 7)
        self.assertEqual(Question.objects.count(), 21)

    def test_seed_reactivates_a_known_question(self):
        call_command("seed_framework", verbosity=0)
        question = Question.objects.get(code="ACC-03")
        question.active = False
        question.save()
        call_command("seed_framework", verbosity=0)
        question.refresh_from_db()
        self.assertTrue(question.active)
