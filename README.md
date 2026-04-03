# Career Copilot Skills

Welcome to the **Career Copilot Skills** repository! This project contains powerful AI agent skills designed to automate and assist you with your job search and company research activities. 

By leveraging these skills, your AI assistant can autonomously browse job boards, analyze your personal resume, investigate corporate tech stacks, and generate beautifully formatted Markdown reports to accelerate your career advancement.

---

## 🛠 Available Skills

### 1. 🏢 Company Research (`company-research`)
A comprehensive intelligence skill that scours the web to build a detailed profile of any company or startup you are interested in.

*   **What it does:** Extracts key information such as the company's core business, funding rounds, engineering tech stack, employee culture (Glassdoor/Blind), and recent news.
*   **How to trigger:** Simply provide a company name or a job posting URL and say, *"Research this company"* or *"What can you tell me about [Company Name]?"*
*   **Output:** The skill will automatically summarize its findings and save a structured markdown report into the `company-research-results/` directory.

### 2. 🔍 Job Search (`job-search`)
A highly personalized job-hunting assistant that parses your resume to find the most suitable, active job postings across various platforms (e.g., LinkedIn, Indeed, Startup Job Boards).

*   **Initial Setup:** For the best experience, save your resume as a markdown file inside the `resumes/` folder (e.g., `resumes/John_Doe.md`). 
*   **What it does:** The skill analyzes your core competencies, seniority, and location preferences from your resume. It then fetches active job postings and evaluates your suitability (highlighting match points and potential gaps) for each role.
*   **How to trigger:** Say something like, *"Find backend jobs that fit my resume in Berlin,"* or *"Search the web for new job postings for me."*
*   **Output:** A curated list of recommended jobs and their match evaluations will be saved in the `job-search-results/` directory as a daily digest.

### 3. 📝 Job Fit Analyzer (`job-fit-analyzer`)
A quick analysis tool that deciphers lengthy job descriptions and extracts exactly what you need to know before applying.

*   **What it does:** Scrapes job posting pages and cleanly recategorizes all requirements into "Minimum" and "Preferred" qualifications (Education, Experience, Tech Skills, etc.).
*   **How to trigger:** Paste a URL for a job posting (like LinkedIn) and ask, *"Summarize the qualifications for this posting,"* or *"What do they need for this role?"*
*   **Output:** Generates a neatly organized markdown breakdown of the requirements and a match analysis with your resume. The result is automatically saved into the `job-fit-analyzer-results/` directory.

### 4. ✉️ Cover Letter Writer (`cover-letter`)
A personalized cover letter writing assistant that crafts tailored application letters based on your resume and a specific job posting.

*   **What it does:** Analyzes your resume and the target job posting, leverages any existing company research or job fit analysis results, and writes a compelling, position-specific cover letter. Strengths are highlighted, gaps are navigated with transferable skills, and company-specific details are woven in for differentiation.
*   **How to trigger:** Say things like, *"Write me a cover letter for this job,"* *"Draft a motivation letter for this posting,"* or *"I want to apply here — can you write a cover letter?"*
*   **Output:** A ready-to-send cover letter saved as `cover-letter-results/[YYYY-MM-DD]_[Name]_[Company]_cover_letter.md`, along with a brief writing notes summary in the chat.

### 5. 🛠️ Resume Tailor (`resume-tailor`)
A precision-tuning assistant that optimizes your base resume for a specific job posting by re-framing your experience through the lens of the target role.

*   **What it does:** Analyzes the gaps and strengths between your resume and the job requirements to highlight relevant achievements and incorporate target keywords. It strategically re-structures bullet points, emphasizes transferable skills, and de-emphasizes less relevant areas—all while strictly adhering to the factual history in your base resume (no fabrication).
*   **How to trigger:** Say things like, *"Tailor my resume for this position,"* *"Update my resume to fit this job,"* or *"Optimize my resume for this posting using [Resume_Name].md".*
*   **Output:** A newly generated, job-specific markdown resume saved as `resume-tailor-results/[YYYY-MM-DD]_[Name]_[Company]_tailored_resume.md`, along with a detailed modification summary in the chat.

---

## 🌍 Language Flexibility

All skills are built dynamically with multilingual support. The AI is instructed to summarize its findings in **your preferred language** (the language you used to trigger the skill) while retaining crucial proper nouns like technical terms and company names in their original formatting for maximum accuracy.

## 📂 Project Structure Overview

```text
career-copilot-skills/
├── company-research/          # Skill workflow for company research
├── company-research-results/  # (Auto-generated) Saved company reports
├── job-search/                # Skill workflow for job searching
├── job-search-results/        # (Auto-generated) Saved job match digests
├── job-fit-analyzer/          # Skill workflow for extracting qualifications
├── job-fit-analyzer-results/  # (Auto-generated) Saved qualifications and match analyses
├── cover-letter/              # Skill workflow for writing cover letters
├── cover-letter-results/      # (Auto-generated) Saved cover letters
├── resume-tailor/             # Skill workflow for tailoring resumes
├── resume-tailor-results/     # (Auto-generated) Saved tailored resumes
└── resumes/                   # Directory to store your personal markdown resumes
```