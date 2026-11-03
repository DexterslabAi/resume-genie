# Changelog

## 1.2.1 (2026-11-03)

- **Decline a role.** Users can mark a role they've chosen not to apply for: `batch_tracker.py declined batch.json N ["reason"]`. Declined roles count as done, are never reopened, and show in the summary with applied and still-to-decide counts. The next batch starts once every ready role is applied or declined.
- **Cleaner page breaks in Word CVs.** No empty line under an entry without a company or location (a career break, say). A role's heading always stays on the same page as its first bullet, short entries (three bullets or fewer) stay together, and bullets never split across pages.
- 4 new tests (50 in total).

## 1.2.0 (2026-11-02)

- **Batch mode** in `resume-genie`: handle several roles in one go. Each role gets the usual fit check, tailored CV and fabrication audit, then `batch_tracker.py` takes over the parts that must be exact.
- Gates every role on the user's own settings: fit threshold (default 70), ATS target after tailoring (default 80) and a clean audit. Skipped roles keep their reason.
- Flags likely duplicate adverts (the same role and location from different advertisers).
- Clears any salary "ask" that has no advert range or cited source behind it.
- Creates one folder per company with consistent file names, converts CVs to PDF when LibreOffice is available, and prints one summary table with apply links, Word and PDF links, salary and flags.
- Tracks applications: the next batch starts only after the user confirms they've applied. Resume Genie never submits an application itself.
- New reference `batch-mode.md`, covering settings, job sources (pasted links or public job boards; no scraping of sites that forbid it) and the reply format.
- 11 new unit tests (46 in total).

## 1.1.0 (2026-10-27)

- Staged workflow in `resume-genie`: a job advert now gets a fit check only (one-line calculated ATS score plus a gap table), followed by a menu to rewrite the CV, write a cover letter or prepare for the interview. Finished steps are marked done and leave the menu. Most adverts need only the fit check, which cuts tokens substantially.
- The menu shows Claude-orange buttons where the app can render them (done steps greyed out), then the app's own choices, then a numbered list.
- Salary benchmark on request only: the advert's own range with a suggested ask, or a table of the top 3 sources and a one-line verdict.
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
