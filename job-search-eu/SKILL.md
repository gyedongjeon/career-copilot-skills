---
name: job-search-eu
description: Searches the web for the latest suitable job postings in Europe based on a resume and summarizes the results. Integrates searches across multiple EU job sites and general platforms. Triggered by requests like "Search for job postings in Europe", "Find postings that fit my resume in Germany", "Are there any positions for me lately in London?", or "Search backend jobs on LinkedIn for Europe".
---

# Job Search EU

Analyzes the resume to extract core competencies and technical keywords, searches the web for the latest suitable job postings, and summarizes the results.

## Workflow

### 1. Read Resume

- If a file path is given, read it using `Read`.
- If shared as text in the conversation, use it as is.
- If neither is provided, search the `resumes/` folder in the project for the applicant's resume (e.g., markdown files).
- If no resume can be found, request it from the user. When requesting, proactively guide them with the following tip: *"For future convenience, please save the applicant's resume as a markdown file named after them (e.g., `resumes/[Applicant Name].md`) inside the `resumes/` folder."*

### 2. Extract Search Criteria

Automatically extract the following information from the resume:

- **Core Skills**: Top 2-3 skills with the most experience (e.g., Python, Django, AWS)
- **Job Level**: Based on years of experience (e.g., Senior, Lead)
- **Job Type**: Based on job titles/roles in the resume (e.g., Backend Engineer, Software Engineer)
- **Location**: Utilize residence/visa info if present in the resume (e.g., Berlin, Germany)

If the user specifies additional conditions (location, skills, role, specific site, etc.), apply those conditions with priority.

### 3. Web Search

Use `WebSearch` as the primary method. `WebFetch` is only used when the user specifies a particular site.

**Default mode:** Run in **Fast mode** unless the user explicitly asks for exhaustive search or strict link verification.

**Time budget:**
- Start a wall-clock timer when web searching begins.
- Use a default total time budget of **10 minutes** for the full search workflow.
- If the 10-minute budget is reached, stop searching immediately and save the **best results collected so far**.
- Partial results are acceptable. Do not discard already validated postings just because fewer than 5 were found.
- If 3 valid postings are collected before the time budget is exhausted, stop early and save the results.
- Do not spend more than 2 minutes trying to improve or replace a single posting link.

Use the variables below (derived from Step 2) to build search queries:
- `{primary_skill}` — top skill (e.g., Python, Java, Go)
- `{secondary_skill}` — second skill (e.g., Django, Spring, Kubernetes)
- `{job_level}` — seniority (e.g., Senior, Lead)
- `{job_type}` — role keyword (e.g., Backend Engineer, Data Scientist)
- `{city}` — target city (e.g., Berlin, Amsterdam, London)

**Web Search Queries**

Fire ALL queries simultaneously in a single parallel batch:
- `"{job_level} {primary_skill} {job_type}" jobs {city} {current_year}`
- `"{primary_skill} {secondary_skill}" "{job_type}" hiring {city}`
- `site:linkedin.com/jobs "{primary_skill}" "{job_type}" {city}`

**Fast mode limits:**
- Run only 1 initial parallel search batch.
- Review at most 8 candidate search results before deciding what to keep.
- Retry the search **at most once**, and only if fewer than 2 valid postings remain after filtering and deduplication.
- Visit at most 2 posting detail pages in total unless the user explicitly asks for a deeper search.

**If the user specifies a particular site:**
- Visit that site directly via `WebFetch` with a dynamically constructed search URL, and perform a supplementary `site:` search via `WebSearch`.
- Example: "Find it on LinkedIn" → `WebFetch` LinkedIn search URL + `WebSearch` `site:linkedin.com/jobs`

**Detail page visits:**
- Only visit a posting's detail page via `WebFetch` when the search result lacks key information (company, title, or tech stack). Skip detail page visits for postings where this information is already clear.
- Do not use detail-page visits as an open-ended quality pass. In Fast mode, use them only to fill missing core fields or to recover a more stable final link when it can be done quickly.

**Link capture rules (very important):**
- Prefer the **canonical job detail page URL**: the page where the user can directly view the specific posting or apply.
- Final link priority must be:
  1. Official company career detail URL
  2. Stable LinkedIn job detail URL
  3. Stable job-board detail URL
- Reject unstable or intermediate URL patterns as final links. Examples include:
  - `stepstone.de/*-inline.html`
  - search result URLs
  - redirect or tracking-heavy URLs
  - company homepages or generic careers landing pages when the result claims to be a specific role
- Always store both:
  - `Source URL`: where the posting was discovered
  - `Detail URL`: the canonical final job detail page URL
- Also store a markdown-safe `Detail Link` using angle brackets when needed. Some markdown renderers break when URLs contain `)` `]` spaces, tracking params, or get auto-escaped.
- Normalize URLs:
  - If a URL is missing a scheme, prepend `https://`.
  - Remove trailing punctuation accidentally captured from prose (common: `.`, `,`, `)`).
  - If the URL contains parentheses, prefer angle-bracket form `<https://...>` in the output (markdown link parsers are inconsistent around `)`).
