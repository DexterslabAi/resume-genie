---
name: regional-cv-formats
description: Convert or check a CV against country conventions. Covers UK and Ireland, US, Canada, Australia and NZ, Europe, Germany/Austria/Switzerland, UAE and the Gulf, and India, including paper size, spelling, photo, visa status, personal details, declaration and signature. Use when the user is applying in another country or asks for a UAE, Gulf, German, Indian, US or Europass-style CV.
---

# Regional CV formats

The same CV can be right in Dublin and wrong in Dubai. Follow `references/regions.md`.

## Workflow

1. Identify the target region from the job location or the user's request.
2. Check the CV against that region's rules:
   - paper size and spelling
   - photo: expected, optional or not used
   - which personal details belong (and which must be removed, for example date of birth in the US or UK)
   - visa or right-to-work line
   - languages with levels
   - declaration or signature
3. Ask the user for any personal details the region expects that they haven't given: visa status, nationality, photo, languages with levels, notice period. Never invent them.
4. Rebuild the CV as Word in the right format. If there's no structured `output.json` yet, convert the CV into one first (see `references/output-schema.json`), changing no facts. Examples:
   ```bash
   # UAE: photo and visa status expected
   python scripts/build_docx.py output.json --page a4 --photo photo.jpg --header "Visa status: Employment visa (transferable)" --detail "Nationality=Indian" --detail "Notice period=30 days" --languages "English (C2), Arabic (A2)"
   # Germany: CEFR languages, place, date and signature
   python scripts/build_docx.py output.json --page a4 --languages "German (B2), English (C1)" --signature --place Berlin
   # India: personal details and declaration
   python scripts/build_docx.py output.json --page a4 --detail "Date of birth=..." --declaration --place Bengaluru
   # US: Letter paper, no photo or personal details
   python scripts/build_docx.py output.json --page letter
   ```
5. Reply with:
   - what changed for this region and why
   - anything removed for legal or convention reasons
   - the file
