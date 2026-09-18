# ==================================================
# OVERALL MATCH SCORE
# ==================================================

def calculate_overall_score(
    skill_score,
    experience_score,
    education_score,
    semantic_score
):
    """
    Calculate final resume-JD match score.

    Weights:

        Skill        = 45%
        Experience   = 25%
        Education    = 15%
        Semantic     = 15%

    Total = 100%
    """

    skill_score = float(
        skill_score
    )

    experience_score = float(
        experience_score
    )

    education_score = float(
        education_score
    )

    semantic_score = float(
        semantic_score
    )

    overall_score = (

        skill_score * 0.45

        +

        experience_score * 0.25

        +

        education_score * 0.15

        +

        semantic_score * 0.15

    )

    return round(
        min(
            max(
                overall_score,
                0.0
            ),
            100.0
        ),
        2
    )


if __name__ == "__main__":

    score = calculate_overall_score(
        skill_score=88.5,
        experience_score=0,
        education_score=100,
        semantic_score=76.2
    )

    print(
        f"Overall Match Score: "
        f"{score}"
    )