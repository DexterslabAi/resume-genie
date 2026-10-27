---
name: ats-score
description: Calculate a transparent, reproducible ATS (applicant tracking system) score for a CV against a job advert. It uses weighted keyword coverage with synonyms plus format checks, computed by a script rather than guessed, and lists the required keywords that are missing. Use when the user asks for an ATS score, keyword match or "will my CV get through the ATS?".
---

# ATS score

Most AI tools guess an ATS score. This skill **calculates** one, so the same CV and advert always give the same number, and the user can see exactly why.

## How the score works

- **Keyword coverage (75%).** Required keywords count double. Plurals, simple stems and listed synonyms match (for example "purchase-to-pay" counts for "P2P"). Matching is literal, like a recruiter's ATS search.
- **Format hygiene (25%).** The CV is checked for:
  - an email address and a phone number
  - standard Summary, Skills, Experience and Education headings
  - length between 350 and 1,100 words
  - at least 40% of bullets quantified
  - no unusual characters

## Workflow

1. Save the CV text as `cv.txt`.
2. Read the advert and choose 15–30 keywords, following the keyword section of `references/job-analysis.md`:
   - use the advert's exact wording, including the job title
   - mark terms `required` if they sit under a requirements heading or are repeated in the duties
   - add synonyms: the acronym and its expansion, plus spelling variants
3. Save the keywords as `keywords.json`:
   ```json
   [{"term": "P2P", "importance": "required", "synonyms": ["procure-to-pay", "purchase-to-pay"]}]
   ```
4. Run:
   ```bash
   python scripts/ats_score.py cv.txt keywords.json
   ```
5. Report:
   - the score, the keyword score and the format score
   - matched keywords
   - missing keywords, required ones first
   - failed format checks

   For each missing required keyword, say honestly whether the CV shows evidence for it elsewhere (then use the advert's wording) or whether it's a real gap.

## Rules

- Never estimate or round a score yourself. Report what the script prints.
- Never advise adding a keyword the candidate can't back up in an interview.