- Run a **default local link validation** before saving results. This validation must stay fast and should not make network requests. Check only:
  - The URL is an absolute `http` or `https` URL.
  - The URL looks like a stable detail page rather than an intermediate or inline rendering page.
  - The URL is not obviously a homepage or generic careers landing page when the posting claims to be a specific role.
  - `Detail URL` and `Detail Link` point to the same destination.
  - The rendered markdown will not likely break because of missing scheme, trailing punctuation, or unescaped parentheses.
- If a stable detail URL cannot be obtained confidently, exclude the posting instead of saving a weak or likely-dead link.
- Run a **strict link check** only when the user explicitly asks for it, or when link reliability is the main concern. Strict check may open/fetch each final posting URL to confirm it still resolves to the intended job page, but it is optional because it is slower and some sites block automated requests.

### 4. Suitability Judgment and Filtering

Evaluate suitability by comparing the found postings against the resume:

- **High**: Core skills and experience level mostly match.
- **Medium**: Some skills match, but there is a gap in domain or specific requirements.
- **Low**: Very few matching aspects → Exclude from results.

Select up to 5 postings with "High" or "Medium" suitability.

### 5. Organize and Save Results

Save the search results as a markdown file. Include frontmatter at the top. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to avoid overwriting.**

**Save Path**: `job-search-eu-results/[YYYY-MM-DD]_[Applicant_Name]_[Country_or_City]_search_results.md`

Use the most specific location scope requested by the user:
- City specified → city name (e.g., `Berlin`)
- Country specified → country name (e.g., `Germany`)
- Broad region or no specific location → `Europe`

Before saving:
- Perform the default local link validation for every final posting.
- If the default validation fails and the URL cannot be repaired confidently, either replace the posting with a better-verified source or state clearly that the exact detail URL could not be verified.
- Do not run strict link check unless the user requested it or the task explicitly prioritizes link verification over speed.
- Save partial results if the time budget or Fast mode limits are reached.

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
**Search Mode**: Fast / Strict
**Time Budget**: 10 minutes
**Search Criteria**: [core skills], [job type], [city]
**Search Sources**: [list of sites actually searched]

---

## 1. [Company Name] - [Position Name]

- **Suitability**: High / Medium
- **Location**: Berlin, Germany
- **Employment Type**: Full-time
- **Key Tech**: Python, Django, PostgreSQL, AWS
- **Experience Required**: 5+ years
- **Source URL**: https://example.com/search-or-source-page
- **Detail URL**: https://example.com/job/123
- **Detail Link**: <https://example.com/job/123>
- **Link Confidence**: official / platform / unverified
- **Match Points**: Summary of core elements matching the resume
- **Gaps**: Lacking aspects (if any)

---

## 2. [Company Name] - [Position Name]
...

---

## Summary

| # | Company | Position | Suitability | Core Match |
|---|---------|----------|-------------|------------|
| 1 | Company A | Backend Engineer | High | Python, Django, AWS |
| 2 | Company B | Senior Developer | Medium | Python, PostgreSQL |
```

## Core Rules

- **Only include actual postings.** Only put real job postings confirmed through search into the results. Do not invent or guess postings. This rule is extremely important — providing non-existent postings wastes the user's time and destroys trust.
- **Must include working links.** For every posting, include `Source URL`, `Detail URL`, and a markdown-safe `Detail Link`. Prefer the exact job detail page; do not replace it with a homepage/careers landing page.
- **Canonical links only.** Do not save unstable intermediate URLs such as inline render pages when a posting claims to be a specific job detail page.
- **Default to fast validation.** The standard workflow must use only local, format-level link validation unless the user asks for stricter verification.
- **Default to Fast mode.** Use bounded search depth, bounded detail-page visits, and a 10-minute time budget unless the user explicitly asks for deeper coverage.
- **Strict link check is opt-in.** Only perform network-based link verification when explicitly requested or when the user prioritizes reliability over speed.
- **Prioritize recent postings.** If possible, exclude older postings (more than 3 months old).
- **Be conservative with suitability judgments.** Base judgments on clear matches found within the resume, and do not force the inclusion of irrelevant postings.
- **Be honest if search results are lacking.** If there are fewer than 5 postings, advise: "You may find more results by broadening the search scope or adjusting keywords." It is acceptable to save only 1-3 solid postings if weak links are the alternative.
- **Deduplicate postings.** If the same position at the same company appears on multiple platforms, keep only the most informative or official source (prefer the company's own career page over aggregators). Judge duplicates by matching company name + position title.
- **Language Policy**: Summarize the output in the user's preferred language (the language they used to request the skill). Keep proper nouns like company names, position names, and technical terms in their original language.
