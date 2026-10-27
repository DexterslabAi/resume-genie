# Regional CV formats

Pick the region from the job's location (default: UK & Ireland). Personal details are always typed by the candidate: never invent them. If a region expects one that's missing, ask once or leave a placeholder such as `[Visa status]`.

| Region | Call it | Paper | Photo | Spelling |
|---|---|---|---|---|
| UK & Ireland | CV | A4 | No | British |
| United States | resume | Letter | No | American |
| Canada | resume | Letter | No | Canadian (colour, centre, -ize) |
| Australia & New Zealand | resume | A4 | No | British-style |
| Europe (general) | CV | A4 | Optional | British unless the advert is in American English |
| Germany, Austria & Switzerland | CV (Lebenslauf) | A4 | Optional, common | as the advert |
| UAE & Gulf (GCC) | CV | A4 | Expected | British |
| India | resume | A4 | Optional, common | Indian English (British-style) |

## Region details

**UK & Ireland.** No photo, date of birth, marital status, gender or nationality. Two pages is normal for experienced candidates. If right to work needs stating, keep it to one header line (for example "Right to work: Stamp 4, full right to work in Ireland").

**United States.** No photo or personal details beyond contact information; US employers avoid them for anti-discrimination reasons. One page under ten years of experience, two pages otherwise.

**Canada.** As the US, with Canadian spelling. Mention English and French proficiency if relevant.

**Australia & New Zealand.** No photo or personal details. Two to three pages is fine for experienced candidates. State work rights or visa status clearly if the candidate is not a citizen or resident.

**Europe (general).** A photo is optional and varies by country. List languages with CEFR levels (A1–C2). Nationality and work authorisation if relevant.

**Germany, Austria & Switzerland.** Reverse chronological order with dates as MM/YYYY. A professional photo is common but optional. Date of birth and nationality are optional. Languages with CEFR levels (German B2, English C1). One to two pages. Traditionally ends with place, date and a signature line (`--signature --place <city>` in build_docx.py).

**UAE & Gulf (GCC).**
- A professional passport-style photo is expected for most private-sector roles (`--photo`).
- Visa status must be precise and sit near the top as a header line, for example `--header "Visa status: Employment visa (transferable)"`.
- Nationality is normally included; date of birth is optional.
- List languages with proficiency, highlighting English and Arabic.
- Driving licence and notice period if the candidate gives them.
- Flag UAE or GCC experience clearly.
- Two pages maximum, simple ATS-friendly layout.

**India.**
- A professional photo is often expected.
- A Personal Details section near the end (date of birth, gender, marital status, nationality, languages, willingness to relocate), only as the candidate provides.
- Many established and government-related employers expect a closing declaration with place and date (`--declaration --place <city>`).
- Two pages is normal.

## Personal detail fields by region

| Field | Where it goes | Regions |
|---|---|---|
| Visa status / right to work | Header line | UAE & GCC (visa); UK & Ireland, US, Canada, Australia & NZ, Europe, Germany (right to work, if needed) |
| Nationality | Personal Details | UAE & GCC, Europe, Germany, India |
| Date of birth | Personal Details | UAE & GCC (optional), Germany (optional), India |
| Gender, marital status | Personal Details | India only |
| Languages with levels | Languages section | UK & Ireland, Canada, Australia & NZ, Europe, Germany, UAE & GCC, India |
| Driving licence, notice period | Personal Details | UAE & GCC |
| Willing to relocate | Personal Details | India |
| Place (for signing) | Signature line | Germany, India |
