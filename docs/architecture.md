# Architecture

## Context

The workbench supports a multidisciplinary review process. Policy specialists maintain assessment content and mappings; engineers and system owners answer technical questions; reviewers examine rationale and evidence; decision owners accept actions or residual gaps.

## Components

### Content catalogue

`data/framework.json` is the portable source for the sample catalogue. `seed_framework` applies it idempotently to four relational models:

- `Framework`: name, version, provenance, and scope note
- `Requirement`: ordered assessment dimension
- `Question`: stable code, text, guidance, weight, and lifecycle state
- `RegulatoryReference`: external reference that can map to multiple questions

Stable codes support review comments, exports, and future migrations without using question text as an identifier. Removed catalogue entries are deactivated instead of deleting historical references.

### Assessment records

`Assessment` stores organisational context, intended purpose, lifecycle stage, role, and review state. `Response` stores one contextual answer per assessment/question pair, enforced by a database constraint. It also carries rationale, an evidence locator, owner, and target date.

`AssessmentEvent` records status and answer events. The current event model is intentionally small; a production implementation should add authenticated actor identifiers and tamper-evident retention.

### Domain services

`services.py` contains deterministic policy logic:

- completion coverage counts answered active questions;
- the readiness indicator applies configured weights to `Yes`, `Partly`, and `No`, excluding `Not applicable`;
- action items are derived from `No` and `Partly` responses;
- state transitions are checked against an explicit transition map;
- report export assembles context, results, responses, mappings, and actions.

Separating this logic from templates and models makes calculation and workflow changes independently testable.

### Web interface

Django views and model forms provide server-rendered pages. CSRF middleware protects writes, form validation requires rationale for applicable answers, and workflow changes accept POST only. The Django admin provides a basic content-management surface.

## Data flow

1. A content maintainer updates the versioned JSON catalogue.
2. The seed command creates or updates the relational catalogue.
3. A user creates an assessment with system context.
4. Each answer is validated and stored with an audit event.
5. Services calculate coverage/readiness and derive open actions on read.
6. Reviewers move the assessment through guarded states.
7. JSON export provides a reviewable, machine-readable snapshot.

## Security and deployment boundary

The portfolio application enables standard Django protections but does not claim production readiness. Before real organisational use, add identity and access management, tenant isolation, protected evidence storage, audit actors, rate limiting, backup and recovery, privacy analysis, and operational monitoring. Replace SQLite and the development server with production services.
