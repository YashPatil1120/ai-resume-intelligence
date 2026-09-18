# ==================================================
# SCORE ENGINE
# ==================================================

from app.scoring.skill_score import (
    calculate_skill_score
)

from app.scoring.experience_score import (
    calculate_experience_score
)

from app.scoring.education_score import (
    calculate_education_score
)

from app.scoring.semantic_score import (
    calculate_semantic_score
)

from app.scoring.overall_score import (
    calculate_overall_score
)


# ==================================================
# MAIN SCORE CALCULATION
# ==================================================

def calculate_scores(
    analysis_result
):
    """
    Calculate all resume-JD scores from the output
    of the Decision Engine.

    IMPORTANT:

    This function does NOT contain any hard-coded
    candidate data.

    It receives the actual analysis result generated
    from the user's uploaded resume and job description.

    Input:
        analysis_result

    Output:
        calculated scores
    """

    # ==================================================
    # 1. REQUIRED SKILL COVERAGE
    # ==================================================

    required_skill_coverage = float(
        analysis_result.get(
            "required_skill_coverage",
            0.0
        )
    )

    # ==================================================
    # 2. PREFERRED SKILL GROUPS
    # ==================================================

    preferred_groups = analysis_result.get(
        "preferred_skill_groups",
        []
    )

    # ==================================================
    # 3. SKILL SCORE
    # ==================================================

    skill_score = calculate_skill_score(
        required_skill_coverage,
        preferred_groups
    )

    # ==================================================
    # 4. EXPERIENCE
    # ==================================================

    experience = analysis_result.get(
        "experience",
        {}
    )

    candidate_years = float(
        experience.get(
            "candidate_years",
            0.0
        )
    )

    required_years = float(
        experience.get(
            "required_years",
            0.0
        )
    )

    # ==================================================
    # 5. EXPERIENCE SCORE
    # ==================================================

    experience_score = calculate_experience_score(
        candidate_years,
        required_years
    )

    # ==================================================
    # 6. EDUCATION
    # ==================================================

    education = analysis_result.get(
        "education",
        {}
    )

    # ==================================================
    # 7. EDUCATION SCORE
    # ==================================================

    education_score = calculate_education_score(
        education
    )

    # ==================================================
    # 8. SEMANTIC EVIDENCE
    # ==================================================

    requirement_evidence = analysis_result.get(
        "requirement_evidence",
        []
    )

    # ==================================================
    # 9. SEMANTIC SCORE
    # ==================================================

    semantic_score = calculate_semantic_score(
        requirement_evidence
    )

    # ==================================================
    # 10. OVERALL SCORE
    # ==================================================

    overall_match_score = calculate_overall_score(
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
        semantic_score=semantic_score
    )

    # ==================================================
    # 11. RETURN SCORES
    # ==================================================

    return {
        "required_skill_coverage":
            round(
                required_skill_coverage,
                2
            ),

        "skill_score":
            round(
                skill_score,
                2
            ),

        "experience_score":
            round(
                experience_score,
                2
            ),

        "education_score":
            round(
                education_score,
                2
            ),

        "semantic_score":
            round(
                semantic_score,
                2
            ),

        "overall_match_score":
            round(
                overall_match_score,
                2
            )
    }


# ==================================================
# TERMINAL TEST
# ==================================================

if __name__ == "__main__":

    # --------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------
    #
    # We do NOT create a fake resume here.
    #
    # We use the actual Decision Engine.
    #
    # This means:
    #
    #     data/resume.txt
    #
    # and
    #
    #     data/job_description.txt
    #
    # are analyzed first.
    #
    # Then their actual result is passed to the
    # Score Engine.
    # --------------------------------------------------

    from app.nlp.decision_engine import (
        analyze_resume
    )

    # --------------------------------------------------
    # LOAD RESUME
    # --------------------------------------------------

    with open(
        "data/resume.txt",
        "r",
        encoding="utf-8"
    ) as file:

        resume = file.read()

    # --------------------------------------------------
    # LOAD JOB DESCRIPTION
    # --------------------------------------------------

    with open(
        "data/job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    # --------------------------------------------------
    # RUN DECISION ENGINE
    # --------------------------------------------------

    analysis_result = analyze_resume(
        resume,
        job_description
    )

    # --------------------------------------------------
    # RUN SCORE ENGINE
    # --------------------------------------------------

    scores = calculate_scores(
        analysis_result
    )

    # ==================================================
    # DISPLAY
    # ==================================================

    print()
    print(
        "RESUME SCORE ENGINE"
    )

    print(
        "==================="
    )

    print()

    print(
        f"Required Skill Coverage: "
        f"{scores['required_skill_coverage']:.2f}%"
    )

    print(
        f"Skill Score: "
        f"{scores['skill_score']:.2f}"
    )

    print(
        f"Experience Score: "
        f"{scores['experience_score']:.2f}"
    )

    print(
        f"Education Score: "
        f"{scores['education_score']:.2f}"
    )

    print(
        f"Semantic Score: "
        f"{scores['semantic_score']:.2f}"
    )

    print(
        f"Overall Match Score: "
        f"{scores['overall_match_score']:.2f}"
    )

    print()

    print(
        f"Eligibility: "
        f"{analysis_result['eligibility']}"
    )