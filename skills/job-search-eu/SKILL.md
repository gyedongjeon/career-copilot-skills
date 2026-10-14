---
name: job-search-eu
description: Searches the web for the latest suitable job postings in Europe based on a resume and summarizes the results. Integrates searches across multiple EU job sites and general platforms. Triggered by requests like "Search for job postings in Europe", "Find postings that fit my resume in Germany", "Are there any positions for me lately in London?", or "Search backend jobs on LinkedIn for Europe".
---

# Job Search EU

Analyzes the resume, searches for suitable job postings, and recommends only roles whose application availability was verified during the current search.

## Language Policy

- Write the report body in the user's request language. Use English only when the user writes in English or explicitly asks for it.
- Keep template field labels and section labels exactly as defined in the Output Template (e.g., `Search Date`, `Detail URL`, `Match Points`). Do not translate them.
- Keep company names, position names, product names, technical terms, and URLs in their original form.
- Translate explanatory prose, including `Match Points`, `Gaps`, `Application Evidence`, exclusion reasons, and closing guidance.

## Workflow

### 1. Read Resume

- If a file path is given, read it using `Read`.
- If shared as text in the conversation, use it as is.
- If neither is provided, search the `resumes/` folder in the project for the applicant's resume (e.g., markdown files).
- If no resume can be found, request it from the user. When requesting, proactively guide them with the following tip: *"For future convenience, please save the applicant's resume as a markdown file named after them (e.g., `resumes/[Applicant Name].md`) inside the `resumes/` folder."*

### 2. Extract Search Criteria

Automatically extract the following information from the resume:

- **Core Skills**: Top 2-3 skills with the most experience (e.g., Python, Django, AWS)
- **Job Level**: Based on years of experience (e.g., Senior, Mid-level, Junior, Entry Level)
- **Job Type**: Based on job titles/roles in the resume (e.g., Backend Engineer, Software Engineer)
- **Location**: Utilize residence/visa info if present in the resume (e.g., Berlin, Germany)
- **Preferred Work Location**: A location explicitly listed as a job-search preference (e.g., `Preferred location: Berlin`). Treat it as the target scope, not just residence information.
- **Preferred Companies**: Companies the applicant explicitly lists as targets.
- **Language and Visa Constraints**: Working languages and work-permit status, if stated. Use them to judge requirements such as fluent German or visa sponsorship.

If the user specifies additional conditions (location, skills, role, specific site, etc.), apply those conditions with priority.

**Preferred location rule:**
- If a preferred work location exists, search only within it. For a city, keep postings in that city, its metro area, or remote/hybrid roles explicitly open to that city. Do not broaden to the whole country unless the user asks.
- When the preference contains both city and country (e.g., `Frankfurt, Germany`), use the city as `{city}` and the country as `{country}` for site selection.

**Early-career rule:**
- If the resume indicates internship or entry-level experience, also search internship, trainee, working-student, and entry-level roles. All other filters still apply.

### 3. Web Search

Use `WebSearch` for discovery and `WebFetch` (or an available browser, or `curl` via `Bash` where noted) to verify each shortlisted posting and its application destination.

**Default mode:** Run in **Fast mode** unless the user asks for deeper coverage. Fast mode limits discovery, not application-status verification; verification is mandatory in every mode.

**Time budget:**
- Start a wall-clock timer when web searching begins.
- Use a default total time budget of **10 minutes** for the full search workflow.
- If the 10-minute budget is reached, stop searching immediately and save only the **verified-open results collected so far**.
- Partial results are acceptable. Do not discard already validated postings just because fewer than 5 were found.
- A valid posting must be suitable, have a stable detail URL, and pass the application-status check below. Stop early after collecting 3 valid postings.
- Spend at most 2 minutes verifying or recovering a single posting. If it remains unverified, exclude it.

Use the variables below (derived from Step 2) to build search queries:
- `{primary_skill}` — top skill (e.g., Python, Java, Go)
- `{secondary_skill}` — second skill (e.g., Django, Spring, Kubernetes)
- `{job_level}` — seniority (e.g., Senior, Lead)
- `{job_type}` — role keyword (e.g., Backend Engineer, Data Scientist)
- `{city}` — target city (e.g., Berlin, Amsterdam, London)
- `{country}` — target country (e.g., Germany, Netherlands, UK)
- `{preferred_company}` — a target company from the resume, if any

#### 3-A. Country-Specific Job Site Selection

Local sites often carry postings that global platforms miss. When a target country is known (or can be inferred from the city), include its local sites alongside LinkedIn.

