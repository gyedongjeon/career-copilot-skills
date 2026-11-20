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
- Read `resumes/[Name].md` as the default.
- If the user specifies a different resume, use that file instead.

**Job Posting:**
- If shared as text in the conversation, use it as-is.
- If a URL is provided, fetch the content using `WebFetch`.

**Applicant Info/Contact:**
- Before modifying the resume, check whether the applicant's contact details (Address, Phone, Email) and preferred English level are available in `resumes/[Name]_info.md`.
- Read and verify:
  - Address
  - Phone
  - Email
  - English level
- If `resumes/[Name]_info.md` does not exist or is missing fields, ask the user for the missing details. Do not guess, infer, or use placeholders.

**Check for Existing Analysis Results:**
- Check if a `resumes/[Name]/[Company]/` folder exists.
- If it does, read and utilize:
  - `company-research.md` (for business/technical direction context)
  - `job-fit-analysis.md` (for pre-analyzed strengths and gaps)
- If the folder does not exist, perform an internal gap analysis using only the resume and posting.

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

**English Level & Readability:**
- For English resumes, use the applicant-confirmed English level when provided; otherwise, default to **plain, simple English**.
- Use simple, active sentence structures: usually one clear idea per sentence.
- Use common verbs such as "built", "led", "improved", "worked with", "designed", and "supported".
- Avoid overly advanced, flowery, or literary phrasing that the applicant cannot sustain in interviews.
- Technical terms from the job posting and resume must match the exact spelling and casing (e.g., PostgreSQL, Docker, Django).

### 5. Output

Create two Markdown files: one working draft for internal review metadata and one final resume output for submission. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to preserve existing versions.**

**Working Draft File**
- **Save Path**: `results/resume-tailor/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume.md`
- This file may include:
  - YAML frontmatter
  - the tailored resume
  - optional review metadata, source notes, or tailoring notes when useful
- This file is not the submission-ready resume.

**Final Resume Output File**
- Always save a separate submission-ready resume Markdown file.
- **Resume Output Save Path**: `results/resume-tailor/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.md`
- The final resume output file must contain only:
  - The tailored resume in the output language
  - No YAML frontmatter
  - No writing notes
  - No analysis
  - No modification summary
  - No source citations unless the user explicitly asks for them
- The final resume output file should be directly usable for PDF conversion and job applications.
- Do not leave placeholders in the final resume output file. If a contact field such as Website is not available in the base resume or applicant info, omit that field or line.
- For English job postings, use `_output_en.md`.
- If the job posting is not in English, create the final output in the posting language and adjust the suffix accordingly (e.g., `_output_de.md`). If an English copy is also requested or useful for PDF submission, create an additional `_output_en.md` file.

**PDF Output**
- Always attempt to create a PDF version from the final resume output file, using the **`resume-pdf` skill** (see Section 6). That skill owns the resume PDF layout and styling.
- **PDF Save Path**: `results/resume-tailor/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.pdf`
- Match the PDF suffix to the final resume output language (e.g., `_output_de.pdf` for a German output file).
- If PDF conversion fails because the `resume-pdf` tools are unavailable, say so in the final response and provide the final resume output Markdown path.
- The `resume-pdf` converter uses temporary files internally; do not leave stray `.html`/`.css` artifacts in `results/resume-tailor/`.
- Final saved artifacts should normally be only:
  - the working draft Markdown
  - the final resume output Markdown
  - the final resume output PDF

### 6. PDF Conversion (via the `resume-pdf` skill)

Do not hand-roll a pandoc/weasyprint pipeline or embed CSS here. The **`resume-pdf` skill** owns the resume PDF layout and styling (single-column, ATS-friendly A4, Charter body / Avenir Next headings, navy accent). Use it for every resume PDF so the resume, cover letter, and any references page look like one set.

**How to run it:**
- Invoke the `resume-pdf` skill, or call its converter directly on the **final resume output Markdown** (the `_output_*.md` file, which has no frontmatter):

  ```bash
  python3 skills/resume-pdf/scripts/md_to_pdf.py \
    "results/resume-tailor/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.md" \
    -o "results/resume-tailor/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.pdf" \
    --fit-pages 2
  ```

- Always pass `-o` with the PDF Save Path from Section 5; otherwise the PDF is written next to the input.
- `--fit-pages 2` keeps it to 2 pages. After it fits, try a larger `--base` (body font pt) and keep the largest value that still fits the page budget, rather than leaving text needlessly small.

