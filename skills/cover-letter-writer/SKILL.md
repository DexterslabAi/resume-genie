---
name: cover-letter-writer
description: Write a short, specific cover letter for one job from the candidate's real CV. It opens with a relevant result, maps evidence to the advert's top needs, handles the main gap honestly and avoids clichés, exported as a Word file. Use when the user asks for a cover letter, application letter or motivation letter.
---

# Cover letter writer

A letter that sounds like a capable person, not a template. Follow `references/cover-letter.md`.

## Shape (250–350 words)

1. **Hook:** the candidate's most relevant result, or a specific link to the company's work. Name the role. Never open with "I am writing to apply" or "I am excited to".
2. **Proof:** 2–3 pieces of evidence mapped to the advert's top needs, with concrete facts and numbers from the CV.
3. **The gap, handled honestly:** name it briefly and show the nearest evidence or a plan. If there's no significant gap, use this paragraph for why this company.
4. **Close:** one or two sentences about what they'd like to discuss, and thanks.

## Workflow

1. Read the CV and the advert. If an analysis exists in this conversation, reuse its strengths and gaps.
2. Write the letter in plain, confident sentences, mirroring 2–3 of the advert's key terms naturally. Use the hiring manager's name only if the advert gives it; otherwise "Dear Hiring Manager,".
3. Save it as `output.json`, with at least `cv.name` and `cover_letter` (see `references/output-schema.json`). Then build it:
   ```bash
   python scripts/build_docx.py output.json --template classic
   ```
4. Reply with:
   - the letter text
   - the file
   - a short "before you send" list: what to personalise or check

## Rules

- Only facts from the CV or the user. No invented numbers.
- No "passionate", "dynamic", "synergy" or "leverage".
