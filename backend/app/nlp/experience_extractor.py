import re
from datetime import datetime


# ==================================================
# EXPERIENCE EXTRACTION
# ==================================================

def extract_explicit_years(text):
    """
    Extract explicitly stated years of professional
    experience from resume text.

    Examples:
        "3 years of experience"
        "3+ years experience"
        "experience of 4 years"

    Returns
    -------
    float
        Explicitly stated years of experience.
        Returns 0 if nothing is found.
    """

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+professional\s+experience",

        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+experience",

        r"(\d+(?:\.\d+)?)\+?\s*years?\s+experience",

        r"experience\s+of\s+(\d+(?:\.\d+)?)\+?\s*years?"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return float(match.group(1))

    return 0.0


# ==================================================
# DATE PARSING
# ==================================================

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12
}


def parse_date(date_text):
    """
    Convert a month/year or year-only string
    into a (year, month) tuple.

    Examples:
        "Jan 2024" -> (2024, 1)
        "January 2024" -> (2024, 1)
        "2024" -> (2024, 1)
    """

    date_text = date_text.strip().lower()

    # ----------------------------------------------
    # MONTH + YEAR
    # ----------------------------------------------

    match = re.search(
        r"\b([a-z]+)\s+(\d{4})\b",
        date_text
    )

    if match:

        month_name = match.group(1)
        year = int(match.group(2))

        if month_name in MONTHS:

            return (
                year,
                MONTHS[month_name]
            )


    # ----------------------------------------------
    # YEAR ONLY
    # ----------------------------------------------

    match = re.search(
        r"\b(\d{4})\b",
        date_text
    )

    if match:

        return (
            int(match.group(1)),
            1
        )

    return None


# ==================================================
# DATE RANGE EXTRACTION
# ==================================================

