import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from assessments.models import Framework, Question, RegulatoryReference, Requirement


class Command(BaseCommand):
    help = "Load the versioned sample assessment framework from data/framework.json"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=Path, default=settings.BASE_DIR / "data" / "framework.json")

    @transaction.atomic
    def handle(self, *args, **options):
        payload = json.loads(options["path"].read_text(encoding="utf-8"))
        framework_data = payload["framework"]
        framework, _ = Framework.objects.update_or_create(
            code=framework_data["code"],
            defaults={
                "name": framework_data["name"],
                "version": framework_data["version"],
                "source_url": framework_data["source_url"],
                "notes": framework_data["notes"],
            },
        )

        references = {}
        for ref_data in payload["regulatory_references"]:
            reference, _ = RegulatoryReference.objects.update_or_create(
                code=ref_data["code"],
                defaults={"title": ref_data["title"], "url": ref_data["url"]},
            )
            references[reference.code] = reference

        seen_question_codes = []
        for requirement_data in payload["requirements"]:
            requirement, _ = Requirement.objects.update_or_create(
                framework=framework,
                code=requirement_data["code"],
                defaults={
                    "title": requirement_data["title"],
                    "description": requirement_data["description"],
                    "sort_order": requirement_data["sort_order"],
                },
            )
            for question_data in requirement_data["questions"]:
                question, _ = Question.objects.update_or_create(
                    code=question_data["code"],
                    defaults={
                        "requirement": requirement,
                        "text": question_data["text"],
                        "guidance": question_data["guidance"],
                        "weight": question_data["weight"],
                        "active": True,
                    },
                )
                question.references.set(references[code] for code in question_data["references"])
                seen_question_codes.append(question.code)

        Question.objects.filter(requirement__framework=framework).exclude(code__in=seen_question_codes).update(
            active=False
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {framework.name}: {len(payload['requirements'])} dimensions and {len(seen_question_codes)} questions"
            )
        )
