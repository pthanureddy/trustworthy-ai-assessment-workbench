from assessments.models import Assessment, Framework, Question, Requirement


def make_framework() -> Framework:
    return Framework.objects.create(
        code="TEST",
        name="Test framework",
        version="1",
        source_url="https://example.com/framework",
    )


def make_question(code: str = "Q-1", weight: int = 1, requirement=None) -> Question:
    if requirement is None:
        requirement = Requirement.objects.create(
            framework=make_framework(),
            code="DIM",
            title="Dimension",
            description="Test dimension",
            sort_order=1,
        )
    return Question.objects.create(
        requirement=requirement,
        code=code,
        text=f"Question {code}?",
        guidance=f"Action for {code}",
        weight=weight,
    )


def make_assessment() -> Assessment:
    return Assessment.objects.create(
        organisation_name="Example SME",
        system_name="Decision support system",
        intended_purpose="Help trained staff prioritise maintenance reviews.",
        lifecycle_stage=Assessment.LifecycleStage.DEVELOPMENT,
        organisation_role=Assessment.OrganisationRole.PROVIDER,
    )
