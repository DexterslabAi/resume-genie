---
name: cv-tailor
description: Rewrite a CV for one specific job while keeping it 100% truthful. Uses the advert's language, achievement-focused bullets and placeholders instead of invented numbers, and runs an automated fabrication check before delivering a Word file in a chosen template and regional format. Use when the user asks to tailor, rewrite, improve or optimise their CV or resume for a role.
---

# CV tailor

Tailoring is editing, not inventing. Choose, order and reword the candidate's real experience for this one job.

## Workflow

1. Extract the CV text and save it as `original_cv.txt`. Read the job advert.
2. Work out what matters: must-haves, duties, keywords. If the `job-match-analyzer` skill has already run in this conversation, reuse its analysis.
3. Rewrite, following `references/cv-writing.md`, the relevant section of `references/career-tracks.md`, and the region in `references/regions.md` (default UK & Ireland):
   - **Headline:** the target role plus 2–3 of the candidate's strongest relevant themes.
   - **Summary:** 3–4 specific sentences with signature results. No "results-driven".
   - **Skills:** 2–4 labelled groups, using the advert's terms where true.
   - **Experience:** keep every role and date. Put the most relevant bullets first. Each bullet is: strong verb + what + how/scale + result.
   - **Numbers:** only the user's own. Otherwise use `[placeholders]` with `needs_confirmation: true`.
   - **Log every change** with the reason it helps.
4. Save the result as `output.json` following `references/output-schema.json`. The `analysis` needs at least the keywords, and `cover_letter` may be minimal if not requested.
5. Verify, and fix the output until the fabrication check is clean:
   ```bash
   python scripts/check_fabrication.py original_cv.txt output.json
   python scripts/ats_score.py --compare original_cv.txt output.json
   ```
6. Build the Word file in the chosen template (`classic`, `modern`, `executive` or `compact`):
   ```bash
   python scripts/build_docx.py output.json --template classic --page a4
   ```
7. Reply with:
   - the ATS score before → after
   - the most important changes and why
   - the placeholders to fill in
   - the file

## Rules

- Never invent or upgrade employers, titles, dates, tools, qualifications or results.
- Never deliver a CV that fails `check_fabrication.py`.
- Keep layouts ATS-safe: one column, standard headings, contact details in the body.