| Country | Local Job Sites | Expat / English-Friendly Sites |
| :--- | :--- | :--- |
| **Germany** | StepStone (`stepstone.de`), XING (`xing.com`) | Arbeitnow (`arbeitnow.com`), IamExpat (`iamexpat.com`) |
| **Netherlands** | Jobbird (`jobbird.com`), Nationale Vacaturebank (`nationalevacaturebank.nl`) | IamExpat (`iamexpat.com`) |
| **Switzerland** | Jobs.ch (`jobs.ch`), Jobup.ch (`jobup.ch`) | IamExpat (`iamexpat.com`) |
| **Austria** | karriere.at (`karriere.at`) | IamExpat (`iamexpat.com`) |
| **France** | Welcome to the Jungle (`welcometothejungle.com`) | The Local Jobs (`thelocal.com/jobs`) |
| **Norway** | FINN.no (`finn.no/job`) | The Local Jobs (`thelocal.com/jobs`) |
| **Sweden** | Platsbanken (`arbetsformedlingen.se/platsbanken`) | The Local Jobs (`thelocal.com/jobs`) |
| **Denmark** | Jobindex.dk (`jobindex.dk`) | Workindenmark.dk (`workindenmark.dk`) |
| **UK** | Reed.co.uk (`reed.co.uk`), Totaljobs (`totaljobs.com`) | — |
| **Ireland** | IrishJobs.ie (`irishjobs.ie`) | — |
| **Spain** | InfoJobs (`infojobs.net`) | The Local Jobs (`thelocal.com/jobs`) |

**Europe-wide platforms:** Relocate.me (`relocate.me`, tech roles with relocation/visa support), Europe Language Jobs (`europelanguagejobs.com`), EURES (`ec.europa.eu/eures`).

**Site selection rules:**
1. Single country → LinkedIn + up to 2 local sites + one expat site if the applicant is a non-native speaker or needs a visa.
2. City → infer the country and apply rule 1.
3. "Europe" or multiple countries → LinkedIn + one Europe-wide platform + local sites of the 2 most relevant countries.
4. A site named by the user → use it directly (see below) and supplement with a `site:` query.

#### 3-B. Arbeitnow API (Germany / DACH)

When Arbeitnow is selected, prefer its public JSON API over scraping. It returns structured postings with timestamps:

```bash
curl -s --max-time 15 "https://www.arbeitnow.com/api/job-board-api?page=1"
```

- Add `&visa_sponsorship=true` when the applicant needs sponsorship. Fetch at most 2 pages in Fast mode.
- Filter results locally by keywords (title, `tags`, `description`) and `location`.
- Convert `created_at` (Unix timestamp) to `YYYY-MM-DD` for `Posted Date`.
- Use the returned `url` as the `Detail URL` with `Link Provenance: api-response`. The application-status check below still applies.
- If the API is unreachable, fall back to `WebSearch` with `site:arbeitnow.com`.

#### 3-C. Web Search Queries

Fire ALL queries simultaneously in a single parallel batch:
- `"{job_level} {primary_skill} {job_type}" jobs {city} {current_year}`
- `"{primary_skill} {secondary_skill}" "{job_type}" hiring {city}`
- `site:linkedin.com/jobs "{primary_skill}" "{job_type}" {city}`
- *(country-specific)* `site:{local_site_domain} "{primary_skill}" "{job_type}" {city}` — at most 2 local `site:` queries in Fast mode
- *(if preferred companies exist)* `"{preferred_company}" jobs {city} {primary_skill}`
- *(early-career rule)* `"{primary_skill}" "{job_type}" internship OR trainee OR "working student" {city} {current_year}`

**Fast mode limits:**
- Run only 1 initial parallel search batch.
- Review at most 8 candidate search results before deciding what to keep.
- Retry the search **at most once**, and only if fewer than 2 valid postings remain after filtering and deduplication.
- Within the 8-candidate limit, open the detail page and application destination for every potential recommendation. Do not keep an unchecked posting to satisfy a result count or time limit.

**If the user specifies a particular site:**
- Visit that site directly via `WebFetch` with a dynamically constructed search URL, and perform a supplementary `site:` search via `WebSearch`.
- Example: "Find it on LinkedIn" → `WebFetch` LinkedIn search URL + `WebSearch` `site:linkedin.com/jobs`

#### 3-D. Mandatory Application-Status Check

