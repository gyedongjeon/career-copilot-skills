# Career Copilot Skills

Welcome to the **Career Copilot Skills** repository! This project contains powerful AI agent skills designed to automate and assist you with your job search and company research activities. 

By leveraging these skills, your AI assistant can autonomously browse job boards, analyze your personal resume, investigate corporate tech stacks, and generate beautifully formatted Markdown reports to accelerate your career advancement.

---

## 🚀 Getting Started

Professional job tools are only as good as the data they use. To enable full resume-aware automation (Job Search, Job Fit Analyzer, Cover Letter, and Resume Tailor), simply **save your resume as a markdown file** inside the `resumes/` directory (e.g., `resumes/John_Doe.md`). 

The AI will automatically reference this file to provide personalized insights and tailored documents.

---

## 🛠 Available Skills

### Common Output File Rule
All skills save their outputs under `results/<skill-name>/` and preserve previously generated files. If an output file with the same name already exists, the agent appends a time-based suffix (e.g., `_HHMMSS`) instead of overwriting.

### 1. 🏢 Company Research (`company-research`)
A comprehensive intelligence skill that scours the web to build a detailed profile of any company or startup you are interested in.

*   **What it does:** Extracts key information such as the company's core business, funding rounds, engineering tech stack, employee culture (Glassdoor/Blind), and recent news.
*   **How to trigger:** Simply provide a company name or a job posting URL and say, *"Research this company"* or *"What can you tell me about [Company Name]?"*
*   **Output:** A complete company profile saved as `results/company-research/[YYYY-MM-DD]_[Company_Name].md`, along with a key findings summary in the chat.

### 2. 🔍 Job Search EU (`job-search-eu`)
A highly personalized job-hunting assistant for the European market that parses your resume to find the most suitable active job postings across EU-specific platforms (GermanTechJobs, Stepstone, Arbeitnow, Relocate.me) and global sites (LinkedIn, Indeed, DevJobsScanner).

*   **What it does:** Extracts core competencies from your resume, dynamically builds search queries for region-appropriate job boards, and evaluates your suitability for each posting — highlighting match points and gaps.
*   **How to trigger:** Say something like, *"Search for job postings in Europe,"* *"Find postings that fit my resume in Germany,"* or *"Are there any positions for me lately in London?"*
*   **Output:** A curated list of recommended jobs and their match evaluations saved as `results/job-search-eu/[YYYY-MM-DD]_[Applicant_Name]_[Country_or_City]_search_results.md`, highlighting the most suitable roles for you.

### 3. 📝 Job Fit Analyzer (`job-fit-analyzer`)
A quick analysis tool that deciphers lengthy job descriptions and extracts exactly what you need to know before applying.

*   **What it does:** Scrapes job posting pages and cleanly recategorizes all requirements into "Minimum" and "Preferred" qualifications (Education, Experience, Tech Skills, etc.).
*   **How to trigger:** Paste a URL for a job posting (like LinkedIn) and ask, *"Summarize the qualifications for this posting,"* or *"What do they need for this role?"*
*   **Output:** A structured qualification analysis and gap report saved as `results/job-fit-analyzer/[YYYY-MM-DD]_[Name]_[Company]_qualifications.md`, summarizing your fit for the role.

### 4. ✉️ Cover Letter Writer (`cover-letter`)
A personalized cover letter writing assistant that crafts tailored application letters based on your resume and a specific job posting.

*   **What it does:** Analyzes your resume and the target job posting, leverages any existing company research or job fit analysis results, and writes a compelling, position-specific cover letter. Strengths are highlighted, gaps are navigated with transferable skills, and company-specific details are woven in for differentiation.
*   **How to trigger:** Say things like, *"Write me a cover letter for this job,"* *"Draft a motivation letter for this posting,"* or *"I want to apply here — can you write a cover letter?"*
*   **Output:** A ready-to-send cover letter saved as `results/cover-letter/[YYYY-MM-DD]_[Name]_[Company]_cover_letter.md`, along with a brief writing notes summary in the chat.

