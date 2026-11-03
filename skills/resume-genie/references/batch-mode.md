# Batch mode

Use batch mode when the user wants several roles handled together ("tailor my CV for these 10 jobs", "find me roles and prepare the CVs"). It reuses the single-job workflow for each role and adds gating, filing and tracking. The non-negotiable rules in SKILL.md apply to every role.

## Settings (ask once, then reuse)

Ask in one message for anything not already known, and save it in `batch.json` under `settings`:

| Setting | Default | Meaning |
|---|---|---|
| `output_dir` | `Resume Genie CVs` | Where company folders are created |
| `candidate` | the name on the CV | Used in file names |
| `fit_threshold` | 70 | Roles below this fit score are skipped |
| `ats_target` | 80 | A tailored CV below this is not delivered |
| `batch_size` | 10 | Roles per table |

Target salary per country is optional. If the user gives one, flag roles whose evidence sits below it; never change the evidence to meet it.

## Where roles come from

- **Best:** links or adverts the user pastes.
- **Search:** if asked to find roles, use web search on public job boards and company career pages, with the user's titles, locations and seniority.
- **Never** scrape sites that forbid automated access (LinkedIn's terms, for example). If a page can't be read, ask the user to paste the advert.
- Read each advert in full before scoring it. A search snippet is not an advert.

## The loop

For each role, in order:

1. **Fit check** exactly as in Stage 1: requirements, keywords, calculated score. Record `fit` and `ats_before`.
2. Write `batch.json` with every role, then gate:
   ```bash
   python scripts/batch_tracker.py check batch.json
   ```
   Skipped roles keep their reason. Duplicate adverts (the same role and place from different advertisers) are flagged; tell the user and keep only one.
3. For each ready role, **tailor the CV** as in Stage 2a, then run `check_fabrication.py` and `ats_score.py --compare`. Record `ats_after`, `audit` (`clean` only if the audit passes) and `placeholders`.
4. **Salary** for each ready role, using the rules in "Salary benchmark": the advert's range if stated, otherwise up to 3 cited sources (`name`, `url`, `range`). An `ask` with no advert range and no cited source is cleared by the script. Never invent figures.
5. Run `check` again (the ATS and audit gates now apply), then file and build:
   ```bash
   python scripts/batch_tracker.py folders batch.json
   python scripts/build_docx.py output.json --outdir "<company folder>"   # one build per role, renamed to files.docx
   python scripts/batch_tracker.py pdf batch.json                         # if LibreOffice is available
   python scripts/batch_tracker.py table batch.json
   ```

## Reply

The table from `batch_tracker.py table`, then at most five short bullets:
- gaps that will come up at interview, per role, one line each
- duplicates and anything below the user's salary target
- on-site, relocation or sponsorship conditions stated in the advert

End with: "Tell me which roles you've applied to, and any you've decided not to apply for, and I'll start the next batch."

## Applying and the next batch

- **Never submit an application for the user.** Give the apply link; the user applies.
- When the user confirms, run `batch_tracker.py applied batch.json all` (or the numbers they name).
- The user may decide not to apply for a role, for reasons of their own. Don't argue or ask why; record it with `batch_tracker.py declined batch.json N ["reason"]` (a reason only if they give one). Declined roles never come back in later batches.
- Start the next batch only when `batch_tracker.py next batch.json` exits 0: every ready role is applied or declined.
- If a role reaches interview, save the interview prep in that company's folder.
