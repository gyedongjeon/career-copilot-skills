---
name: resume-tailor
description: A skill that compares a base resume with a job posting to create a tailored resume optimized for the specific role. It reframes the resume by highlighting strengths and downplaying less relevant areas while staying true to the facts. Triggered by requests like "Update my resume for this job", "Tailor my resume", "Customize my resume", or "Create a resume for this position". Also used when the user wants to refine their resume after a suitability analysis via the job-fit-analyzer skill. Use this for any situation requiring resume modification, optimization, or tailoring.
---

# Resume Tailor

Analyzes the base resume against a job posting and generates a tailored resume in Markdown format, optimized for the specific role.

## Core Principles

The goal of this skill is to **show the same facts through a different lens**. Never fabricate experiences or add skills that do not exist. Instead:

- **Surface relevant experiences**: Bring experiences directly related to the posting to the top and highlight specific achievements.
- **Incorporate keywords**: Naturally reflect the keywords and terminology used in the job posting.
- **De-emphasize less relevant areas**: Downplay or restructure less relevant experiences (adjusting the focus rather than deleting them).
- **Reframe existing experience**: Present existing accomplishments within the context of the posting's domain (e.g., "managing robot fleets" → "optimizing logistics operations").

## Workflow

### 1. Gather Inputs

**Base Resume:**
- If a file path is provided, read it (`.md`, `.pdf`, `.txt`).
- If a URL is provided, fetch it using `WebFetch`.
- If shared as text in the conversation, use it as-is.
- If none of the above are available, request a resume from the user.

**Job Posting:**
- If shared as text in the conversation, use it as-is.
- If a URL is provided, fetch it using `WebFetch`.

### 2. Gap Analysis (Internal Step)

Perform an internal gap analysis using the logic from the `job-fit-analyzer` skill. This step's results are not included in the final output but serve as the basis for modifications:

- Extract job requirements (Minimum Qualifications, Preferred Qualifications).
- Match requirements against the resume (✅ Met, ⚠️ Partially Met, ❌ Not Met).
- Identify strengths and weaknesses.

### 3. Establish Resume Modification Strategy

Determine the strategy based on the gap analysis results:

**Strengths (✅ Items) → Highlight**
- Rewrite using keywords from the posting.
- Move quantifiable achievements to the forefront.
- Expand descriptions of relevant projects or experiences.

**Partially Met (⚠️ Items) → Reframe**
- Reinterpret related experiences in the context of the posting.
- Example: "Managed 100+ autonomous robot fleet" → "Real-time monitoring, scheduling, and operational optimization for 100+ devices."
- Emphasize transferable skills.

**Not Met (❌ Items) → Downplay/De-emphasize**
- Reduce the weight of unrelated experiences (fewer bullet points).
- Avoid phrases that directly highlight the missing area.
- Do not delete core career history—only adjust the level of detail.

### 4. Create Tailored Resume

Maintain the original resume's structure as a baseline while applying the following adjustments:

**Professional Summary**
- Completely rewrite to reflect the posting's core requirements.
- Summarize the experiences and competencies most relevant to the position.

**Experience Section**
- Rearrange bullet points within each role by relevance to the posting.
- Provide detail for relevant achievements and be concise for unrelated items.
- Naturally incorporate terms and keywords used in the posting.
- Maintain the "Action Verb + Quantifiable Result" format (e.g., "Optimized path planning, achieving 15x performance improvement").

**Skills Section**
- Place skills required by the posting at the beginning.
- Move unrelated skills to the end or group them under a sub-heading like "Others."
- Match the posting's terminology (e.g., if the posting asks for "PostgreSQL," use "PostgreSQL" rather than "Postgres").

**Other Sections (Education, Certifications, Languages, etc.)**
- Emphasize items relevant to the posting (e.g., highlight a German language certificate when applying to a German company).
- Maintain unrelated items but adjust their order if necessary.

### 5. Output

Save the modified resume as a Markdown file with a frontmatter section. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to preserve existing versions.**

- **Filename**: `[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume.md`
- **Output Path**: `resume-tailor-results/`

## Output Template

```markdown
---
title: Tailored Resume - [Applicant Name] ([Company Name])
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: resume-tailor
applicant: [Applicant Name]
company: [Company Name]
tags: [resume, tailored]
---

[Follow original resume structure, but with modifications]
```

After the resume, output a brief **Modification Summary** separately in the chat (do not include in the file):

```
## 📝 Modification Summary

### Key Changes
1. Rewrote Summary to align with [Core Posting Requirement].
2. Detailed [Relevant Experience] in [Company A] and incorporated keywords.
3. De-emphasized experiences at [Company B].
4. Reorganized Skills section to match job requirements.

### Reframing Points
- "Robot fleet management" → "Real-time device monitoring and operational optimization"
- "B2B2C SaaS Platform" → "High-traffic processing and order/settlement systems"

### Notes
- [Supply Chain Domain Experience] was difficult to reflect directly in the resume; recommended for inclusion in the cover letter.
```

## Core Rules

- **No Fabrication**: Do not add experiences, skills, or certifications that are not in the original resume. All content must be based on the source document. Do not add unconfirmed content under "Learning", "Exploring", or "Interests" unless it was already present.
- **Minimize Deletion**: Do not delete entire roles or projects; only adjust their weight.
- **Natural Flow**: Do not force keywords. While optimized for ATS, it must remain readable and professional for recruiters.
- **Language Alignment**: Match the language of the job posting (e.g., English posting → English resume). Maintain technical terms in their original form.
- **Preserve Originals**: Do not modify the original resume file. Always save as a new file.
- **Specific Output Path**: Store results in `resume-tailor-results/` directory.
