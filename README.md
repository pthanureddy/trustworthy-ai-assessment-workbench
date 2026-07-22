# Trustworthy AI Assessment Workbench

A Django application for running evidence-based Trustworthy AI self-assessments. It turns versioned questionnaire content into a reviewable workflow: teams describe an AI system, answer structured questions, attach rationale and evidence references, review coverage by dimension, assign follow-up work, and export a machine-readable report.

The included starter content uses original questions organised around the European Commission's seven ALTAI requirements and maps them to selected provisions of Regulation (EU) 2024/1689 (the EU AI Act). It is a software-engineering example, not an official ALTAI implementation, conformity assessment, or legal opinion.

## Why this project exists

Trustworthy AI guidance is often distributed across long documents, while small organisations need a repeatable process with explicit ownership and review records. This workbench demonstrates how to separate:

- versioned assessment content from application code;
- principle-level dimensions from regulatory references;
- working answers from reviewed assessment states;
- a readiness indicator from a legal compliance conclusion.

## Implemented capabilities

- Django models for frameworks, dimensions, questions, regulatory references, assessments, responses, and audit events
- JSON-managed seed content with 7 dimensions, 21 original questions, and question-to-article mappings
- contextual answers with rationale, evidence reference, action owner, and target date
- weighted readiness and completion coverage calculated separately
- deterministic action generation for `No` and `Partly` responses
- `Draft -> In review -> Completed` workflow with guarded transitions and audit events
- JSON report export with source mappings and an explicit non-compliance disclaimer
- responsive server-rendered interface, CSRF protection, validation, and Django admin content management
- automated tests, coverage threshold, Ruff checks, deployment checks, Docker, and GitHub Actions CI

## Architecture

```text
data/framework.json
        |
        v
seed_framework command ---> Framework / Requirement / Question / Reference
                                      |
                                      v
Browser ---> Django views/forms ---> Assessment / Response ---> scoring + actions
                                                     |               |
                                                     v               v
                                               audit events     JSON report
```

The application intentionally keeps scoring in a service module rather than model methods or templates. This makes policy choices testable and allows the question catalogue to evolve independently. See [Architecture](docs/architecture.md) and [Assessment methodology](docs/methodology.md).

## Local setup

Requires Python 3.11 or later.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python manage.py migrate
python manage.py seed_framework
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

To use the admin interface, create a local account with `python manage.py createsuperuser`, then open `/admin/`.

## Verification

```bash
ruff check .
python manage.py makemigrations --check --dry-run
coverage run manage.py test
coverage report
python manage.py check
```

The CI workflow repeats lint, migration, seed, test, coverage, and deployment-oriented checks on every push and pull request.

## Docker

```bash
docker compose up --build
```

The Compose command applies migrations, loads the content catalogue idempotently, and starts the development server on port 8000.

## Content update workflow

1. Create a new framework version instead of silently changing the meaning of a completed assessment.
2. Write questions in plain language and make the requested evidence or decision explicit.
3. Map each question to principle-level and regulatory sources separately.
4. Review content with technical, policy, legal, domain, and affected-stakeholder perspectives.
5. Test seed idempotence, ordering, mappings, scoring, and export output.
6. Record release notes and reassessment triggers.

See [Content governance](docs/content-governance.md) for the review checklist.

## Source material

- [European Commission - Assessment List for Trustworthy Artificial Intelligence (ALTAI) for self-assessment](https://digital-strategy.ec.europa.eu/en/library/assessment-list-trustworthy-artificial-intelligence-altai-self-assessment)
- [EUR-Lex - Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [European Commission - AI Act overview and application timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

These sources are references for the content model. The repository does not reproduce the ALTAI questionnaire text. Regulatory mappings are illustrative and require qualified review for a real organisation and use case.

## Limitations

- The included catalogue is deliberately small and does not cover every AI Act role, risk classification, obligation, standard, sectoral rule, or national requirement.
- The readiness indicator reflects answers to configured questions; it is not a probability, certification result, or compliance score.
- Authentication and organisation-level permissions are not implemented in this portfolio version.
- Evidence is referenced as text; production use would need protected document storage, access control, retention rules, and integrity controls.
- SQLite and Django's development server are used for local demonstration. Production deployment requires a supported database, secrets management, HTTPS, backups, monitoring, and security review.

## License

MIT. The regulatory and guidance materials linked above remain subject to their respective terms.