def extract_date_ranges(text):
    """
    Extract employment-style date ranges.

    Supported formats:

        Jan 2024 - Mar 2026
        June 2023 - Present
        2022 - 2024
        2023 - Current
        Jan 2024 to Mar 2026

    Returns
    -------
    list
        List of dictionaries containing the
        start date, end date and parsed dates.
    """

    ranges = []

    # ==================================================
    # MONTH + YEAR RANGE
    # ==================================================

    month_range_pattern = r"""
        \b
        ([A-Za-z]+)\s+(\d{4})
        \s*
        (?:-|–|—|to)
        \s*
        (?:
            ([A-Za-z]+)\s+(\d{4})
            |
            (Present|Current)
        )
        \b
    """

    month_matches = re.finditer(
        month_range_pattern,
        text,
        re.IGNORECASE | re.VERBOSE
    )

    for match in month_matches:

        start_month = match.group(1)
        start_year = match.group(2)

        end_month = match.group(3)
        end_year = match.group(4)
        current = match.group(5)

        start_text = f"{start_month} {start_year}"

        start_date = parse_date(
            start_text
        )

        # ------------------------------------------
        # PRESENT / CURRENT
        # ------------------------------------------

        if current:

            end_text = current
            end_date = None

        else:

            end_text = f"{end_month} {end_year}"

            end_date = parse_date(
                end_text
            )

        if start_date:

            ranges.append(
                {
                    "start": start_text,
                    "end": end_text,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )


    # ==================================================
    # YEAR-ONLY RANGE
    # ==================================================
    #
    # IMPORTANT:
    # Negative lookbehind prevents matching the year
    # inside "June 2023".
    #
    # ==================================================

    year_range_pattern = r"""
        (?<![A-Za-z])
        \b
        (\d{4})
        \s*
        (?:-|–|—|to)
        \s*
        (?:
            (\d{4})
            |
            (Present|Current)
        )
        \b
    """

    year_matches = re.finditer(
        year_range_pattern,
        text,
        re.IGNORECASE | re.VERBOSE
    )

    for match in year_matches:

        start_year = match.group(1)

        end_year = match.group(2)
        current = match.group(3)

        start_text = start_year

        start_date = parse_date(
            start_text
        )

        # ------------------------------------------
        # PRESENT / CURRENT
        # ------------------------------------------

        if current:

            end_text = current
            end_date = None

        else:

            end_text = end_year

            end_date = parse_date(
                end_text
            )

        if start_date:

            ranges.append(
                {
                    "start": start_text,
                    "end": end_text,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )


    return ranges


# ==================================================
# CALCULATE DURATION
# ==================================================

def calculate_duration(date_range):
    """
    Calculate approximate duration of a date range
    in years.
    """

    start = date_range["start_date"]
    end = date_range["end_date"]


    if not start:

        return 0.0


    start_year, start_month = start


    # ----------------------------------------------
    # PRESENT / CURRENT
    # ----------------------------------------------

    if end is None:

        now = datetime.now()

        end_year = now.year
        end_month = now.month

    else:

        end_year, end_month = end


    # ----------------------------------------------
    # CALCULATE MONTH DIFFERENCE
    # ----------------------------------------------

    months = (
        (end_year - start_year) * 12
        + (end_month - start_month)
    )


    if months < 0:

        return 0.0


    return round(
        months / 12,
        2
    )


# ==================================================
# CHECK EXPERIENCE REQUIREMENT
# ==================================================

def check_experience_requirement(
    candidate_years,
    required_years
):
    """
    Check whether available professional
    experience satisfies the job requirement.
    """

    return candidate_years >= required_years


# ==================================================
# MAIN EXPERIENCE ANALYZER
# ==================================================

def analyze_experience(
    experience_text
):
    """
    Analyze ONLY professional experience text.

    Important:
    This function should receive the resume's
    'experience' section rather than the entire
    resume.

    This prevents project and education dates
    from being incorrectly treated as work
    experience.
    """

    if not experience_text:

        return {
            "explicit_years": 0.0,
            "date_ranges": [],
            "calculated_years": 0.0,
            "source": "none"
        }


    # ----------------------------------------------
    # EXPLICIT EXPERIENCE
    # ----------------------------------------------

    explicit_years = extract_explicit_years(
        experience_text
    )


    # ----------------------------------------------
    # DATE RANGES
    # ----------------------------------------------

    date_ranges = extract_date_ranges(
        experience_text
    )


    # ----------------------------------------------
    # CALCULATE DATE-BASED EXPERIENCE
    # ----------------------------------------------

    calculated_years = 0.0

    for date_range in date_ranges:

        calculated_years += calculate_duration(
            date_range
        )


    calculated_years = round(
        calculated_years,
        2
    )


    # ----------------------------------------------
    # DETERMINE SOURCE
    # ----------------------------------------------

    if explicit_years > 0:

        source = "explicit"

    elif date_ranges:

        source = "date_ranges"

    else:

        source = "none"


    return {
        "explicit_years": explicit_years,
        "date_ranges": date_ranges,
        "calculated_years": calculated_years,
        "source": source
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print()
    print("EXPERIENCE EXTRACTOR")
    print("====================")


    # ==================================================
    # TEST 1: EXPLICIT EXPERIENCE
    # ==================================================

    text_1 = """
    Software Developer at ABC Technologies.
    Worked on backend development using Python.
    3 years of professional experience.
    """

    result_1 = analyze_experience(
        text_1
    )

    print()
    print("TEST 1")
    print("------")
    print(result_1)


    # ==================================================
    # TEST 2: MONTH + YEAR RANGE
    # ==================================================

    text_2 = """
    Software Engineer
    Jan 2024 - Mar 2026

    Developed REST APIs using Python.
    """

    result_2 = analyze_experience(
        text_2
    )

    print()
    print("TEST 2")
    print("------")
    print(result_2)


    # ==================================================
    # TEST 3: PRESENT
    # ==================================================

    text_3 = """
    Full Stack Developer
    June 2023 - Present

    Developed web applications using React
    and Node.js.
    """

    result_3 = analyze_experience(
        text_3
    )

    print()
    print("TEST 3")
    print("------")
    print(result_3)


    # ==================================================
    # TEST 4: YEAR-ONLY RANGE
    # ==================================================

    text_4 = """
    Software Engineer
    2022 - 2024

    Worked on backend services.
    """

    result_4 = analyze_experience(
        text_4
    )

    print()
    print("TEST 4")
    print("------")
    print(result_4)


    # ==================================================
    # TEST 5: NO PROFESSIONAL EXPERIENCE
    # ==================================================

    text_5 = """
    Bachelor of Technology in Computer Science.
    Student developer with several academic projects.
    """

    result_5 = analyze_experience(
        text_5
    )

    print()
    print("TEST 5")
    print("------")
    print(result_5)