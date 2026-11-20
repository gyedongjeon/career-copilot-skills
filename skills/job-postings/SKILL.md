---
name: job-postings
description: A skill that downloads a job posting from a URL (or pasted text) and archives it as Markdown with the ORIGINAL posting preserved verbatim, then optionally appends a separate analysis/fit section at the end. Triggered when the user says things like "Save this posting", "Download this job ad as markdown", "Archive this JD", "Keep a copy of this posting", or shares a posting URL and wants the full original kept (not just a requirements summary). Use this to build a durable archive of postings the user is interested in; it preserves the exact wording, unlike job-fit-analyzer which only categorizes qualifications.
---

# Job Postings Archiver

Downloads a job posting and saves it as Markdown, keeping the **original posting text verbatim**. Any analysis (fit, gaps, notes) is added in a **separate section at the very end**, so the archived original is never altered or paraphrased.

## Core Principle

- **Original first, verbatim.** The posting body must reproduce the source wording as closely as the tooling allows — do not summarize, reorder, translate, or "clean up" the original. Keep the original language (German stays German, English stays English).
- **Analysis is separate and last.** Fit notes, strengths/gaps, and recommendations go only in a clearly delimited section after the original, never interleaved into it.

## Workflow

### 1. Get the posting content verbatim

`WebFetch` paraphrases and often refuses to reproduce text verbatim, so **do not rely on it for the original body.** Prefer, in order:

1. **ATS structured source via `curl`** (gives the real description text/HTML):
   - **Greenhouse**: `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{id}` → JSON `content` field (HTML-escaped).
   - **Lever**: `https://api.lever.co/v0/postings/{slug}/{id}?mode=json` → `description` / `lists`.
   - **Ashby**: the posting page JSON, or `https://api.ashbyhq.com/posting-api/job-board/{slug}` for the listing.
   - **Personio**: `https://{slug}.jobs.personio.de/job/{id}` page (or the `/xml` feed when enabled).
   - **JOIN / Workable / SmartRecruiters**: the posting page.
2. **LinkedIn**: the unauthenticated guest API — `curl -sL --http1.1 -A "Mozilla/5.0" "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"` — then extract the `show-more-less-html__markup` block. (`{job_id}` = trailing digits of the `/jobs/view/` URL.)
3. **Raw page via `curl` + de-HTML**: fetch the page and strip tags (convert `<li>`→`- `, `<p>`/`<br>`→newlines), preserving headings, lists, and wording.
4. **User paste**: if the content is behind a login wall, is JS-rendered with no readable source, or only a summarizing fetch is possible, ask the user to paste the posting text and save that verbatim. Guide them: *"I couldn't fetch the exact text (login/JS wall). Could you paste the posting so I archive it word-for-word?"*

Capture, when present: company, position/title, location, remote/onsite policy, salary/range, posting/updated date, language of the posting, and any application-form questions (e.g., work permit, salary expectation).

**Never fabricate or guess any part of the posting.** If a field is absent, omit it or mark it "not stated". If a fetch only yields a paraphrase, say so in the file (`capture_method: paraphrase — verbatim unavailable`) rather than presenting a paraphrase as the original.

### 2. Save the archive file

**Save Path**: `results/job-postings/[YYYY-MM-DD]_[Company]_[Position].md`
- Sanitize company/position for the filename (spaces → `_`, drop punctuation).
- **If a file with the same name exists, append a time-based suffix (e.g., `_HHMMSS`)** — never overwrite an existing archive.

Write the **original posting first** (Step 3 template), with metadata in frontmatter.

### 3. Append analysis separately (optional)

Add the analysis **only** when a resume/context is available (e.g., `resumes/`) or the user asks for it. Put it after a horizontal rule under `## Analysis (added later — not part of the original posting)`. Keep it clearly separated from the verbatim body. For fit judgments, follow the same High/Medium/Low approach as `job-fit-analyzer`, and be honest about gaps. If the user does not want analysis, stop after the original.

## Output Format

```markdown
---
title: [Company] — [Position]
company: [Company]
position: [Position]
location: [e.g. Berlin (onsite 3 days/week)]
source_url: [exact posting URL]
ats: [greenhouse (slug) / personio (slug) / lever / linkedin / other]
posted: [YYYY-MM-DD or Unknown]
captured: [YYYY-MM-DD]
capture_method: [curl-ats-json / linkedin-guest-api / curl-html / user-paste / paraphrase — verbatim unavailable]
language: [English / German / ...]
category: job-posting
---

# [Company] — [Position]

## Original posting (verbatim)

[The posting text, reproduced as faithfully as the source allows — responsibilities,
requirements, preferred, tech stack, benefits, language/location/salary, in the
original wording and language. Do not paraphrase or reorder.]

---

## Analysis (added later — not part of the original posting)

**Fit: [High / Medium / Low]**

### 🟢 Strengths
- ...

### 🟡 Gaps & Opportunities
- ...

**💡 Notes:** [application-form questions, salary expectation to enter, hard gates such as
language level or driving licence, cross-links to resume-tailor / cover-letter / job-fit files]
```

## Core Rules

- **Verbatim original, always.** Reproduce the source wording; never paraphrase, translate, or trim the archived posting. If you cannot get verbatim text, record `capture_method` honestly and/or ask the user to paste.
- **Analysis strictly separated.** Only after the original, under its own heading. The original section must read exactly as the employer wrote it.
- **One file per posting**, dated; never overwrite — add `_HHMMSS` on collision.
- **No fabrication.** Only what the posting states. Mark missing fields "not stated".
- **Record the source.** Always store the exact `source_url` and the `ats`; capture application-form questions (work permit, salary expectation) when shown.
- **Language Policy**: keep the **original posting in its own language**, verbatim. Write the **Analysis section in the user's request language** (keep tech terms, company/role names, and URLs in their original form).
- **Relation to other skills**: this skill archives the full posting; use `job-fit-analyzer` for a categorized requirements breakdown, and `resume-tailor` / `cover-letter` to act on a posting. Link to those files from the Notes when relevant.
