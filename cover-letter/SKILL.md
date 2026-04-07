---
name: cover-letter
description: A skill that writes a tailored cover letter for a specific company based on a resume and job posting. Triggered when the user says things like "Write me a cover letter", "Draft a cover letter for this posting", "Create a motivation letter", "I want to apply for this job, can you write a cover letter?", or "Write a letter for this company". Also activate this skill when a job posting and resume are present in the conversation, or when existing analysis results (company research, job fit analysis, etc.) are already available in a resumes/[Name]/ folder. Use this skill in any situation where an application document such as a cover letter or motivation letter needs to be written.
---

# Cover Letter Writer

Analyzes the resume and job posting, leverages any existing skill outputs (company research, job fit analysis, etc.) when available, and writes an optimized cover letter tailored to the specific company and position.

## Core Principles

The purpose of a cover letter is to convincingly communicate **"why I am the right fit for this position at this company"** based on the facts stated in the resume.

- Do not fabricate experience, skills, or achievements that are not in the resume. Never include anything the user has not confirmed.
- Connect the key requirements of the posting with the strengths from the resume, but do not exaggerate.
- Do not directly mention weaknesses (areas lacking in the resume); instead, naturally compensate with transferable skills or demonstrated willingness to learn.
- Genuine interest in and motivation for the company must come through. If company research results are available, differentiate by referencing specific business, technology, or culture details.
- Aim for a specific and personal opening rather than formulaic, generic phrases (e.g., "I am writing to express my interest...").

## Workflow

### 1. Gather Inputs

**Resume:**
- Read `resumes/[Name].md` as the default
- If the user specifies a different resume, use that file instead

**Job Posting:**
- If shared as text in the conversation, use it as-is
- If a URL is provided, fetch the content using `WebFetch`

**Check for Existing Analysis Results:**
- Check if a `resumes/[Name]/[Company]/` folder exists
- If it does, read and utilize the following files:
  - `company-research.md` — Company information (mission, tech stack, culture, recent news, etc.)
  - `job-fit-analysis.md` — Resume tailored to the posting (strengths/gaps identified)
  - Any other analysis files found in the folder
- If the folder does not exist, perform an internal gap analysis using only the resume and posting

### 2. Analysis (Internal Step)

Before writing the cover letter, internally organize the following (do not include in the output):

**Company & Position Essentials:**
- What problem is this company solving / what is their mission?
- What are the 3 most critical competencies for this position?
- What aspects of the company's technical direction or culture can be connected to the resume?

**Strength Mapping:**
- Select 2–3 experiences from the resume that directly match the posting's requirements
- Use quantifiable outcomes from those experiences where available

**Weakness Mitigation Strategy:**
- Address gaps through transferable skills or a track record of fast learning
- Never write "I do not have experience in..." directly

### 3. Write the Cover Letter

Use the structure below as a baseline, adjusting flexibly based on content:

**Opening Paragraph**
- State the position being applied for
- Express specific interest in the company (even better if based on company research)
- Hook the reader in the first sentence with a compelling connection

**Body (2–3 Paragraphs)**
- Connect the posting's core requirements to your own experience
- Include concrete outcomes and numbers (use only what is in the resume)
- Explain not just what you did, but "why this experience is valuable for this position"
- Articulate how the company's technology, culture, or mission aligns with your values and background

**Closing Paragraph**
- Summarize the value you can contribute
- Express enthusiasm for the opportunity to interview
- Close with a thank-you

**Length:** Must be strictly concise, fitting easily on half of an A4 page (strictly under 200-250 words for English letters). Never write long, dense paragraphs. Be scannable, punchy, and direct.

### 4. Output

Save the cover letter as a markdown file with a frontmatter section.

- **Save Path**: `cover-letter-results/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_cover_letter.md`

## Output Template

```markdown
---
title: Cover Letter - [Applicant Name] ([Company Name])
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: cover-letter
applicant: [Applicant Name]
company: [Company Name]
tags: [cover-letter, application]
---

[Follow cover letter structure]
```

**Language handling:**
- Always write the cover letter in the **job posting's language** (e.g., English posting → English cover letter, German posting → German cover letter).
- If the user's language (the language they used to trigger the skill) differs from the posting's language, append a full translation of the cover letter below the original, clearly separated with a divider and a heading (e.g., `---` and `## 번역 (Korean Translation)`).
- If both languages are the same, no translation is needed.

After the cover letter, output a brief **Writing Notes** section separately in the chat (do not include in the file):

```
## Writing Notes

### Key Strategy
- [Which strengths were highlighted]
- [Which company-specific information was leveraged]

### Mitigation Points
- [How weaknesses or gaps were navigated]

### Customization Suggestions
- [Personal anecdotes or motivations the user could add themselves]
```

## Core Rules

- **No fabrication**: Do not write experience, skills, or achievements that are not in the resume. Do not arbitrarily add unconfirmed content, even with hedging phrases like "currently learning" or "interested in".
- **No copy-pasting from resume**: Do not lift bullet points from the resume verbatim. A cover letter complements the resume — it does not repeat it.
- **Match the posting's language**: Always write the cover letter in the language of the job posting, not the language the user used. If the user's language differs from the posting's language, append a full translation in the user's language at the end of the file. Keep technical terms (Python, AWS, REST API, etc.) in their original form in both versions.
- **Preserve originals**: Always preserve original files. If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) instead of overwriting.
- **Company-specific**: Never leave the company name or position title as a placeholder like `[Company Name]`. Always fill them in specifically.
- **Keep it brief**: Recruiters are busy. Never exceed 250 words. Write short, punchy paragraphs rather than dense blocks of text.
- **Tone**: Professional yet genuine. Avoid both overly formal ("I humbly submit") and overly casual tones.
