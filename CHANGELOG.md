# Changelog

## 1.0.0 (2026-10-27)

First public release.

- Eight skills: `resume-genie` (end-to-end orchestrator), `job-match-analyzer`, `ats-score`, `cv-tailor`, `cover-letter-writer`, `interview-prep-coach`, `regional-cv-formats`, `finance-transformation-cv`.
- Deterministic ATS scoring (weighted keyword coverage with synonyms, plus format hygiene).
- Fabrication guardrail with adversarial evaluation in CI.
- JSON output contract with a dependency-free validator.
- Word export in four templates (Classic, Modern, Executive, Compact) and eight regional formats, including photo, visa status, personal details, declaration and signature.
- Lint, sync, test, evaluation and packaging tooling; skill zips attached to tagged releases.
