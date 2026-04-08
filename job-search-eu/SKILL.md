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

If initial search results are lacking, modify the query and retry **at most once**.

**If the user specifies a particular site:**
- Visit that site directly via `WebFetch` with a dynamically constructed search URL, and perform a supplementary `site:` search via `WebSearch`.
- Example: "Find it on LinkedIn" → `WebFetch` LinkedIn search URL + `WebSearch` `site:linkedin.com/jobs`

**Detail page visits:**
- Only visit a posting's detail page via `WebFetch` when the search result lacks key information (company, title, or tech stack). Skip detail page visits for postings where this information is already clear.

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
**Search Criteria**: [core skills], [job type], [city]
**Search Sources**: [list of sites actually searched]

---

## 1. [Company Name] - [Position Name]

- **Suitability**: High / Medium
- **Location**: Berlin, Germany
- **Employment Type**: Full-time
- **Key Tech**: Python, Django, PostgreSQL, AWS
- **Experience Required**: 5+ years
- **Link**: [Posting URL]
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
- **Must include links.** Include the original URL for every single posting so the user can verify it directly.
- **Prioritize recent postings.** If possible, exclude older postings (more than 3 months old).
- **Be conservative with suitability judgments.** Base judgments on clear matches found within the resume, and do not force the inclusion of irrelevant postings.
- **Be honest if search results are lacking.** If there are fewer than 5 postings, advise: "You may find more results by broadening the search scope or adjusting keywords."
- **Deduplicate postings.** If the same position at the same company appears on multiple platforms, keep only the most informative or official source (prefer the company's own career page over aggregators). Judge duplicates by matching company name + position title.
- **Language Policy**: Summarize the output in the user's preferred language (the language they used to request the skill). Keep proper nouns like company names, position names, and technical terms in their original language.
