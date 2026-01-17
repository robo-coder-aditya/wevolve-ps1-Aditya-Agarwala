from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
from rapidfuzz import fuzz
from fastapi.responses import PlainTextResponse

app = FastAPI()


def normalize(s: str):
    return s.lower().strip()


# parsing the jobExperienceString
def parse_experience(exp_str: str):
    if not exp_str or not isinstance(exp_str, str):
        return None

    s = exp_str.lower().strip()

    import re

    # Case 1: range "0-2", "1 - 3"
    m = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        return {"min": int(m.group(1)), "max": int(m.group(2))}

    # Case 2: "3+ years", "5+"
    m = re.search(r"(\d+)\s*\+", s)
    if m:
        return {"min": int(m.group(1)), "max": 40}

    # Case 3: fresher / entry
    if "fresher" in s or "entry" in s:
        return {"min": 0, "max": 1}

    return None


class Candidate(BaseModel):
    skills: List[str]
    preferred_locations: List[str]
    preferred_roles: List[str]
    expected_salary: int
    experience_years: int


class Job(BaseModel):
    job_id: Any
    required_skills: List[str]
    location: str
    salary_range: List[int] | None = None
    experience_required: str | None = None
    title: str | None = None


class ApplicationInput(BaseModel):
    candidate: Candidate
    jobs: List[Job]


@app.post("/application")
def application(data: ApplicationInput):
    # candidate object parse
    candidate = data.candidate

    # jobs array parse
    jobs = data.jobs

    matches = []

    # take one job object at a time
    for job in jobs:
        # deducing required fields
        job_id = job.job_id

        missing_skills = []
        total_skills = len(job.required_skills)
        matched_skills = 0

        # skill matching with fuzzy
        for req_skill in job.required_skills:
            best = 0
            for cand_skill in candidate.skills:
                score = fuzz.partial_ratio(
                    normalize(req_skill),
                    normalize(cand_skill)
                )
                best = max(best, score)

            if best >= 80:
                matched_skills += 1
            else:
                missing_skills.append(req_skill)

        skill_match = 50
        if total_skills:
            skill_match = (matched_skills / total_skills) * 100

        # job requirement string
        job_location = job.location
        candidate_location = candidate.preferred_locations

        location_match = 0
        if job_location in candidate_location:
            location_match = 100
        elif job_location == "Remote":
            location_match = 80

        # int salary expected
        candidate_salary = candidate.expected_salary
        job_salary = job.salary_range
        salary_match = 50

        if isinstance(job_salary, list) and len(job_salary) == 2:
            if job_salary[0] <= candidate_salary <= job_salary[1]:
                salary_match = 100
            elif job_salary[0] > candidate_salary:
                diff = job_salary[0] - candidate_salary
                ratio = diff / job_salary[0]
                salary_match = max(0, 100 - ratio * 100)
            else:
                diff = candidate_salary - job_salary[1]
                ratio = diff / job_salary[1]
                salary_match = max(0, 100 - ratio * 100)

        job_experience = job.experience_required
        candidate_experience = candidate.experience_years
        experience_match = 0

        exp_range = parse_experience(job_experience)
        if exp_range is None:
            experience_match = 50
        else:
            min_r = exp_range["min"]
            max_r = exp_range["max"]

            if min_r <= candidate_experience <= max_r:
                experience_match = 100
            elif candidate_experience < min_r:
                diff = min_r - candidate_experience
                ratio = diff / min_r
                experience_match = max(0, 100 - ratio * 100)
            else:
                experience_match = 80

        role_match = 50
        if job.title:
            best = 0
            for role in candidate.preferred_roles:
                score = fuzz.partial_ratio(
                    normalize(role),
                    normalize(job.title)
                )
                best = max(best, score)
            role_match = best

        match_score = (
            0.4 * skill_match +
            0.2 * location_match +
            0.15 * salary_match +
            0.15 * experience_match +
            0.10 * role_match
        )
        match_score = round(match_score, 1)

        recommendation_reason = (
            f"Matching {matched_skills}/{total_skills} skills with a location score "
            f"of {location_match}, and experience score of {experience_match}"
        )

        if total_skills == 0:
            recommendation_reason = (
                f"Skill requirements not specified, location score of "
                f"{location_match} and experience score of {experience_match}"
            )

        match = {
            "job_id": job_id,
            "match_score": match_score,
            "breakdown": {
                "skill_match": skill_match,
                "location_match": location_match,
                "salary_match": salary_match,
                "experience_match": experience_match,
                "role_match": role_match
            },
            "missing_skills": missing_skills,
            "recommendation_reason": recommendation_reason
        }

        matches.append(match)

    return {"matches": matches}

@app.post("/explain/{job_id}", response_class=PlainTextResponse)
def explain_job(job_id: str, data: ApplicationInput):
    result = application(data)
    matches = result["matches"]

    for m in matches:
        if m["job_id"] == job_id:
            b = m["breakdown"]

            explanation = (
                f"Job ID {job_id} explanation:\n\n"
                f"Skills match: {b['skill_match']:.1f}% — "
                f"{len(m['missing_skills'])} skills missing.\n"
                f"Location match: {b['location_match']}%.\n"
                f"Experience match: {b['experience_match']}%.\n"
                f"Salary match: {b['salary_match']}%.\n"
                f"Role match: {b['role_match']}%.\n\n"
                f"Overall match score: {m['match_score']}%."
            )

            return explanation

    raise HTTPException(status_code=404, detail="Job not found")
