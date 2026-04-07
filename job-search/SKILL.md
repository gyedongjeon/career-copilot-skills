---
name: job-search
description: A skill that searches the web for the latest suitable job postings based on a resume and summarizes the results. Triggered when the user asks "Search for job postings", "Find postings that fit my resume", "Are there any positions for me lately?", "Look up Python jobs in Berlin", "Search backend jobs on LinkedIn", or "Dig up some job postings". It integrates searches across multiple sites even if a specific site is not designated, and focuses on a specified site if one is provided. Use this skill in all situations where exploring job postings is needed during a job search, career change, or employment preparation.
---

# Job Search

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

Utilize `WebSearch` and `WebFetch` to look for job postings using two methods.

**Method 1: Direct Exploration of Job Sites**

Directly visit the search pages of major job boards via `WebFetch` based on the skills/roles/location from the resume. Dynamically construct the search URL for each site tailored to the extracted keywords:

- **GermanTechJobs**: `https://germantechjobs.de/jobs/Python/Berlin`
- **Arbeitnow**: `https://www.arbeitnow.com/jobs?search=python+backend&location=berlin`
- **Relocate.me**: `https://relocate.me/international-jobs/python`
- **Indeed**: `https://de.indeed.com/jobs?q=python+backend+engineer&l=Berlin`
- **LinkedIn**: `https://www.linkedin.com/jobs/search/?keywords=python+backend&location=Berlin` (may have login walls)
- **Stepstone**: `https://www.stepstone.de/jobs/python-backend-engineer/in-berlin`
- **DevJobsScanner**: `https://www.devjobsscanner.com/django-jobs-in-berlin/`

Dynamically construct the search query portion of the site URL according to the keywords extracted from the resume. If a site is inaccessible, move on to the next.

**Method 2: Utilizing Web Search Engines**

Use `WebSearch` to conduct supplementary Google searches:
- `"Senior Python Backend Engineer" jobs Berlin 2026`
- `site:greenhouse.io "Python" "Backend" Berlin`
- `site:ashbyhq.com Python Backend Berlin`
- `"Python Django" "Backend Engineer" hiring Berlin`

**If the user specifies a particular site:**
- Prioritize visiting that site directly (`WebFetch`), and perform a supplementary `site:` search.
- Example: "Find it on LinkedIn" → Visit LinkedIn search URL directly + search `site:linkedin.com/jobs`

**Search Tips:**
- Use both methods in parallel to gather as many candidates as possible, then filter by suitability.
- Combine tech keywords in various ways (Python + Django, Python + Backend, Python + API, etc.).
- Include the current year in the search query to prioritize recent postings.
- If initial search results are lacking, modify the query and try again.
- From the search results, use `WebFetch` to retrieve the actual job posting pages and check the details.

### 4. Suitability Judgment and Filtering

Evaluate suitability by comparing the found postings against the resume:

- **High**: Core skills and experience level mostly match.
- **Medium**: Some skills match, but there is a gap in domain or specific requirements.
- **Low**: Very few matching aspects → Exclude from results.

Select 5-10 postings with "High" or "Medium" suitability.

### 5. Organize and Save Results

Save the search results as a markdown file. Include frontmatter at the top.

**Save Path**: `job-search-results/[YYYY-MM-DD]_search_results.md`

## Output Template

```markdown
---
title: Job Search Results - [YYYY-MM-DD]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: job-search
tags: [job-search, postings]
---

# Job Posting Search Results

**Search Date**: 2026-03-29
**Search Criteria**: Python, Django, Backend Engineer, Berlin
**Search Sources**: LinkedIn, Indeed, Stepstone, Glassdoor

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
- **Language Policy**: Summarize the output in the user's preferred language (the language they used to request the skill). Keep proper nouns like company names, position names, and technical terms in their original language.