- Open the exact posting during the current search, preferably on the employer's official careers site or applicant tracking system (ATS). Search snippets, cached descriptions, crawl dates, HTTP 200 responses, and an Apply label alone do not establish that applications are open.
- Follow the Apply link to confirm that it reaches an active application form or application-start screen for the same company and role. A form on the detail page also qualifies. An official posting with explicit, current email application instructions may qualify without a form. Do not submit applications, enter personal data, create accounts, or send messages as part of verification.
- Classify each checked candidate as **Open**, **Closed**, or **Unverified**. Recommend only **Open** postings with positive evidence of an active application route and no unresolved closure signals.
- Treat a passed application deadline, a disabled application control, or any closure notice as a closure signal. Common notices:
  - **English**: `No longer accepting applications`, `This job posting is closed`, `Job no longer available`, `This vacancy has now expired`, `Position filled`, `Applications closed`
  - **German**: `Keine Bewerbungen mehr möglich`, `Stelle nicht mehr verfügbar`, `Stelle besetzt`, `Anzeige abgelaufen`
  - **French**: `Offre non disponible`, `Annonce clôturée`, `Offre expirée`, `Poste pourvu`
  - **Dutch / Spanish / Italian**: `Verlopen`, `Vacature gesloten` / `Ya no se aceptan solicitudes`, `Oferta cerrada` / `Annuncio scaduto`
  - Match whole phrases in the visible text. Do not treat benign words as closure signals (e.g., German `abgeschlossen` "completed", Italian `contratto a tempo indeterminato`).
  - Ignore closure phrases that appear only in scripts or embedded translation data. Many ATS pages ship every UI string with every page; JOIN, for example, always contains `This job is no longer available`. Read the posting's own state instead (on JOIN, `"status":"ONLINE"` in the embedded job data means open; `OFFLINE` or another value means closed).
- Exclude removed pages (HTTP 404/410), unresolvable hosts, and redirects to generic careers/search pages, including `expired_jd_redirect`.
- If access is blocked, login prevents viewing the application state, only cached/search content is available, or evidence conflicts, mark the candidate **Unverified** and exclude it. An expired mirror may be replaced only by a verified-open official posting for the same role; recommend the official URL and record the discrepancy.
- Record the check time (with timezone), evidence URL, and a brief description of the observed application state. A missing closure notice is not positive evidence. Never describe an unverified posting as an active opportunity.

**LinkedIn postings:** LinkedIn renders the `No longer accepting applications` banner with JavaScript, so a fetched `/jobs/view/` page looks open even when it is closed, and an expired posting silently redirects to a search page. Check every LinkedIn candidate through the unauthenticated jobs-guest API:

```bash
curl -sL --http1.1 --max-time 20 -A "Mozilla/5.0" \
  "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
```

- `{job_id}` is the trailing digit sequence of the `/jobs/view/` URL (e.g., `...-at-example-4452704835` → `4452704835`).
- **Closed** if the response is HTTP 404/410, (near-)empty, or contains `closed-job` or `No longer accepting applications`, or if the detail URL redirects off `/jobs/view/`.
- The same response contains the posting age in `posted-time-ago__text` (e.g., `3 days ago`); use it as the `Posted Date` source.
- A guest-API pass only rules out a LinkedIn closure. If the posting uses an external Apply link, still confirm the employer's application route; prefer the employer's own posting when it is found.
- HTTP 429 means rate limiting, not closure. Wait a few seconds and retry once.
- If the guest API is still unreachable, mark the posting **Unverified** unless the same role is verified open on the employer's site.

#### 3-E. Posted Date

- Extract `Posted Date` only from tool output: a search snippet, fetched page, API response, or the LinkedIn guest API. Never infer a date from a search filter or from how recent a posting "looks".
- Normalize relative dates (`Today`, `3 days ago`) into absolute dates using the current date.
- If tool outputs disagree, or no date can be read after a genuine attempt, set `Posted Date: Unknown`. Never guess.
- Exclude postings with a confirmed date older than 3 months. Rank dated postings (most recent first) before `Unknown` ones.

#### 3-F. Link Capture Rules (very important)

- Prefer the **canonical job detail page URL**: the page where the user can directly view the specific posting or apply.
- Final link priority must be:
  1. Official company career detail URL
  2. Stable LinkedIn job detail URL
  3. Stable job-board detail URL
- **Never fabricate or assemble URLs.** The exact `Detail URL` must appear verbatim in current-session tool output (search result, fetched page, or API response). Building a URL from a known ATS domain (Workday, Greenhouse, Lever, Personio, SmartRecruiters, etc.) plus a guessed job ID or slug is fabrication, even when the domain is correct.
- Classify each candidate URL:
  - **Likely detail page**: has a job ID, a role-specific slug, or a path deeper than a careers hub (e.g., `/jobs/12345`, `/positions/backend-engineer-berlin`).
  - **Generic hub**: broad paths such as `/jobs`, `/careers`, `/join-us`, `/open-positions`, `/vacancies`, or a filtered listing/search page. Reject these as `Detail URL`.
