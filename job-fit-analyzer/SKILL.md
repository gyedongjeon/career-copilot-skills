---
name: job-fit-analyzer
description: A skill that categorizes and summarizes the minimum and preferred qualifications when a job posting link (e.g., LinkedIn) is shared. Triggered when the user pastes a job posting URL or asks things like "Summarize the qualifications for this posting", "This is a LinkedIn posting, what do I need?", or "What are the requirements to apply for this position?". Use this skill whenever understanding job requirements is necessary during a job search or career transition.
---

# Job Fit Analyzer

Receives a job posting link and categorizes its minimum and preferred qualifications neatly.

## Workflow

### 1. Fetch Posting Content

When the user shares a URL, use `WebFetch` to retrieve the page content.

For LinkedIn postings, there may be a login wall. If the content cannot be fetched properly:
- Ask the user to paste the job posting text directly.
- Guide them politely: "LinkedIn might require a login to view this. Could you please copy and paste the job posting text for me?"

### 2. Extract and Categorize Qualifications

Extract the qualifications from the posting and classify them into the categories below. If there is no content for a specific category, omit it.

**Categories:**
- Education
- Experience
- Technical Skills
- Certifications
- Language
- Other

### 3. Match Analysis with Resume

If a resume is available (e.g., located in the `resumes/` folder), compare the extracted job qualifications against the applicant's resume to provide a match analysis. Identify strengths, gaps, and an overall suitability evaluation (High/Medium/Low).

### 4. Organize and Save Results

Save the extracted qualifications AND the match analysis together into a single markdown file. **If a file with the same name already exists, append a time-based suffix (e.g., `_HHMMSS`) to preserve the original.**

**Save Path**: `job-fit-analyzer-results/[YYYY-MM-DD]_[Applicant_Name]_[Company_Name]_qualifications.md`

### 5. Output Format

Follow this template, including a frontmatter section at the top:

```markdown
---
title: Job Fit Analysis - [Company Name] ([Position Name])
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: job-fit-analysis
company: [Company Name]
position: [Position Name]
tags: [job-fit, analysis]
---

## 📋 [Company Name] - [Position Name]
**🔗 Link**: [Job Posting URL]

### ✅ Minimum Qualifications

**Education**
- Bachelor's degree in Computer Science or related field

**Experience**
- 3+ years in software development

**Technical Skills**
- 1+ programming languages like Python, Java
- REST API design experience

**Certifications**
- (Omit this section if not applicable)

---

### ⭐ Preferred Qualifications

**Experience**
- Experience operating large-scale distributed systems

**Technical Skills**
- Kubernetes, Docker experience
- AWS/GCP cloud platform experience

---

## 🔍 Resume Match Analysis

### 🟢 Strengths
- **Technical Skills**: Expert in Python and REST APIs.
- **Experience**: 5+ years of software development experience easily meets the requirement.

### 🟡 Gaps & Opportunities
- **Cloud Platform**: AWS/GCP experience is not explicitly mentioned on the resume.

**💡 Overall**: High Suitability. Strong technical and experience overlap with minor gaps in cloud tools.
```

## Core Rules

- **Language Policy**: Summarize the output in the user's preferred language (the language they used to request the skill). Keep proper nouns like technical terms (Python, Kubernetes, etc.) in their original language.
- Only outline what is explicitly stated in the posting. Do not guess or add generic requirements.
- If "Minimum" and "Preferred" are not clearly separated in the posting, examine the context. Classify "required/must" variations as Minimum Qualifications, and "preferred/nice to have/plus" variations as Preferred Qualifications.
- If years of experience are written as a range (e.g., 3-5 years), organize it based on the minimum value (e.g., 3+ years).
