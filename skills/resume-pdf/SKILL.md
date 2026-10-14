---
name: resume-pdf
description: A skill that converts a Markdown resume into a print-ready, ATS-friendly A4 PDF with a clean typographic layout. Triggered when the user says things like "Convert my resume to PDF", "Export this resume as a PDF", "Make a PDF version of my CV", or "I need a PDF to attach to this application". Also use it after `resume-tailor` produces a tailored resume that the user wants to submit as a PDF file.
---

# Resume PDF

Renders a Markdown resume to a single-column A4 PDF that stays readable in print and
remains machine-parsable (real text, no images) so ATS systems can read it.

## Prerequisites

The conversion needs three tools. Check first and tell the user what is missing:

```bash
brew install pandoc                 # Markdown -> HTML
pip install weasyprint beautifulsoup4  # HTML -> PDF, HTML restructuring
```

`pdfinfo` (from `poppler`) is optional and only used to report the page count.

## Workflow

### 1. Locate the source resume

- Default to `resumes/[Name].md`.
- If the user points at a tailored resume, use that file
  (e.g. `results/resume-tailor/[YYYY-MM-DD]_[Name]_[Company]_tailored_resume.md`).
- Never edit the source Markdown to make it fit. Layout problems are solved in the
  stylesheet, not by rewriting the user's content.

### 2. Convert

```bash
python3 skills/resume-pdf/scripts/md_to_pdf.py "resumes/[Name].md" --fit-pages 2
```

Options:

| Option | Purpose |
| --- | --- |
| `-o, --output` | PDF path (default: next to the input, same basename) |
| `--base` | Body font size in pt; one knob that scales the whole layout (default `9.6`) |
| `--fit-pages N` | Shrink the layout in 0.2pt steps until it fits N pages (floor: 7.6pt) |

The PDF is written next to the source by default, so a resume in `resumes/` produces
`resumes/[Name].pdf`. Both directories are gitignored, so generated PDFs are not committed.

### 3. Check the result before reporting

Render the pages and look at them — do not assume the layout is fine:

```bash
pdftoppm -png -r 105 "resumes/[Name].pdf" /tmp/page   # then read /tmp/page-*.png
```

Verify:

- **Page count** — normally aim for 1-2 resume pages. Honor the user's requested
  page budget, including a separate recommendation page when requested. A stray
  line on an extra page is a defect, not an intentional appendix.
- **Readability at actual size** — inspect the body text, contact block, and stack
  lines at normal reading size, not only a zoomed preview. The converter's minimum
  font size is a technical limit, not a readability target.
- **Whitespace across all pages** — compare page density. If substantial unused
  space accompanies small text, increase `--base` first and rebalance page breaks.
  Preserve breathing room; do not stretch short sections just to fill a page.
- **Broken blocks** — keep headings with their following content and short bullets
  together. Avoid carrying a single line of a sentence onto the next page.

Adjust `--base`, line height, section spacing, margins, and page breaks as needed,
then re-render and inspect every page. `--fit-pages` only limits page count; it does
not enlarge undersized text or balance whitespace automatically.

## Expected Markdown structure

The script maps the resume conventions used in this repository onto the layout:

| Markdown | Rendered as |
| --- | --- |
| YAML frontmatter | Stripped |
| `# Name` + `**Title**` + contact line | Header block with a rule under it |
| `## Section` | Uppercase section heading with a hairline rule |
| `### Company \| Title` | Job heading; the following `*Location \| Dates*` line becomes its meta line |
| `* **Label:** value` under Technical Skills / Languages | Aligned label-value grid |
| `* *Stack: ...*` | Muted italic footer line under the role |
| Certifications + Education | Separate full-width sections in source order |
| Languages | Collapsed into a single inline line |

A resume that does not follow these conventions still converts — it simply falls back to
plain headings, paragraphs, and bullets.

## Styling

`assets/resume.css` holds the whole design: Charter for body text, Avenir Next for
headings and labels, and a navy accent (`#1a3a52`). Every size is expressed in `em`
relative to the body font size, so `--base` scales the document as a whole.

Treat the stylesheet and its default sizes as a starting point, not a fixed layout
to enforce. Prioritize readable text, clear hierarchy, balanced whitespace, and
natural page transitions. Follow a user-provided reference when available. Choose
the largest comfortable body size that fits the requested content and page budget;
do not preserve small text simply because it is the default. Around 11-12pt is a
useful starting range when space permits, not a mandatory size.

Use the existing converter rather than forking it. Keep document-specific layout
adjustments scoped to that output; change the shared stylesheet for reusable design
improvements or an explicitly requested default change.

Keep Certifications and Education stacked at full width by default, especially when
the page has room. Do not force a two-column layout to save space.

## Output Summary

Report to the user in the language of their request:

- The output path and page count.
- Any layout decision worth knowing (e.g. "increased body text to 11.2pt and
  rebalanced page breaks to reduce excess whitespace").
- Anything that could not be fixed by layout alone (e.g. the resume is too long for the
  requested page count and the content itself needs trimming).
