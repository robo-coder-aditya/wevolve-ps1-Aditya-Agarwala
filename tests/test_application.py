from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def payload():
    return {
        "candidate": {
            "skills": ["Python", "FastAPI", "Docker", "React"],
            "experience_years": 1,
            "preferred_locations": ["Bangalore", "Hyderabad"],
            "preferred_roles": ["Backend Developer"],
            "expected_salary": 800000
        },
        "jobs": [
            {
                "job_id": "J001",
                "title": "Backend Developer",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_required": "0-2 years",
                "location": "Bangalore",
                "salary_range": [600000, 1000000]
            }
        ]
    }

def test_application_endpoint():
    r = client.post("/application", json=payload())
    assert r.status_code == 200
    assert "matches" in r.json()

def test_match_score_range():
    r = client.post("/application", json=payload())
    score = r.json()["matches"][0]["match_score"]
    assert 0 <= score <= 100

def test_missing_skills_present():
    r = client.post("/application", json=payload())
    missing = r.json()["matches"][0]["missing_skills"]
    assert "PostgreSQL" in missing

def test_location_match_100():
    r = client.post("/application", json=payload())
    loc = r.json()["matches"][0]["breakdown"]["location_match"]
    assert loc == 100

def test_recommendation_reason_exists():
    r = client.post("/application", json=payload())
    reason = r.json()["matches"][0]["recommendation_reason"]
    assert isinstance(reason, str)
