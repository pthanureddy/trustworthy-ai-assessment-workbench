# Assessment methodology

## Purpose

The workflow helps a team discover and organise Trustworthy AI readiness work. It does not decide whether a system is legally compliant. Assessment conclusions depend on the system's role, risk classification, context, sectoral law, evidence quality, and qualified interpretation.

## Question design

The sample catalogue contains original questions grouped under the seven requirements presented by the European Commission's ALTAI material:

1. human agency and oversight;
2. technical robustness and safety;
3. privacy and data governance;
4. transparency;
5. diversity, non-discrimination and fairness;
6. societal and environmental well-being;
7. accountability.

Selected questions link to relevant EU AI Act provisions to demonstrate many-to-many traceability. A mapping means "review this source when evaluating the question", not "a Yes answer proves compliance".

## Answer semantics

- `Yes`: the described practice is implemented and the rationale should point to reviewable evidence.
- `Partly`: some elements exist, but scope, evidence, operation, or coverage is incomplete.
- `No`: the practice is missing or not yet implemented.
- `Not applicable`: the team records a justified scope decision; the item is excluded from the readiness denominator.

For applicable answers, rationale is mandatory. Evidence references can be document identifiers, issue links, test-report identifiers, model-card sections, or other locators appropriate to the organisation.

## Indicators

Coverage and readiness answer different questions:

- `coverage = answered active questions / all active questions`;
- `readiness = weighted answer value / applicable question weight`, where Yes = 1, Partly = 0.5, and No = 0.

The configured weight (1-5) expresses relative attention within this starter catalogue. The readiness result is an internal prioritisation signal only. It must not be presented as conformity, certification, residual-risk acceptance, or legal advice.

## Actions and review

Every `No` response produces a high-priority action, and every `Partly` response produces a medium-priority action. The question guidance supplies the action text; the response may add an owner and target date. Real deployments should support edited action statements, dependencies, approval, residual-risk decisions, and links to delivery systems.

The state machine separates authoring from review:

```text
Draft <-> In review <-> Completed
```

Completed records can be reopened when the system, deployment context, regulation, evidence, incident history, or catalogue changes.

## Interpretation safeguards

- Review the rationale and evidence, not only the numeric indicator.
- Treat unanswered and unjustified not-applicable items as review findings.
- Involve technical, policy, legal, security, data-protection, domain, accessibility, and affected-stakeholder perspectives as appropriate.
- Record disagreements and decisions; avoid forcing false consensus into a single answer.
- Reassess after material model, data, interface, use, organisational, regulatory, or incident changes.