- Reject unstable or intermediate URL patterns as final links. Examples include:
  - `stepstone.de/*-inline.html`
  - search result URLs
  - redirect or tracking-heavy URLs
  - company homepages or generic careers landing pages when the result claims to be a specific role
- Recovery order for a weak link:
  1. Look for the direct official posting URL for the same company + title in the current results or page.
  2. Otherwise keep a stable platform detail page for that exact posting.
  3. Otherwise exclude the posting. Never "upgrade" a specific platform link to a broader company jobs hub.
- **Follow redirects to the final posting URL.** Some boards repost a role under a new ID and redirect the old link (JOIN does this). When the final page is the same company and role, save the post-redirect URL as `Detail URL`. If the redirect lands on a different role, a listing, or a hub, treat the posting as closed.
- Always store both:
  - `Source URL`: where the posting was discovered
  - `Detail URL`: the canonical final job detail page URL
- Also store a markdown-safe `Detail Link` using angle brackets when needed. Some markdown renderers break when URLs contain `)` `]` spaces, tracking params, or get auto-escaped.
- Normalize URLs:
  - If a URL is missing a scheme, prepend `https://`.
  - Remove trailing punctuation accidentally captured from prose (common: `.`, `,`, `)`).
  - If the URL contains parentheses, prefer angle-bracket form `<https://...>` in the output (markdown link parsers are inconsistent around `)`).
- After the application-status check, run a **local link-format validation** before saving results. This is a formatting check, not a substitute for checking application availability:
  - The URL is an absolute `http` or `https` URL.
  - The URL looks like a stable detail page rather than an intermediate or inline rendering page.
  - The URL is not obviously a homepage or generic careers landing page when the posting claims to be a specific role.
  - `Detail URL` and `Detail Link` point to the same destination.
  - The rendered markdown will not likely break because of missing scheme, trailing punctuation, or unescaped parentheses.
- Set `Link Confidence` to `official` only for a company-owned single-posting URL, and `platform` for a stable LinkedIn or job-board single-posting URL.
- Set `Link Provenance` to how the `Detail URL` was obtained: `search-snippet`, `fetched-page`, or `api-response`.
- If a stable detail URL cannot be obtained confidently, exclude the posting instead of saving a weak or likely-dead link.

### 4. Suitability Judgment and Filtering

Evaluate suitability by comparing the found postings against the resume:

- **High**: Core skills and experience level mostly match.
- **Medium**: Some skills match, but there is a gap in domain or specific requirements.
- **Low**: Very few matching aspects → Exclude from results.

Also treat hard requirements the resume clearly does not meet (e.g., native-level German, a required work permit, much higher seniority) as gaps, and exclude the posting when they make an application unrealistic.

Select up to 5 postings with "High" or "Medium" suitability and verified **Open** status. Suitability cannot override a closed or unverified application route.

**Standalone evaluation:** Write `Match Points` and `Gaps` so each posting makes sense on its own. Do not compare postings with each other (e.g., avoid "better than #1").

### 5. Organize and Save Results

Save the search results as a markdown file. Include frontmatter at the top. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to avoid overwriting.**

**Save Path**: `results/job-search-eu/[YYYY-MM-DD]_[Applicant_Name]_[Country_or_City]_search_results.md`

Use the most specific location scope requested by the user:
- City specified → city name (e.g., `Berlin`)
- Country specified → country name (e.g., `Germany`)
- Broad region or no specific location → `Europe`

Before saving:
- Confirm that every recommendation has **Open** status, current-search evidence, a traceable `Detail URL`, and a stable detail URL that passes local link-format validation. Exclude any that fail.
- Save fewer results, including zero, when limits are reached. If none qualify, state that no suitable, verified-open postings were found within this search; do not imply that no such jobs exist anywhere.
- If useful, add a short, separate exclusion log with company, role, and reason. Closed and unverified roles must not appear in recommendation tables, rankings, or application suggestions in either the report or chat summary.

**Mandatory script validation (after writing, before reporting):**

```bash
python3 skills/job-search-eu/scripts/validate_report.py "<saved_file_path>"
```

