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
- For English cover letters, ask the applicant's preferred English level before writing when it is not already known.
- If the applicant does not answer, the information is unavailable, or the user asks to proceed without specifying a level, write at a **B1-B2 English level** by default. The letter should sound like something the applicant can naturally explain in an interview.
- Prefer short, clear sentences over polished corporate phrasing. Avoid idioms, complex grammar, long clauses, and overly sophisticated vocabulary.

## Workflow

### 1. Gather Inputs

**Resume:**
- Read `resumes/[Name].md` as the default
- If the user specifies a different resume, use that file instead

**Job Posting:**
- If shared as text in the conversation, use it as-is
- If a URL is provided, fetch the content using `WebFetch`

**Applicant English Level:**
- Before creating an English main draft, final submission copy, or PDF, check whether the applicant's preferred English level is already known from the conversation or available applicant notes.
- If it is not known, ask the user for the desired English level or whether to use the default B1-B2 level.
- If the user does not provide an answer, wants to proceed quickly, or no reliable information exists, use B1-B2 by default.
- Do not use advanced C1-C2 phrasing unless the user explicitly asks for it.

**Applicant Contact Block:**
- Before creating the main draft or submission-ready cover letter, confirm the applicant's address and contact details with the user.
- Required fields:
  - Applicant street address
  - Applicant postal code
  - Applicant city and country
  - Applicant email
  - Applicant phone number
- Do not guess, infer, or reuse stale applicant contact details unless the user explicitly confirms them for this application.
- If any required applicant contact field is missing, ask the user for the missing details before producing the main draft, final submission copy, or PDF.

**Company Address Block:**
- Look up the company's current office or registered address on the internet before creating the draft and submission-ready cover letters.
- Prefer official company sources first, such as the company website, legal notice/imprint, contact page, LinkedIn company page, or official registry entry.
- For Berlin-based applications, verify the Berlin office address when available. For example, for **Engelhart Commodities Trading Partners**, do not leave placeholders such as `[Company Street Address]` or `[Company Postal Code] Berlin, Germany`; search online and fill in the verified company address.
- Do not collect company phone numbers, company email addresses, or generic contact page URLs unless the user explicitly asks for them.
- Record the exact source URL and source label for the company address so the user can cross-check it later.
- If multiple plausible addresses exist, use the address most clearly tied to the hiring location or job posting and include the alternate source(s) in the draft notes for cross-checking.
- If no reliable address can be verified, ask the user whether to use the posting's location-only company block or a specific address they provide.

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

**English Level & Readability:**
- For English postings, use the applicant-confirmed English level when provided.
- If no English level is confirmed, keep the English at **B1-B2 level** by default.
- Use simple sentence structures: usually one idea per sentence.
- Keep most sentences under 20 words.
- Use common verbs such as "built", "led", "improved", "worked with", "helped", "designed", and "supported".
- Avoid phrases that may sound unnatural in an interview, such as "I am deeply passionate about leveraging synergies" or "I thrive at the intersection of".
- Technical terms from the job posting and resume are allowed (e.g., Python, AWS ECS, PostgreSQL, Docker), but surrounding explanations should remain simple.

### 4. Output

Save the cover letter as a markdown file with a frontmatter section.

- **Save Path**: `results/cover-letter/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_cover_letter.md`
- The main draft file may include the cover letter, Korean translation when required, and review metadata.
- In the main draft file, include the confirmed applicant contact block and researched company address block before the letter body so the user can review them.
- In the main draft file, put the source directly next to the company address line. This makes cross-checking easy without collecting unnecessary company contact details.
- The company address line must include:
  - The verified address
  - The source name, such as official locations page, legal notice/imprint, LinkedIn, registry, or job posting
  - The source URL
  - The date checked
- Do not include company phone, company email, or contact page fields in the main draft unless the user explicitly asks for them.
- Do not include source citations in the English-only submission copy or PDF unless the user explicitly asks for them.
- Also save a separate English-only submission copy that is easy to convert to PDF.
- **English Submission Save Path**: `results/cover-letter/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_cover_letter_submission_en.md`
- The English submission copy must contain only:
  - The English cover letter
  - No frontmatter
  - No translation
  - No writing notes
  - No analysis
  - No extra explanations
- Format the English submission copy for clean PDF export:
  - Use plain Markdown only.
  - Follow the `English Submission Template` below.
  - Include the applicant block, company block, location/date line, application title, greeting, body, and signature.
  - Fill the applicant block only with user-confirmed address and contact details.
  - Fill the company block with a verified company address found through internet research, using official or high-confidence sources where possible.
  - Never leave address placeholders such as `[Applicant Street Address]`, `[Company Street Address]`, or `[Company Postal Code]`.
  - Keep applicant and company address blocks left-aligned in Markdown; do not use HTML alignment for those blocks unless the user explicitly asks for it.
  - Right-align the location/date line in the PDF and any HTML conversion output. In plain Markdown, keep the location/date line as a normal standalone line unless the converter supports clean right alignment.
  - Bold only the applicant name and company name in the address blocks. Keep the rest of the address/contact lines plain.
  - Avoid tables, footnotes, comments, and long headings.
  - Keep the letter compact enough for one page.
  - Use the applicant-confirmed English level when available; otherwise use the default B1-B2 readability rules.
- Always attempt to create a PDF version from the English submission copy.
- **PDF Save Path**: `results/cover-letter/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_cover_letter_submission_en.pdf`
- If PDF conversion fails because no local converter is available, say so in the final response and provide the English submission markdown path.

