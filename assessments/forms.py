from typing import ClassVar

from django import forms

from .models import Assessment, Response


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields: ClassVar[list[str]] = [
            "organisation_name",
            "system_name",
            "intended_purpose",
            "lifecycle_stage",
            "organisation_role",
        ]
        widgets: ClassVar[dict[str, forms.Widget | type[forms.Widget]]] = {
            "intended_purpose": forms.Textarea(attrs={"rows": 4})
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields: ClassVar[list[str]] = ["answer", "rationale", "evidence_reference", "owner", "target_date"]
        widgets: ClassVar[dict[str, forms.Widget | type[forms.Widget]]] = {
            "answer": forms.RadioSelect,
            "rationale": forms.Textarea(attrs={"rows": 4}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("answer") != Response.Answer.NOT_APPLICABLE and not cleaned.get("rationale", "").strip():
            self.add_error("rationale", "Explain the answer so reviewers can understand the evidence and assumptions.")
        return cleaned
