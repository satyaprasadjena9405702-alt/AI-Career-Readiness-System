from utils import (
    detect_skills,
    calculate_skill_coverage,
    get_skill_gap,
    validate_resume_text,
     calculate_job_match_score
)


def test_detect_skills():

    resume = "I know Python and SQL."

    result = detect_skills(
        resume,
        ["Python", "Java", "SQL"]
    )

    assert result == ["Python", "SQL"]


def test_skill_coverage():

    result = calculate_skill_coverage(
        ["Python", "SQL"],
        ["Python", "SQL", "Java", "Git"]
    )

    assert result == 50


def test_skill_gap():

    matched, missing = get_skill_gap(
        ["Python", "SQL"],
        ["Python", "SQL", "Java"]
    )

    assert matched == ["Python", "SQL"]
    assert missing == ["Java"]


def test_empty_required_skills():

    result = calculate_skill_coverage(
        ["Python"],
        []
    )

    assert result == 0
    
def test_java_and_javascript_detection():

    resume = "I have experience in JavaScript."

    result = detect_skills(
        resume,
        ["Java", "JavaScript"]
    )

    assert result == ["JavaScript"]
def test_special_character_skills():

    resume = "I know C++, C# and .NET."

    result = detect_skills(
        resume,
        ["C++", "C#", ".NET", "Java"]
    )

    assert result == ["C++", "C#", ".NET"]
def test_validate_resume_text():

    assert validate_resume_text("My resume content") == True
    assert validate_resume_text("") == False
    assert validate_resume_text("   ") == False
def test_job_match_score():
    assert calculate_job_match_score(28.22, 100) == 56.93


def test_job_match_score_zero():
    assert calculate_job_match_score(0, 0) == 0.0


def test_job_match_score_full():
    assert calculate_job_match_score(100, 100) == 100.0
