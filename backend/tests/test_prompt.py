from backend.src.llm.prompt import build_prompt


def test_build_prompt_includes_resume_and_job_text():
    cv = "MY RESUME TEXT"
    job = "MY JOB TEXT"
    prompt = build_prompt(cv, job)
    assert cv in prompt
    assert job in prompt


