# JobEngine – Intelligent Job–Candidate Matching API

JobEngine is a backend service that evaluates how well a candidate matches available job postings using skill similarity, location preference, experience fit, salary alignment, and role relevance.  
The system also provides a human-readable explanation for each match decision.

This project is built as a REST API and focuses on clean logic, explainability, and testability.

---

## Features

- Skill matching using fuzzy string comparison  
- Weighted scoring based on:
  - Skills
  - Location
  - Experience
  - Salary
  - Role relevance
- Plain-text explanation for match decisions
- Fully unit tested core logic
- Deployed and publicly accessible API

---

## Tech Stack

- **FastAPI** – backend framework
- **Pydantic** – request validation and type safety
- **RapidFuzz** – fuzzy skill and role matching
- **Pytest** – unit testing
- **Render** – deployment and hosting

---

## API Documentation

### POST `/application`

Evaluates a candidate against multiple job postings and returns a structured match score for each job.

#### Request Body (JSON)
- Candidate profile (skills, experience, preferences)
- List of job postings
- Example of request Body:-
      {
      "candidate": {
      "skills": ["Python", "FastAPI", "Docker", "React"],
      "experience_years": 1,
      "preferred_locations": ["Bangalore", "Hyderabad"],
      "preferred_roles": ["Backend Developer", "Full Stack Developer"],
      "expected_salary": 800000,
      "education": {
      "degree": "B.Tech",
      "field": "Computer Science",
      "cgpa": 8.5
      }
      },
      "jobs": [
      {
      "job_id": "J001",
      "title": "Backend Developer",
      "required_skills": ["Python", "FastAPI", "PostgreSQL"],
      "experience_required": "0-2 years",
      "location": "Bangalore",
      "salary_range": [600000, 1000000],
      "company": "TechCorp"
      }
      ]
      }

#### Response
- Overall match score per job
- Individual score breakdown:
  - Skill match
  - Location match
  - Experience match
  - Salary match
  - Role match
- Missing skills (if any)
- Recommendation reason
- Example response Body:-
    Output Specifications:
    {
    "matches": [
    {
    "job_id": "J001",
    "match_score": 85.5,
    "breakdown": {
    "skill_match": 75,
    "location_match": 100,
    "salary_match": 90,
    "experience_match": 100,
    "role_match": 95
    },
    "missing_skills": ["PostgreSQL"],
    "recommendation_reason": "Strong skill alignment with 3/3 matching skills."
    }
    ]
    }

---

### POST `/explain/{job_id}`

Returns a **human-readable explanation** describing why a candidate matched (or didn’t match) a specific job.

#### Response
Plain-text explanation including:
- Skill match percentage
- Location compatibility
- Experience suitability
- Salary alignment
- Role relevance
- Final match score
- Example response body:-

    Job ID J001 explanation:
    
    Skills match: 66.7% — 1 skills missing.
    Location match: 100%.
    Experience match: 100%.
    Salary match: 100%.
    Role match: 100.0%.
    
    Overall match score: 86.7%.

---

### Interactive API Docs (Swagger)

FastAPI automatically generates interactive documentation.

👉 **Swagger UI:**  
https://jobengine-5mhe.onrender.com/docs

Judges can directly test all endpoints from the browser.

---

## Running Tests

The core matching and explanation logic is covered using unit tests written with **Pytest**.

To run all tests locally:

```bash
pytest


## Running Locally

```bash
git clone https://github.com/robo-coder-aditya/wevolve-ps1-Aditya-Agarwala.git
cd wevolve-ps1-Aditya-Agarwala
pip install -r requirements.txt
uvicorn app.main:app --reload
