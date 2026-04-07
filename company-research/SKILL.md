---
name: company-research
description: A skill that searches the web and summarizes key information about a company when the user shares a company name or job posting. Triggered when the user makes requests like "How is this company?", "Look up XX company", "Summarize company info for this posting", or "Please research this company for my application". Also includes extracting the company name from job posting URLs or text to conduct the research. Use this skill in all situations requiring company information, such as job change/search preparation, interview prep, and comparing companies.
---

# Company Research

Receives a company name or job posting, searches the web for key information about the company, and summarizes it.

## Workflow

### 1. Identify Company Name

- If the user directly inputs a company name: Use it as is.
- If a job posting URL or text is shared: Extract the company name from the posting.

### 2. Web Search

Utilize `WebSearch` and `WebFetch` to collect the information below. Search query examples:

- `"[Company Name] company overview"`
- `"[Company Name] funding investment"`
- `"[Company Name] tech stack engineering blog"`
- `"[Company Name] glassdoor reviews culture"`
- `"[Company Name] recent news 2025 2026"`

If the search results are insufficient, change the search query and try again. If it is a Korean company, also search in Korean.

### 3. Classify and Output Information

Classify and summarize into the categories below. If there is no information for a specific category, indicate "No information", but keep the section itself. This is so the user can know what information is lacking.

### 4. Save Results

Save the final summarized research result as a markdown file in the `company-research-results/` folder (e.g., `company-research-results/[YYYY-MM-DD]_[Company Name].md`). Create the folder if it does not exist. Include frontmatter at the top of the file. **If a file with the same name already exists, append a time-based suffix (e.g., `[YYYY-MM-DD]_[Company Name]_143000.md` or `_HHMMSS`) to preserve the original.**

## Output Template

```markdown
---
title: [Company Name]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
category: company-research
tags: [company-research, [Industry]]
---

## 🏢 [Company Name]

### 📌 Company Overview
- **Founded**: 2020
- **Headquarters**: Seoul, South Korea
- **Industry**: Fintech / Financial Services
- **Core Business**: Comprehensive financial platform including easy money transfers, investments, insurance, etc.
- **Mission/Vision**: (If public)

### 📊 Size
- **Employees**: ~3,000
- **Main Offices**: Seoul, US, etc.

### 💰 Funding & Financials
- **Total Funding**: $X M
- **Latest Round**: Series G ($X M, 2024)
- **Key Investors**: Sequoia, Altos Ventures, etc.
- **Public/Private**: Private

### 🛠 Tech Stack
- **Backend**: Kotlin, Spring Boot
- **Frontend**: React, TypeScript
- **Infrastructure**: AWS, Kubernetes
- **Other**: (Information gathered from engineering blogs, etc.)

### 🏗 Culture & Reputation
- **Organization Culture**: (Key keywords from Glassdoor, Blind, etc.)
- **Pros**: (Frequently mentioned positive factors)
- **Cons**: (Frequently mentioned negative factors)
- **Rating**: Glassdoor X.X/5

### 📰 Recent News
- [News Title 1] (2026.03)
- [News Title 2] (2026.01)
- [News Title 3] (2025.12)

### 💡 Interview Reference
- **Interview Process**: (If known)
- **Interview Difficulty**: (Based on Glassdoor)
- **Frequent Question Types**: (If known)
```

## Core Rules

- **Only include information confirmed through search.** Do not add guesses or generic content. Mark unverified items as "No information".
- **Prioritize information with clear sources.** Utilize reliable sources such as the official homepage, Crunchbase, LinkedIn, Glassdoor, and engineering blogs.
- **Prioritize the latest information.** If there is information from multiple points in time on the same topic, use the most recent one.
- **Language policy:** Summarize the output in the user's preferred language (the language they used to request the skill). Keep proper nouns such as company names and technical terms in their original language.
- For companies with scarce information, like startups, summarize as much as possible within the scope of what can be found, and be honest about what information is missing.