- The script re-checks every numbered entry's `Detail URL`: URL format, generic jobs hubs, unresolvable hosts, removed pages (HTTP 404/410), closure notices in several languages, login walls, JOIN posting status, redirects to a different URL, and LinkedIn closed/expired status via the jobs-guest API. It uses only the Python standard library and `curl`.
- **Exit code 1**: remove every `❌` entry, move it to the exclusion log with the script's reason, update the Summary table, re-number the remaining entries, and re-run the script until it passes.
- **`⚠️` warnings pass** but mean the script could not confirm the page (bot protection, rate limiting, or JS-rendered content). Keep such an entry only if your own application-status check in Step 3-D recorded Open evidence for it; otherwise remove it.
- **`⚠️ WARN redirected to ...`**: the saved link now redirects. If the target is the same role, replace `Detail URL` and `Detail Link` with the target and re-run; otherwise remove the entry.
- **Exit code 0**: the report is final.
- If no entries remain, keep the file with the "no verified-open postings found" statement and the exclusion log.
- Do not skip this step. Self-reported `Application Status` or `Link Confidence` fields are not a substitute.

## Output Template

```markdown
---
title: Job Search Results - [Applicant Name] [Country or City] [YYYY-MM-DD]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: job-search-eu
tags: [job-search, postings]
---

# Job Posting Search Results

**Search Date**: [YYYY-MM-DD]
**Search Mode**: Fast / Extended (application-status verification required in both)
**Time Budget**: 10 minutes
**Search Criteria**: [core skills], [job type], [city]
**Search Sources**: [list of sites actually searched, including local sites and APIs]

---

## 1. [Company Name] - [Position Name]

- **Suitability**: High / Medium
- **Posted Date**: [YYYY-MM-DD, or Unknown]
- **Location**: Berlin, Germany
- **Employment Type**: Full-time
- **Key Tech**: Python, Django, PostgreSQL, AWS
- **Experience Required**: 5+ years
- **Source URL**: https://example.com/search-or-source-page
- **Detail URL**: https://example.com/job/123
- **Detail Link**: <https://example.com/job/123>
- **Link Confidence**: official / platform
- **Link Provenance**: search-snippet / fetched-page / api-response
- **Application Status**: Open
- **Checked At**: [YYYY-MM-DD HH:MM timezone]
- **Application Evidence URL**: [exact page or application destination checked]
- **Application Evidence**: [observed active form/start screen for this role, or current official email application instructions]
- **Match Points**: Summary of core elements matching the resume
- **Gaps**: Lacking aspects (if any)

---

## 2. [Company Name] - [Position Name]
...

---

## Summary

| # | Company | Position | Posted Date | Suitability | Core Match |
|---|---------|----------|-------------|-------------|------------|
| 1 | Company A | Backend Engineer | 2026-04-08 | High | Python, Django, AWS |
| 2 | Company B | Senior Developer | Unknown | Medium | Python, PostgreSQL |

## Excluded Candidates (optional)

| Company | Position | Reason |
|---------|----------|--------|
| Company C | Backend Engineer | Closed (LinkedIn: No longer accepting applications) |
```

## Core Rules

- **Only recommend verified-open postings.** Real but expired postings are not actionable results. Never invent postings or fill the list with closed or unverified candidates.
- **Never fabricate URLs.** Every `Detail URL` must appear verbatim in current-session tool output. Pattern-assembled ATS links are fabrication.
- **Must include working links.** For every posting, include `Source URL`, `Detail URL`, and a markdown-safe `Detail Link`. Prefer the exact job detail page; do not replace it with a homepage/careers landing page.
- **Canonical links only.** Do not save unstable intermediate URLs or generic job hubs when a posting claims to be a specific job detail page.
- **Verify before recommending.** The detail page and application route must pass the mandatory status check in every mode. URL formatting checks and search snippets are insufficient. A clean-looking LinkedIn detail page proves nothing; use the jobs-guest API.
- **Run the validation script before reporting.** `scripts/validate_report.py` must pass (exit 0) on the saved report; remove flagged entries and re-run.
- **Default to Fast mode.** Bound discovery and verification time, and reduce the result count rather than skipping verification.
- **Dates come from tool output.** Never guess `Posted Date`; use `Unknown` when it cannot be read. Exclude postings with a confirmed date older than 3 months.
- **Respect the preferred work location.** Do not broaden a city-level preference to the whole country unless the user asks.
- **Search preferred companies.** If the resume lists target companies, run a dedicated query for them.
- **Be conservative with suitability judgments.** Base judgments on clear matches found within the resume, and do not force the inclusion of irrelevant postings.
- **Be honest if search results are lacking.** Save only verified-open matches, even if there are zero. Explain the limited coverage and, where useful, suggest broader criteria without presenting excluded candidates as recommendations.
- **Deduplicate postings.** If the same position at the same company appears on multiple platforms, keep only the most informative or official source (prefer the company's own career page over aggregators). Judge duplicates by matching company name + position title.
- **Language Policy**: Follow the Language Policy section. Field labels stay fixed in English; prose follows the user's request language.
