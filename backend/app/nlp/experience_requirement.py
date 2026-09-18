import re


# ==================================================
# EXPERIENCE REQUIREMENT EXTRACTION
# ==================================================

def extract_required_experience(job_description):
    """
    Extract the minimum required years of experience
    from a job description.

    Supports patterns such as:

        1 year of experience
        1+ years of experience
        at least 1 year of experience
        at least 1 year of professional experience
        2+ years of software development experience
        minimum 2 years of experience
        3 years professional experience
        experience of 4 years
    """

    text = job_description.lower()

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # ==================================================
    # 1. "AT LEAST X YEARS ... EXPERIENCE"
    # ==================================================

    patterns = [

        r"at\s+least\s+"
        r"(\d+(?:\.\d+)?)\+?\s*years?"
        r".{0,80}?\bexperience\b",

        # ==================================================
        # 2. "MINIMUM X YEARS ... EXPERIENCE"
        # ==================================================

        r"minimum\s+"
        r"(\d+(?:\.\d+)?)\+?\s*years?"
        r".{0,80}?\bexperience\b",

        # ==================================================
        # 3. "MINIMUM OF X YEARS ... EXPERIENCE"
        # ==================================================

        r"minimum\s+of\s+"
        r"(\d+(?:\.\d+)?)\+?\s*years?"
        r".{0,80}?\bexperience\b",

        # ==================================================
        # 4. "X YEARS OF ... EXPERIENCE"
        # ==================================================

        r"(\d+(?:\.\d+)?)\+?\s*years?"
        r".{0,80}?\bexperience\b",

        # ==================================================
        # 5. "X YEARS ... EXPERIENCE"
        # ==================================================

        r"(\d+(?:\.\d+)?)\+?\s*years?"
        r".{0,80}?\bexperience\b",

        # ==================================================
        # 6. "EXPERIENCE OF X YEARS"
        # ==================================================

        r"experience\s+of\s+"
        r"(\d+(?:\.\d+)?)\+?\s*years?"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            try:

                return float(
                    match.group(1)
                )

            except ValueError:

                continue

    return 0.0


# ==================================================
# EXPERIENCE REQUIREMENT CHECK
# ==================================================

def check_experience_requirement(
    candidate_years,
    required_years
):
    """
    Check whether candidate experience satisfies
    the minimum experience requirement.
    """

    if required_years <= 0:

        return True

    return candidate_years >= required_years


# ==================================================
# TERMINAL TEST
# ==================================================

if __name__ == "__main__":

    test_cases = [

        "At least 1 year of professional software development experience.",

        "Minimum 2 years of experience.",

        "Minimum of 3 years of professional experience.",

        "2+ years of software development experience.",

        "3 years professional experience.",

        "Experience of 4 years.",

        "At least 5 years of backend engineering experience.",

        "6+ years of full stack development experience."
    ]

    print()
    print("EXPERIENCE REQUIREMENT TEST")
    print("===========================")

    for text in test_cases:

        result = extract_required_experience(
            text
        )

        print()
        print(text)

        print(
            f"Required Years: {result}"
        )