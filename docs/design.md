# Design notes

Why Resume Genie is built the way it is.

## 1. Split judgement from arithmetic

Language models are excellent at reading a job advert, judging fit and rewriting bullets. They're unreliable at anything that must be exact and repeatable. Resume Genie draws a hard line between the two:

| Done by Claude (judgement) | Done by scripts (exact) |
|---|---|
| Reading the advert, weighting requirements | ATS score: weighted keyword coverage plus format checks (`ats_score.py`) |
| Choosing keywords and synonyms | Checking the output against a schema (`validate_output.py`) |
| Rewriting the CV, letter and interview prep | Auditing for invented facts (`check_fabrication.py`) |
| Deciding region, track and template | Word layout in four templates and eight regional formats (`build_docx.py`) |

The model never states an ATS score; it runs the scorer and reports the number. The same CV and advert always give the same score, and the user can see exactly which keywords moved it.

## 2. A contract between the model and the code

The writing step produces one JSON document (`shared/references/output-schema.json`), and every script consumes that. This makes the output:
- **checkable:** schema validation catches a malformed reply before anything is built
- **re-usable:** "switch to the Modern template" or "make it US format" is a rebuild, not a rewrite
- **testable:** the evaluation suite works on saved outputs, with no model calls

## 3. Guardrails you can test

The biggest risk with AI CV tools is fabrication: an invented "increased revenue by 37%" that falls apart in an interview or a background check. Resume Genie handles it in three layers:

1. **Instruction:** never estimate a number. Write a `[placeholder]` and set `needs_confirmation`.
2. **Verification:** `check_fabrication.py` compares every number, employer and date in the tailored CV with the original CV and any facts the user supplied. Arithmetic on the user's own numbers is allowed (9 days to 4 days is "56% faster"); anything else is flagged. The skill must fix issues and re-run before delivering.
3. **Evaluation:** `evals/run_evals.py` injects fabrications into known-good outputs (an invented team size, an inflated percentage, invented revenue, a fake employer, shifted dates, an unflagged placeholder) and fails CI if the checker misses any. See [evals/RESULTS.md](../evals/RESULTS.md).

## 4. Progressive disclosure

Each `SKILL.md` is short: when to use it, the workflow and the rules. Detailed guidance lives in `references/` and is read only when a step needs it, so Claude's context stays focused. Scripts are run rather than read.

## 5. An orchestrator plus specialists

`resume-genie` runs the full pipeline. Seven specialist skills (match analysis, ATS score, CV tailoring, cover letter, interview prep, regional formats, finance transformation) handle narrower requests on their own. For example, "should I apply?" triggers `job-match-analyzer` without rewriting anything.

## 6. One source, self-contained skills

Every skill must work when installed alone, so each carries its own copy of the scripts and references it needs. The single source lives in `shared/`, `tools/manifest.json` maps it into skills, and `tools/sync_shared.py --check` fails CI if any copy drifts.

## 7. Regional formats as data

A CV that's right in Dublin is wrong in Dubai. Region rules (paper, spelling, photo, visa line, personal details, declaration, signature) live in one reference table. Personal details are always supplied by the candidate and passed to the builder as explicit flags. The model never generates them.

## 8. Portable, low-dependency tooling

The scripts need only Python 3.10+ and python-docx, both available in Claude's code execution environment. Tests use the standard library `unittest`, and the schema validator is a small dependency-free implementation of the JSON Schema keywords the contract uses.
