from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Framework(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=180)
    version = models.CharField(max_length=40)
    source_url = models.URLField()
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.version})"


class RegulatoryReference(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=180)
    url = models.URLField()

    def __str__(self) -> str:
        return self.code


class Requirement(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, related_name="requirements")
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=180)
    description = models.TextField()
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "code"]
        constraints = [models.UniqueConstraint(fields=["framework", "code"], name="unique_framework_requirement")]

    def __str__(self) -> str:
        return f"{self.code}: {self.title}"


class Question(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name="questions")
    code = models.CharField(max_length=40, unique=True)
    text = models.TextField()
    guidance = models.TextField(blank=True)
    weight = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    active = models.BooleanField(default=True)
    references = models.ManyToManyField(RegulatoryReference, blank=True, related_name="questions")

    class Meta:
        ordering = ["requirement__sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.code}: {self.text[:60]}"


class Assessment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In review"
        COMPLETED = "completed", "Completed"

    class LifecycleStage(models.TextChoices):
        CONCEPT = "concept", "Concept"
        DEVELOPMENT = "development", "Development"
        PILOT = "pilot", "Pilot"
        OPERATION = "operation", "Operation"

    class OrganisationRole(models.TextChoices):
        PROVIDER = "provider", "AI system provider"
        DEPLOYER = "deployer", "AI system deployer"
        BOTH = "both", "Provider and deployer"
        OTHER = "other", "Other"

    organisation_name = models.CharField(max_length=180)
    system_name = models.CharField(max_length=180)
    intended_purpose = models.TextField()
    lifecycle_stage = models.CharField(max_length=20, choices=LifecycleStage.choices)
    organisation_role = models.CharField(max_length=20, choices=OrganisationRole.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.system_name} - {self.get_status_display()}"


class Response(models.Model):
    class Answer(models.TextChoices):
        YES = "yes", "Yes"
        PARTIAL = "partial", "Partly"
        NO = "no", "No"
        NOT_APPLICABLE = "not_applicable", "Not applicable"

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="responses")
    answer = models.CharField(max_length=20, choices=Answer.choices)
    rationale = models.TextField(blank=True)
    evidence_reference = models.CharField(max_length=300, blank=True)
    owner = models.CharField(max_length=180, blank=True)
    target_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assessment", "question"], name="unique_assessment_response")]

    def __str__(self) -> str:
        return f"{self.assessment.system_name} / {self.question.code}: {self.answer}"


class AssessmentEvent(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.assessment.system_name}: {self.event_type}"
