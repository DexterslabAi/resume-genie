# Changelog

## 1.1.0 (2026-10-27)

- Staged workflow in `resume-genie`: a job advert now gets a fit check only (one-line calculated ATS score plus a gap table), followed by a menu to rewrite the CV, write a cover letter or prepare for the interview. Finished steps are marked done and leave the menu. Most adverts need only the fit check, which cuts tokens substantially.
- `output-schema.json` requires only `analysis`; each stage adds its own part.
- `build_docx.py` builds only what a stage produced (CV, letter or both) and takes `--name` for letter-only builds.

## 1.0.0 (2026-10-27)

First public release.

- Eight skills: `resume-genie` (end-to-end orchestrator), `job-match-analyzer`, `ats-score`, `cv-tailor`, `cover-letter-writer`, `interview-prep-coach`, `regional-cv-formats`, `finance-transformation-cv`.
- Deterministic ATS scoring (weighted keyword coverage with synonyms, plus format hygiene).
- Fabrication guardrail with adversarial evaluation in CI.
- JSON output contract with a dependency-free validator.
- Word export in four templates (Classic, Modern, Executive, Compact) and eight regional formats, including photo, visa status, personal details, declaration and signature.
- Lint, sync, test, evaluation and packaging tooling; skill zips attached to tagged releases.
