---
name: job-match-analyzer
description: Honestly assess how well a CV matches a job advert before applying. Gives a fit score and verdict (apply, stretch or skip), each requirement as met, partial or missing with evidence, gaps with advice, red flags in the advert, and a calculated ATS keyword score. Use when the user asks "should I apply?", "am I a good fit?" or wants a CV-versus-job comparison without a rewrite.
---

# Job match analyzer

Tell the candidate the truth about their fit, with evidence, before they spend time on an application.

## Workflow

1. Extract the text of the CV and the job advert. Save the CV as `cv.txt`.
2. Follow `references/job-analysis.md`:
   - **Read the advert in layers:** must-haves, nice-to-haves, the real job (the duties) and signals.
   - **Judge each requirement:** `met` (direct evidence, quoted), `partial` (adjacent or implied) or `missing`. Never mark something met because it's plausible.
   - **Fit score and verdict:**
     - `strong-apply` (85+)
     - `apply` (65–84)
     - `stretch` (45–64)
     - `skip` (below 45, or a hard gate is missing)
   - **Gaps,** each with advice: surface hidden evidence, address it in the cover letter, or close it.
   - **Red flags,** pointed out kindly.
3. Pick 15–30 ATS keywords in the advert's exact wording, with `importance` and `synonyms`. Save them as `keywords.json`, then calculate the current ATS score:
   ```bash
   python scripts/ats_score.py cv.txt keywords.json
   ```
4. Reply with:
   - the verdict and fit score, plus a one-line reason
   - the ATS score as calculated
   - a requirements table (requirement | status | evidence)
   - the top strengths to lead with
   - gaps with advice
   - red flags
   - 4–6 specific tailoring moves

   If the user wants the tailored CV next, hand over to the `cv-tailor` or `resume-genie` skill.

## Rules

- Quote evidence from the CV. Don't paraphrase it into something stronger.
- A missing hard gate (licence, clearance, mandated degree or language) caps the verdict at `skip`, however strong the rest is.
- Report scores as calculated. Never estimate an ATS score.