### 5. 🛠️ Resume Tailor (`resume-tailor`)
A precision-tuning assistant that optimizes your base resume for a specific job posting by re-framing your experience through the lens of the target role.

*   **What it does:** Analyzes the gaps and strengths between your resume and the job requirements to highlight relevant achievements and incorporate target keywords. It strategically re-structures bullet points, emphasizes transferable skills, and de-emphasizes less relevant areas—all while strictly adhering to the factual history in your base resume (no fabrication).
*   **How to trigger:** Say things like, *"Tailor my resume for this position,"* *"Update my resume to fit this job,"* or *"Optimize my resume for this posting using [Resume_Name].md".*
*   **Output:** A newly generated, job-specific markdown resume saved as `results/resume-tailor/[YYYY-MM-DD]_[Name]_[Company]_tailored_resume.md`, along with a detailed modification summary in the chat.

### 6. 📄 Resume PDF (`resume-pdf`)
A rendering skill that turns any markdown resume in this repository into a print-ready, ATS-friendly A4 PDF.

*   **What it does:** Converts a markdown resume (your base resume or a tailored one) into a typographically clean PDF — aligned skill tables, side-by-side certifications and education, and an automatic size fit so the document lands on the page count you want without a stray trailing page.
*   **How to trigger:** Say things like, *"Convert my resume to PDF,"* *"Export this resume as a PDF,"* or *"I need a PDF version to attach to this application."*
*   **Output:** A PDF saved next to the source markdown (e.g. `resumes/[Name].pdf`), with the page count and any layout adjustments reported in the chat.
*   **Requires:** `pandoc`, `weasyprint`, and `beautifulsoup4` (see the skill's `SKILL.md`).

### 7. 👀 Company Watch (`company-watch`)
A watchlist skill that tracks companies using your main stack (e.g., Berlin startups using Django) and checks their own job feeds instead of job boards.

*   **What it does:** Searches job boards (LinkedIn, StepStone, XING, WeAreDevelopers, Arbeitnow) for your stack to discover hiring companies, builds a list of companies with evidence that they use your stack, records each company's careers page and applicant tracking system (Greenhouse, Lever, Ashby, Personio, JOIN, Workable, SmartRecruiters), and reads their live job feeds to report new matching openings since the last check.
*   **How to trigger:** Say things like, *"Find Berlin startups that use Django,"* *"Add companies to my watchlist,"* or *"Check my watchlist companies for new jobs."*
*   **Output:** The watchlist at `results/company-watch/watchlist.md` and check reports saved as `results/company-watch/[YYYY-MM-DD]_openings.md`, with new postings marked `NEW`.

---

## 🌍 Language Flexibility

All skills are built dynamically with multilingual support. The AI is instructed to summarize its findings in **your preferred language** (the language you used to trigger the skill) while retaining crucial proper nouns like technical terms and company names in their original formatting for maximum accuracy.

## 📂 Project Structure Overview

```text
career-copilot-skills/
├── skills/                    # All skill definitions (one folder per skill)
│   ├── company-research/      # Skill workflow for company research
│   ├── job-search-eu/         # Skill workflow for EU job searching
│   ├── job-fit-analyzer/      # Skill workflow for extracting qualifications
│   ├── cover-letter/          # Skill workflow for writing cover letters
│   ├── resume-tailor/         # Skill workflow for tailoring resumes
│   └── resume-pdf/            # Skill workflow + script for markdown → PDF rendering
├── results/                   # (Auto-generated, gitignored) All skill outputs, one folder per skill
│   ├── company-research/      # Saved company reports
│   ├── job-search-eu/         # Saved job match digests
│   ├── job-fit-analyzer/      # Saved qualifications and match analyses
│   ├── cover-letter/          # Saved cover letters
│   └── resume-tailor/         # Saved tailored resumes
└── resumes/                   # (Gitignored) Your personal markdown resumes; rendered PDFs land here too
```