### 5. PDF Conversion Workflow

After creating the English submission markdown file, create a PDF using the first available method below.

**Preferred conversion order:**
1. `pandoc` with a PDF engine if available.
2. `weasyprint` if available.
3. Headless browser print-to-PDF if available.
4. Any existing project script or local converter that already supports Markdown or HTML to PDF.

**Installing a converter when missing:**
- If no PDF converter is available, try to install one only after user approval.
- Prefer installing `pandoc` when a local package manager is available.
- On macOS, prefer `brew install pandoc` if Homebrew is available.
- If using `pandoc` requires a missing PDF engine, either:
  - use an available HTML-based route, or
  - ask before installing a large TeX distribution.
- Do not silently install packages or download dependencies without the user's approval.
- After installation, rerun the PDF conversion and validation steps.

**PDF preparation rules:**
- The PDF must be generated from the English submission content only.
- The saved English submission markdown must not contain frontmatter, so the PDF conversion can use it directly.
- Do not include Korean translation, writing notes, analysis, or metadata comments.
- Preserve the applicant/company block, location/date line, title, greeting, body, signature space, and applicant name.
- If a signature image path is provided by the user, include it between `Sincerely,` and the applicant name.
- If no signature image is provided, preserve clear vertical space between `Sincerely,` and the applicant name.
  - Use about 36-48px vertical space for a handwritten signature area.
  - Do not rely only on blank Markdown lines, because PDF converters may collapse them.
  - When generating HTML, use a dedicated `.signature-space` block between `Sincerely,` and the applicant name.
- Use simple one-page styling:
  - A4 page size
  - readable body font size around 11-11.5pt
  - **default to a serif font: `"Times New Roman", Times, Georgia, serif`**. A serif face reads like a printed letter and matches the resume PDF produced by the `resume-tailor` skill, so the resume, cover letter, and any references page look like one set
  - use a sans-serif font (`Aptos`, `Calibri`, `Arial`, `Helvetica Neue`) only if the user explicitly asks for it
  - use the same font family consistently throughout the PDF; the subject line may be bold but stays in the same family
  - links (e.g., a GitHub example) should be visible but plain: blue text, no underline
  - make the applicant name and company name in the address blocks bold, but do not enlarge them heavily
  - style the application subject line, e.g. `Application for Software Engineer, Python`, slightly larger than body text
  - subject line should be around 12-13pt, bold, with modest spacing before and after
  - right-align the location/date line, e.g. `Berlin, 29 May 2026`
  - leave clear vertical space between the right-aligned location/date line and the subject line; use about 18-24px or two blank Markdown lines
  - keep the subject line professional; do not make it look like a large document title
  - comfortable margins around 18-25mm
  - left-aligned text

**Suggested commands, depending on available tools:**

```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

```bash
weasyprint input.html output.pdf
```

For `pandoc`, the saved English submission markdown should be used directly because it has no YAML frontmatter.
When generating HTML/CSS for PDF conversion, explicitly set the font family, for example:

```css
body {
  font-family: "Times New Roman", Times, Georgia, serif;
  font-size: 11.5pt;
  line-height: 1.35;
}

.application-subject {
  font-size: 13pt;
  font-weight: 700;
  margin-top: 22px;
  margin-bottom: 14px;
}

.signature-space {
  height: 44px;
}

a {
  color: #0645ad;
  text-decoration: none;
}
```

When generating HTML for PDF conversion, use a dedicated class for the subject line instead of relying only on generic Markdown bold styling.
Also use a dedicated `.signature-space` block for the signature area instead of relying only on blank lines.

**PDF validation:**
- Confirm that the PDF file exists and is non-empty.
- If possible, check the page count and confirm it is one page.
- If installation is declined or the PDF still cannot be created, keep the markdown submission file and clearly report the missing converter or conversion error.

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

[Applicant Contact]
- Name: [Applicant Name]
- Address: [Applicant Street Address], [Applicant Postal Code] [Applicant City], [Applicant Country]
- Email: [Applicant Email]
- Phone: [Applicant Phone]

[Company Address]
- Company: [Company Name]
- Recipient: [Hiring Manager Name or Hiring Team]
- Address: [Company Street Address], [Company Postal Code] [Company City], [Company Country] (source: [Source Name], [Source URL], checked [YYYY-MM-DD])

[Follow cover letter structure]
```

## English Submission Template

```markdown
**[Applicant Name]**  
[Applicant Street Address]  
[Applicant Postal Code] [Applicant City], [Applicant Country]  
Email: [Applicant Email] | Phone: [Applicant Phone]

**[Company Name]**  
[Hiring Manager Name or Hiring Team]  
[Company Street Address]  
[Company Postal Code] [Company City], [Company Country]

[Applicant City], [Date]

**Application for [Position Title]**

Dear [Hiring Manager Name or Hiring Team],

[English cover letter body only]

Sincerely,  

[Signature Image or Signature Space]

[Applicant Name]
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
- **Interview consistency**: The English should match the applicant-confirmed level. If no level is confirmed, default to realistic B1-B2 English. Do not make the applicant sound more fluent, literary, or corporate than they can likely sustain in interviews.
- **Submission-ready output**: Always create an English-only submission markdown file and always attempt PDF conversion. Never include Korean translation or writing notes in the submission copy or PDF.
