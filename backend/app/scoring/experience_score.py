# ==================================================
# EXPERIENCE SCORE
# ==================================================

def calculate_experience_score(
    candidate_years,
    required_years
):
    """
    Calculate experience score.

    If no experience is required:
        score = 100

    If candidate meets or exceeds the requirement:
        score = 100

    Otherwise:
        score is proportional to the requirement.

    Example:

        Required = 2 years
        Candidate = 1 year

        Score = 50
    """

    candidate_years = max(
        0.0,
        float(candidate_years)
    )

    required_years = max(
        0.0,
        float(required_years)
    )

    # --------------------------------------------------
    # No experience requirement
    # --------------------------------------------------

    if required_years == 0:

        return 100.0

    # --------------------------------------------------
    # Requirement satisfied
    # --------------------------------------------------

    if candidate_years >= required_years:

        return 100.0

    # --------------------------------------------------
    # Partial experience
    # --------------------------------------------------

    score = (
        candidate_years
        /
        required_years
    ) * 100

    return round(
        min(score, 100.0),
        2
    )


if __name__ == "__main__":

    print(
        calculate_experience_score(
            0,
            2
        )
    )

    print(
        calculate_experience_score(
            1,
            2
        )
    )

    print(
        calculate_experience_score(
            2,
            2
        )
    )

    print(
        calculate_experience_score(
            4,
            2
        )
    )