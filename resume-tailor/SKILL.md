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
- For English resumes, use the applicant-confirmed English level when provided; otherwise, default to realistic **B1-B2 level**.
- Use simple, active sentence structures: usually one clear idea per sentence.
- Use common verbs such as "built", "led", "improved", "worked with", "designed", and "supported".
- Avoid overly advanced, flowery, or literary phrasing that the applicant cannot sustain in interviews.
- Technical terms from the job posting and resume must match the exact spelling and casing (e.g., PostgreSQL, Docker, Django).

### 5. Output

Create two Markdown files: one working draft for internal review metadata and one final resume output for submission. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to preserve existing versions.**

**Working Draft File**
- **Save Path**: `resume-tailor-results/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume.md`
- This file may include:
  - YAML frontmatter
  - the tailored resume
  - optional review metadata, source notes, or tailoring notes when useful
- This file is not the submission-ready resume.

**Final Resume Output File**
- Always save a separate submission-ready resume Markdown file.
- **Resume Output Save Path**: `resume-tailor-results/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.md`
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
- Always attempt to create a PDF version from the final resume output file.
- **PDF Save Path**: `resume-tailor-results/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_tailored_resume_output_en.pdf`
- Match the PDF suffix to the final resume output language (e.g., `_output_de.pdf` for a German output file).
- If PDF conversion fails because no local converter is available, say so in the final response and provide the final resume output Markdown path.
- Do not keep intermediate HTML or CSS files in `resume-tailor-results/` after the PDF is created. Temporary HTML/CSS files may be used during conversion, but delete them before finishing unless the user explicitly asks to keep them.
- Final saved artifacts should normally be only:
  - the working draft Markdown
  - the final resume output Markdown
  - the final resume output PDF

### 6. PDF Conversion Workflow

After creating the final resume output Markdown file, create a PDF using the first available method below.

**Preferred conversion order:**
1. `pandoc` with a PDF engine if available.
2. `weasyprint` if available.
3. Headless browser print-to-PDF if available.
4. Any existing project script or local converter that already supports Markdown or HTML to PDF.

**Installing a converter when missing:**
- If no PDF converter is available, try to install one only after user approval (e.g., on macOS, `brew install pandoc` if Homebrew is available).
- Do not silently install packages or download dependencies without the user's approval.
- After installation, rerun the PDF conversion and validation steps.

**PDF validation:**
- Confirm that the PDF file exists and is non-empty.
- If possible, check the page count and confirm that it fits the intended page budget.
- If the PDF exceeds the page budget, tighten content or styling and regenerate it.
- If the PDF cannot be created, keep the final resume output Markdown file and clearly report the conversion issue.
- After successful PDF validation, remove any generated `.html` or `.css` conversion files unless the user explicitly requested them.

### 7. Resume PDF Layout & Styling Rules

The PDF should follow the embedded style profile below. The skill must not depend on any external or local files for visual styling.

**Resume design profile:**
- A4, exactly 2 pages when the resume has 10+ years of experience.
- Large serif applicant name at the top left.
- Gray serif subtitle below the name.
- Compact two-line contact block below the subtitle; small icons are acceptable in the PDF/HTML output when available.
- No colored sidebars, cards, tables, full-width header blocks, decorative borders, or background colors.
- Section titles are uppercase, serif, underlined text. Do not use horizontal divider rules between sections.
- Body text is serif, black, left-aligned, and compact.
- Experience entries use one inline heading line: `Company | Location | Role | Dates`.
- Bullets are flat one-level bullets. Avoid nested bullets in the final PDF.
- Stack lines are normal bullets or short plain lines, not separate sub-sections.
- Do not add a location/date line or signature block to a resume/CV. These belong in a cover letter, not in the resume.

**Page and spacing constraints:**
- Default to a 2-page A4 PDF unless the user explicitly asks for 1 page.
- Use approximately 18-22mm top/bottom margins and 18-20mm left/right margins.
- Keep body text around 11-12pt with line-height around 1.25-1.35.
- Keep section spacing moderate: enough white space to scan, but not so much that bullets spill to a third page.
- Avoid orphan section headings or one-line spillover onto a new page. If this happens, tighten spacing or shorten less relevant bullets.

**Typography and structure:**
- Prefer a serif font family similar to the reference: `"Times New Roman", Times, Georgia, serif`.
- Use a sans-serif fallback only if serif rendering is unavailable.
- Applicant name: 28-32pt, normal weight, black.
- Subtitle: 18-21pt, normal weight, medium gray (`#666`).
- Section headings: 15-17pt, uppercase, normal weight, text underline.
- Experience heading lines: 12-13pt, sans-serif or clean serif, slightly emphasized but not oversized.
- Body bullets: 11-12pt serif, simple bullet marker, minimal indentation.

**HTML/CSS conversion requirement:**
- When converting to PDF, prefer generating a temporary intermediate HTML file from the final resume output and applying CSS that matches the resume design profile.
- Hide or avoid Markdown `<hr>` elements in the PDF output because the reference uses underlined headings rather than horizontal rules.
- If Markdown conversion creates nested lists, flatten them before PDF generation.
- Treat generated HTML/CSS as disposable conversion artifacts, not final deliverables.

**Suggested CSS for the reference-like PDF:**
```css
@page {
  size: A4;
  margin: 19mm 19mm 18mm;
}

body {
  color: #000;
  font-family: "Times New Roman", Times, Georgia, serif;
  font-size: 11.5pt;
  line-height: 1.3;
}

h1 {
  font-size: 30pt;
  font-weight: 400;
  line-height: 1.1;
  margin: 0 0 10px;
}

.subtitle {
  color: #666;
  font-size: 20pt;
  margin: 0 0 34px;
}

.contact {
  font-size: 11.5pt;
  line-height: 1.55;
  margin-bottom: 26px;
}

h2 {
  border: 0;
  font-size: 16pt;
  font-weight: 400;
  margin: 24px 0 7px;
  padding: 0;
  text-decoration: underline;
  text-transform: uppercase;
}

h3 {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12.3pt;
  font-weight: 400;
  margin: 18px 0 4px;
}

p {
  margin: 0 0 7px;
}

ul {
  margin: 0 0 12px;
  padding-left: 0;
  list-style-position: inside;
}

li {
  margin: 0 0 4px;
}

hr {
  display: none;
}

a {
  color: #0645ad;
}

```

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

* Backend & Frameworks: [Backend languages/frameworks]
* Frontend & Web: [Frontend/web skills if relevant]
* Database & Data Modeling: [Database list]
* Cloud & Infrastructure: [DevOps/Cloud details]
* Methodologies: [Methodologies/soft skills]

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

* Backend & Frameworks: [Backend languages/frameworks]
* Frontend & Web: [Frontend/web skills if relevant]
* Database & Data Modeling: [Database list]
* Cloud & Infrastructure: [DevOps/Cloud details]
* Methodologies: [Methodologies/soft skills]

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
- **Specific Output Path**: Store results in the `resume-tailor-results/` directory.
- **Submission-Ready Output**: Always create a separate final resume output Markdown file and always attempt PDF conversion from that file. Never include frontmatter, summaries, analysis, source citations, or writing notes in the final resume output file or PDF.
- **Page Budget Compliance**: Adjust formatting, margins, and content length to guarantee the resume fits exactly within the page budget (1 or 2 pages) and does not spill orphan lines onto a new page.
