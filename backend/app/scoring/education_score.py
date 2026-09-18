# ==================================================
# EDUCATION SCORE
# ==================================================

def calculate_education_score(
    education
):
    """
    Calculate education score.

    Education is evaluated using:

        1. Required education level
        2. Required education field

    The score represents how closely the candidate's
    education satisfies the job requirement.
    """

    required_levels = set(
        education.get(
            "required_levels",
            []
        )
    )

    candidate_levels = set(
        education.get(
            "candidate_levels",
            []
        )
    )

    required_fields = set(
        education.get(
            "required_fields",
            []
        )
    )

    candidate_fields = set(
        education.get(
            "candidate_fields",
            []
        )
    )

    education_groups = education.get(
        "required_education_groups",
        []
    )

    # --------------------------------------------------
    # LEVEL SCORE
    # --------------------------------------------------

    if not required_levels:

        level_score = 100.0

    else:

        level_matched = (
            len(
                required_levels
                .intersection(
                    candidate_levels
                )
            )
            > 0
        )

        level_score = (
            100.0
            if level_matched
            else 0.0
        )

    # --------------------------------------------------
    # FIELD SCORE
    # --------------------------------------------------

    field_requirements_exist = (
        bool(required_fields)
        or
        bool(education_groups)
    )

    if not field_requirements_exist:

        field_score = 100.0

    else:

        normal_field_matched = (
            not required_fields
            or
            bool(
                required_fields.intersection(
                    candidate_fields
                )
            )
        )

        group_requirements_satisfied = all(
            group.get(
                "satisfied",
                False
            )
            for group in education_groups
        )

        field_satisfied = (
            normal_field_matched
            and
            group_requirements_satisfied
        )

        field_score = (
            100.0
            if field_satisfied
            else 0.0
        )

    # --------------------------------------------------
    # FINAL EDUCATION SCORE
    # --------------------------------------------------

    education_score = (
        level_score * 0.50
        +
        field_score * 0.50
    )

    return round(
        education_score,
        2
    )


if __name__ == "__main__":

    education = {
        "candidate_levels": [
            "bachelor"
        ],
        "candidate_fields": [
            "computer science"
        ],
        "required_levels": [
            "bachelor"
        ],
        "required_fields": [],
        "required_education_groups": [
            {
                "fields": [
                    "computer science",
                    "software engineering"
                ],
                "satisfied": True
            }
        ]
    }

    print(
        f"Education Score: "
        f"{calculate_education_score(education)}"
    )