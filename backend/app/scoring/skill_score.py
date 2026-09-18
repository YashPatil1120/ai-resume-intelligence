# ==================================================
# SKILL SCORE
# ==================================================

def calculate_skill_score(
    required_skill_coverage,
    preferred_groups
):
    """
    Calculate the overall skill score.

    Required skills have higher importance than
    preferred skills.

    Required skill coverage:
        70% weight

    Preferred skill coverage:
        30% weight
    """

    required_score = float(
        required_skill_coverage
    )

    # --------------------------------------------------
    # Preferred skill coverage
    # --------------------------------------------------

    total_preferred = len(
        preferred_groups
    )

    if total_preferred == 0:

        preferred_score = 100.0

    else:

        satisfied_preferred = sum(
            1
            for group in preferred_groups
            if group.get("satisfied", False)
        )

        preferred_score = (
            satisfied_preferred
            / total_preferred
        ) * 100

    # --------------------------------------------------
    # Weighted skill score
    # --------------------------------------------------

    skill_score = (
        required_score * 0.70
        +
        preferred_score * 0.30
    )

    return round(
        skill_score,
        2
    )


if __name__ == "__main__":

    required_coverage = 100

    preferred_groups = [
        {"satisfied": True},
        {"satisfied": True},
        {"satisfied": False},
        {"satisfied": True},
        {"satisfied": False}
    ]

    score = calculate_skill_score(
        required_coverage,
        preferred_groups
    )

    print(
        f"Skill Score: {score}"
    )