**Make the final output Markdown match `resume-pdf` conventions** so it renders fully (see that skill's "Expected Markdown structure"):
- Technical Skills / Languages rows use a bold label: `* **Backend & Frameworks:** value` (a non-bold `* Label: value` line is dropped from the skills grid).
- Job headings are `### Company | Location | Role | Dates`; the `Stack:` line renders as a muted footer under the role.

**Verify before reporting (required):** render the pages and look at them — do not assume the layout is fine.

```bash
pdftoppm -png -r 110 "results/resume-tailor/..._output_en.pdf" /tmp/resume_page   # then read /tmp/resume_page-*.png
```

- Confirm the page count matches the budget and no section is empty or broken across a page.
- Confirm Technical Skills actually rendered (the most common failure when labels are not bold).
- If a layout issue is reusable (affects any resume), fix it in `skills/resume-pdf/assets/resume.css`; keep one-off tweaks scoped to the run.

**If the `resume-pdf` tools are unavailable:**
- The converter needs `pandoc` and `weasyprint` (see the `resume-pdf` skill's Prerequisites). Install only after user approval.
- If it still cannot run, keep the final resume output Markdown file and clearly report the issue with its path.

## Working Draft Template

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

# [Applicant Name]
[Subtitle / Profession]

Email: [Applicant Email] | Phone: [Applicant Phone]  
LinkedIn: [Applicant LinkedIn] | Website: [Applicant Website]

## Professional Summary

[Tailored Professional Summary]

## Technical Skills

* **Backend & Frameworks:** [Backend languages/frameworks]
* **Frontend & Web:** [Frontend/web skills if relevant]
* **Database & Data Modeling:** [Database list]
* **Cloud & Infrastructure:** [DevOps/Cloud details]
* **Methodologies:** [Methodologies/soft skills]

## Professional Experience

### [Company Name] | [Location] | [Role Title] | [Dates]

* [Relevant accomplishment]: [Detail of achievement using action verbs and metrics]
* [Relevant accomplishment]: [Detail of achievement]
* Stack: [Tech stack list]

## Certifications

* [Certification] | [Issuer]

## Education

* [University Name] | [Degree / Field of Study] ([Dates], [GPA / Honors if applicable])

## Language

* [Language]: [Level]
```

## Final Resume Output Template

```markdown
# [Applicant Name]
[Subtitle / Profession]

Email: [Applicant Email] | Phone: [Applicant Phone]  
LinkedIn: [Applicant LinkedIn] | Website: [Applicant Website]

## Professional Summary

[Tailored Professional Summary]

## Technical Skills

* **Backend & Frameworks:** [Backend languages/frameworks]
* **Frontend & Web:** [Frontend/web skills if relevant]
* **Database & Data Modeling:** [Database list]
* **Cloud & Infrastructure:** [DevOps/Cloud details]
* **Methodologies:** [Methodologies/soft skills]

## Professional Experience

### [Company Name] | [Location] | [Role Title] | [Dates]

* [Relevant accomplishment]: [Detail of achievement using action verbs and metrics]
* [Relevant accomplishment]: [Detail of achievement]
* Stack: [Tech stack list]

## Certifications

* [Certification] | [Issuer]

## Education

* [University Name] | [Degree / Field of Study] ([Dates], [GPA / Honors if applicable])

## Language

* [Language]: [Level]
```

The final resume output file must start directly with `# [Applicant Name]`. It must not include YAML frontmatter, comments, metadata blocks, writing notes, or analysis.

After generating the files, output a brief **Modification Summary** separately in the chat in the **user's language** (e.g., Korean if the user is communicating in Korean, do not include in any output file):

```
## 📝 수정 요약 (Modification Summary)

### 주요 변경 사항
1. [Core Posting Requirement]에 맞추어 전문 요약(Professional Summary)을 수정했습니다.
2. [Company A]에서의 [Relevant Experience] 부분을 구체화하고 관련 핵심 키워드를 반영했습니다.
3. [Company B]에서의 덜 관련성 높은 업무들을 간소화했습니다.
4. 채용 공고 요구사항에 맞춰 Skills 섹션을 재구성했습니다.

### 표현 조정 (Reframing Points)
- "Robot fleet management" → "Real-time device monitoring and operational optimization"
- "B2B2C SaaS Platform" → "High-traffic processing and order/settlement systems"

### 특이 사항
- [Supply Chain Domain Experience]는 이력서에 직접적으로 나타내기 어려워 커버 레터에 작성하는 것을 추천합니다.
```

## Core Rules

- **No Fabrication**: Do not add experiences, skills, or certifications that are not in the original resume. All content must be based on the source document. Do not add unconfirmed content under "Learning", "Exploring", or "Interests" unless it was already present.
- **Casing & Spelling Consistency**: Ensure all technical terms and tool names strictly match industry-standard spelling and casing (e.g., PostgreSQL, Docker, Django).
- **Minimize Deletion**: Do not delete entire roles or projects; only adjust their weight.
- **Language Alignment**: Always write the resume in the language of the job posting (e.g., English posting → English resume). Maintain technical terms in their original form. If the user's language is different, translate the Modification Summary printed in the chat to the user's language.
- **Preserve Originals**: Always preserve original files. If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) instead of overwriting.
- **Specific Output Path**: Store results in the `results/resume-tailor/` directory.
- **Submission-Ready Output**: Always create a separate final resume output Markdown file and always attempt PDF conversion from that file. Never include frontmatter, summaries, analysis, source citations, or writing notes in the final resume output file or PDF.
- **Page Budget Compliance**: Adjust formatting, margins, and content length to guarantee the resume fits exactly within the page budget (1 or 2 pages) and does not spill orphan lines onto a new page.
