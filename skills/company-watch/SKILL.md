---
name: company-watch
description: Builds and monitors a watchlist of companies that use the applicant's main stack (e.g., Berlin startups using Django), records each company's careers page and applicant tracking system, and checks their live job feeds for new matching openings. Triggered by requests like "Find Berlin startups that use Django", "Add companies to my watchlist", "Check my watchlist companies for new jobs", or "Are there new openings at the companies I follow?".
---

# Company Watch

Instead of searching job boards for postings, this skill keeps a list of companies whose stack matches the applicant, then reads each company's own job feed. Postings returned by an applicant tracking system (ATS) feed are live by construction, so stale and expired listings from aggregators are avoided.

The skill has two modes:
- **Build mode**: create or extend the watchlist (research-heavy, run occasionally).
- **Check mode**: fetch current openings for every watchlist company (fast, run often).

If the request does not say which mode, run Check mode when a watchlist exists and Build mode otherwise.

## Language Policy

- Write report prose in the user's request language. Keep field labels, table headers, company names, job titles, technical terms, and URLs in their original form.

## Files

All files are personal data and live under `results/company-watch/`:

- `results/company-watch/watchlist.md`: the watchlist (format below). Edit it in place; do not create dated copies.
- `results/company-watch/seen.json`: posting URLs already reported, with the date first seen. Maintained by the script.
- `results/company-watch/[YYYY-MM-DD]_openings.md`: Check mode reports. If the file exists, append `_HHMMSS`.
- `results/company-watch/[YYYY-MM-DD]_discovery.md`: discovery script reports from Build mode. Same suffix rule.

### Watchlist Format

```markdown
---
title: Company Watchlist - [Stack] [City]
updated: [YYYY-MM-DD]
category: company-watch
---

# Company Watchlist - Django, Berlin

| Company | Django Evidence | Evidence Date | Careers URL | ATS | ATS Slug | Status | Notes |
|---------|-----------------|---------------|-------------|-----|----------|--------|-------|
| Example GmbH | https://example.com/blog/our-django-stack | 2026-09 | https://example.com/careers | personio | example | watch | Fintech, ~80 people |
```

- **Django Evidence**: a URL showing the company uses Django (job posting, engineering blog, GitHub repository, conference talk, StackShare). Required.
- **Evidence Date**: month of the evidence (`YYYY-MM`), or `Unknown`. Evidence older than 2 years is weak; note it in `Notes`.
- **ATS**: `greenhouse`, `lever`, `ashby`, `personio`, `join`, `workable`, `smartrecruiters`, or `other`. The script reads all but `other`, which is listed for manual checks.
- **ATS Slug**: the company identifier in the ATS feed URL (see the table below). Empty for `other`.
- **Status**: `watch`, `applied`, `rejected`, or `excluded`. The script skips `excluded` and labels `applied`/`rejected` companies in the report.

Below the watchlist, an **Excluded Leads** table records discovery candidates that were checked and rejected, so they are not triaged again. It is separate from the watchlist because these companies have no Django evidence (or are recruiters), and `check_watchlist.py` reads only the first table:

```markdown
## Excluded Leads

| Company | Lead URL | Checked | Reason |
|---------|----------|---------|--------|
| Example Recruiting GmbH | https://www.linkedin.com/jobs/view/... | 2026-10-14 | Recruiter |
```

Use `excluded` rows in the watchlist itself only for companies that do use Django but are excluded for another reason (no Berlin roles, salary below floor, gambling).

## Build Mode

### 1. Read Resume and Targets

- Read the applicant's resume (default: the Markdown file in `resumes/`).
- Use the stack and city from the user's request. If not given, use the resume's main framework and current city.
- Read the existing watchlist, if any, so new rows extend it instead of duplicating companies.

### 2. Find Candidate Companies

Collect companies located in the target city (or with an office there) that use the target stack.

**Start with the discovery script.** It searches the job boards for the stack keyword and lists the hiring companies that are not on the watchlist yet:

```bash
python3 skills/company-watch/scripts/discover_companies.py --keyword django --city Berlin \
  --watchlist results/company-watch/watchlist.md \
  -o results/company-watch/[YYYY-MM-DD]_discovery.md
```

- Sources: LinkedIn public guest search (5 pages of 10 by default, `--linkedin-pages`), StepStone, XING, WeAreDevelopers, and the Arbeitnow API. Indeed, Berlin Startup Jobs, and GermanTechJobs block automated access and are not searched.
- Company names are compared without legal suffixes, spacing, or punctuation, and watchlist names in parentheses count as aliases (`Salfy (SalLab GmbH)` matches `SalLab GmbH`). Companies in the watchlist (any status) or in `Excluded Leads` are listed under `Already on the Watchlist`.
- Exit code 1 means a source failed (listed under `Source errors`); the other sources' results are still valid. LinkedIn may rate-limit (HTTP 429); re-run later if it does.
- Every candidate is a lead, not evidence. Boards match the keyword anywhere in a posting, so many hits use the stack only as a nice-to-have or are recruiters. Triage candidates with several postings or the keyword in a job title first.
- For each candidate, open a posting and check that the stack is a main backend framework. Then add the company to the watchlist (Step 3), or add it to `Excluded Leads` with a short reason (recruiter, consultancy, Django only optional, Django not in the posting, internship only). Board searches are fuzzy: LinkedIn and XING return many postings that never mention the keyword, so read the posting text before deciding. Both tables are compared on the next discovery run, so a rejected lead is not listed again.

Other useful sources when the script finds few candidates:

- `WebSearch` queries such as `"Django" "Berlin" startup engineer`, `site:join.com "Django" Berlin`, `site:jobs.personio.de "Django" Berlin`, `site:jobs.ashbyhq.com "Django" Berlin`.
- Earlier reports in `results/job-search-eu/`.
- Engineering blogs, GitHub organizations, StackShare, and Django conference talks (DjangoCon Europe, PyCon DE) by local companies.

Rules:
- Add a company only with a concrete evidence URL that appeared in current-session tool output. Never add a company from memory or because it "probably" uses the stack.
- A posting that lists the stack only as one of many "nice to have" items is weak evidence; prefer postings, blogs, or repositories where it is the main backend framework.
- Skip agencies and recruiting firms unless they hire for their own product.
- Respect the applicant's exclusions: mark companies they already applied to or were rejected by as `applied` or `rejected`, and companies they do not want (e.g., gambling) as `excluded`.

### 3. Identify the Careers Page and ATS

For each company, open its careers page and look at where job links point:

| ATS | Job link pattern | Slug | Feed the script reads |
| :--- | :--- | :--- | :--- |
| Greenhouse | `boards.greenhouse.io/{slug}`, `job-boards.greenhouse.io/{slug}`, `?gh_jid=` | `{slug}` | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` |
| Lever | `jobs.lever.co/{slug}` | `{slug}` | `https://api.lever.co/v0/postings/{slug}?mode=json` |
| Ashby | `jobs.ashbyhq.com/{slug}` | `{slug}` | `https://api.ashbyhq.com/posting-api/job-board/{slug}` |
| Personio | `{slug}.jobs.personio.de` or `.com` | `{slug}` | `https://{slug}.jobs.personio.de/xml` |
| JOIN | `join.com/companies/{slug}` | `{slug}` | `https://join.com/companies/{slug}` |
| Workable | `apply.workable.com/{slug}` | `{slug}` | `https://apply.workable.com/api/v1/widget/accounts/{slug}` |
| SmartRecruiters | `jobs.smartrecruiters.com/{slug}` | `{slug}` (case-sensitive) | `https://api.smartrecruiters.com/v1/companies/{slug}/postings` |

- Take the slug from a link seen on the careers page or in search results. Never guess a slug from the company name.
- Confirm the slug by fetching its feed once: it must return HTTP 200 and list jobs for the same company (an empty list is acceptable if the company name matches the board). If it fails, set `ATS` to `other` and keep the careers URL.
- Teamtailor, Recruitee, d.vinci, rexx, email-only, and custom pages are `other`. Record a public feed URL in `Notes` if one exists (e.g., d.vinci `jobPublication/list.json`).
- Greenhouse boards hosted on `job-boards.eu.greenhouse.io` still use the `boards-api.greenhouse.io` feed.

### 4. Save

- Update `results/company-watch/watchlist.md` in place and set `updated` in the frontmatter.
- Sort rows by company name.
- In the chat summary, report how many companies were added, how many have a script-readable ATS, and which need manual checks.

## Check Mode

### 1. Run the Script

```bash
python3 skills/company-watch/scripts/check_watchlist.py results/company-watch/watchlist.md \
  --state results/company-watch/seen.json \
  -o results/company-watch/[YYYY-MM-DD]_openings.md
```

- Default filters keep engineering titles (`engineer`, `developer`, `entwickler`, `programmer`) and drop internships, mobile, frontend, hardware, electrical/production, C++/Qt, and sales/support engineering titles. Locations must mention Berlin; remote postings (`remote`, `homeoffice`, `home office`) must also name Europe, the EU, EMEA, Germany, Berlin, or CET, so on-site roles in other German cities are dropped. Postings without a location are kept.
- Override with `--keywords`, `--exclude`, `--location`, and `--remote-regions` when the user asks for something else (e.g., `--location munich,germany`).
- Postings not yet in `seen.json` are marked `NEW`; the state file is updated after each run.
- Exit code 1 means at least one feed failed (listed under `Fetch Errors`). Check whether the slug changed, fix the watchlist, and re-run. Other companies' results are still valid.

### 2. Review the Openings

- Focus on `NEW` postings. For each one, open the posting URL and judge suitability against the resume as in `job-search-eu` Step 4 (High / Medium / Low).
- An ATS feed listing is positive evidence that the posting is published. Still open the posting and confirm it is not marked closed before recommending it.
- For `Manual Check Needed` companies, open the careers URL and look for matching roles. Apply the `job-search-eu` application-status check (Step 3-D) to anything you recommend from these pages.
- Do not recommend postings at `applied` or `rejected` companies without saying so.

### 3. Report

Append a short review section to the script's report file:

```markdown
## Review

| Company | Title | Suitability | Why |
|---------|-------|-------------|-----|
| Example GmbH | Senior Backend Engineer | High | Django/DRF, PostgreSQL, AWS match; German not required |
```

In the chat summary, list the High and Medium `NEW` postings with their URLs, then fetch errors and manual checks still pending.

## Core Rules

- **Evidence or nothing.** Every watchlist company needs a stack evidence URL from current-session tool output. Never invent companies, evidence, careers URLs, or ATS slugs.
- **Never guess ATS slugs.** Take them from observed links and confirm them against the feed.
- **Feeds over aggregators.** In Check mode, use ATS feeds and careers pages, not job-board search results.
- **Keep the watchlist current.** Update rows in place; mark companies as `excluded` rather than deleting them, so they are not re-added later.
- **Be honest about coverage.** The watchlist is never "all" companies using the stack; it is the companies with public evidence found so far.
