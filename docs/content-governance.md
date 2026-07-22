# Content governance

Assessment content is a maintained product dependency. Wording, mappings, weights, and workflow effects can change organisational decisions, so changes need review beyond ordinary copy editing.

## Roles

- Content owner: proposes scope, wording, version, and release notes.
- Technical reviewer: tests whether the requested practice and evidence are technically coherent.
- Policy or legal reviewer: checks regulatory interpretation and disclaimers.
- Domain reviewer: checks relevance to the actual sector and operating context.
- User reviewer: tests comprehension, accessibility, and actionability with intended users.

One person may hold multiple roles in a small team, but the review perspectives should remain explicit.

## Change checklist

For every new or changed question:

- state the decision or practice being assessed;
- keep one primary issue per question where practical;
- define plain-language guidance and expected evidence;
- assign a stable code and owning dimension;
- review all source mappings and distinguish binding law from guidance;
- document assumptions about provider, deployer, lifecycle, and risk class;
- check that answer options make sense and that `Not applicable` can be justified;
- review the effect of weight changes on historical interpretation;
- test keyboard use, screen width, errors, and non-specialist comprehension;
- add or update seed, scoring, workflow, and export tests;
- publish a new content version for material meaning changes.

## Versioning rules

- Patch: typo or formatting correction with no change in meaning.
- Minor: new questions or mappings that do not reinterpret existing answers.
- Major: changed semantics, scoring model, source scope, or answer interpretation.

Completed assessments should retain the catalogue version used. This portfolio version stores the framework version but does not yet snapshot each question revision; production use should implement immutable published catalogue versions.

## Source review cadence

Review sources at a scheduled interval and when official guidance, standards, corrigenda, delegated acts, or applicable law changes. Record the source URL, retrieval date, reviewer, decision, and affected content codes. Do not silently treat proposals or draft guidance as adopted obligations.
