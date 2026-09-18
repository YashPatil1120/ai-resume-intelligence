import re


# =========================================================
# EDUCATION LEVELS
# =========================================================

EDUCATION_ALIASES = {
    "phd": [
        "phd",
        "ph.d",
        "doctorate",
        "doctoral"
    ],

    "master": [
        "master",
        "masters",
        "master's",
        "m.tech",
        "mtech",
        "m.sc",
        "msc",
        "mca",
        "mba"
    ],

    "bachelor": [
        "bachelor",
        "bachelors",
        "bachelor's",
        "b.tech",
        "btech",
        "b.sc",
        "bsc",
        "bca"
    ],

    "diploma": [
        "diploma"
    ]
}


# =========================================================
# EDUCATION FIELDS
# =========================================================

FIELD_ALIASES = {
    "computer science": [
        "computer science",
        "computer engineering",
        "computer science and engineering",
        "cse"
    ],

    "software engineering": [
        "software engineering"
    ],

    "information technology": [
        "information technology",
        "information technology engineering",
        "it"
    ],

    "electronics": [
        "electronics",
        "electronics engineering",
        "electronics and communication",
        "ece"
    ],

    "electrical engineering": [
        "electrical engineering",
        "electrical"
    ],

    "mechanical engineering": [
        "mechanical engineering",
        "mechanical"
    ],

    "civil engineering": [
        "civil engineering",
        "civil"
    ],

    "artificial intelligence": [
        "artificial intelligence"
    ],

    "data science": [
        "data science"
    ],

    "mathematics": [
        "mathematics",
        "maths"
    ],

    "physics": [
        "physics"
    ],

    "chemistry": [
        "chemistry"
    ],

    "business": [
        "business administration",
        "business"
    ]
}


# =========================================================
# EDUCATION HEADING DETECTION
# =========================================================

EDUCATION_HEADINGS = [
    "education",
    "educational qualifications",
    "educational qualification",
    "academic qualifications",
    "academic qualification",
    "academic background",
    "education requirements",
    "educational requirements"
]


# =========================================================
# REQUIRED / PREFERRED HEADINGS
# =========================================================

REQUIRED_HEADINGS = [
    "required qualifications",
    "required qualification",
    "requirements",
    "required requirements",
    "mandatory qualifications",
    "mandatory requirements",
    "minimum qualifications"
]


PREFERRED_HEADINGS = [
    "preferred qualifications",
    "preferred qualification",
    "preferred requirements",
    "nice to have",
    "nice-to-have",
    "good to have",
    "desired qualifications",
    "additional qualifications"
]


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize whitespace and common dash characters.
    """

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# ALIAS MATCHING
# =========================================================

def contains_alias(text, alias):
    """
    Check whether an alias appears as a complete term.
    """

    pattern = (
        r"(?<!\w)"
        + re.escape(alias.lower())
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        text
    ) is not None


# =========================================================
# EDUCATION LEVEL EXTRACTION
# =========================================================

def extract_education_levels(text):
    """
    Extract education levels such as:

        bachelor
        master
        phd
        diploma
    """

    normalized = normalize_text(text)

    found_levels = []

    for level, aliases in EDUCATION_ALIASES.items():

        for alias in aliases:

            if contains_alias(
                normalized,
                alias
            ):
                found_levels.append(level)
                break

    return found_levels


# =========================================================
# EDUCATION FIELD EXTRACTION
# =========================================================

def extract_education_fields(text):
    """
    Extract education fields such as:

        computer science
        software engineering
        artificial intelligence
        data science
    """

    normalized = normalize_text(text)

    found_fields = []

    for field, aliases in FIELD_ALIASES.items():

        for alias in aliases:

            if contains_alias(
                normalized,
                alias
            ):
                found_fields.append(field)
                break

    return found_fields


# =========================================================
# INSTITUTION EXTRACTION
# =========================================================

def extract_institution(text):
    """
    Extract likely university / college / institute name.
    """

    lines = text.splitlines()

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        if re.search(
            r"\b(university|college|institute|school)\b",
            clean_line,
            re.IGNORECASE
        ):

            # Remove common trailing date ranges
            clean_line = re.sub(
                r",?\s*[A-Za-z]{3,9}\s+\d{4}"
                r"\s*[-–]\s*"
                r"(?:[A-Za-z]{3,9}\s+)?\d{4}",
                "",
                clean_line
            )

            # Remove numeric year ranges
            clean_line = re.sub(
                r",?\s*\d{4}\s*[-–]\s*(?:\d{4}|present)",
                "",
                clean_line,
                flags=re.IGNORECASE
            )

            clean_line = re.sub(
                r"\s+",
                " ",
                clean_line
            ).strip()

            return clean_line

    return None


# =========================================================
# EDUCATION DATE EXTRACTION
# =========================================================

def extract_education_dates(text):
    """
    Extract education date range.

    Examples:

        Aug 2024-2028

        Aug 2024 - Aug 2028

        2024 - 2028
    """

    lines = text.splitlines()

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        # -------------------------------------------------
        # Month Year -> Year
        # Example:
        # Aug 2024-2028
        # -------------------------------------------------

        match = re.search(
            r"([A-Za-z]{3,9}\s+\d{4})"
            r"\s*[-–]\s*"
            r"(?:(?:[A-Za-z]{3,9})\s+)?"
            r"(\d{4}|present)\b",
            clean_line,
            re.IGNORECASE
        )

        if match:

            start = match.group(1)
            end = match.group(2)

            return {
                "start": start,
                "end": end
            }

        # -------------------------------------------------
        # Year -> Year
        # -------------------------------------------------

        match = re.search(
            r"\b(\d{4})\s*[-–]\s*(\d{4}|present)\b",
            clean_line,
            re.IGNORECASE
        )

        if match:

            return {
                "start": match.group(1),
                "end": match.group(2)
            }

    return {
        "start": None,
        "end": None
    }


# =========================================================
# HEADING DETECTION
# =========================================================

def is_required_heading(line):
    """
    Check whether line is a Required Qualifications heading.
    """

    normalized = normalize_text(line)

    normalized = re.sub(
        r"[^a-z0-9\s-]",
        "",
        normalized
    )

    return normalized.strip() in REQUIRED_HEADINGS


def is_preferred_heading(line):
    """
    Check whether line is a Preferred Qualifications heading.
    """

    normalized = normalize_text(line)

    normalized = re.sub(
        r"[^a-z0-9\s-]",
        "",
        normalized
    )

    return normalized.strip() in PREFERRED_HEADINGS


def is_education_heading(line):
    """
    Check whether line is explicitly an education heading.
    """

    normalized = normalize_text(line)

    normalized = re.sub(
        r"[^a-z0-9\s-]",
        "",
        normalized
    )

    return normalized.strip() in EDUCATION_HEADINGS


# =========================================================
# FLATTENED JD PREPROCESSING
# =========================================================

def insert_heading_boundaries(text):
    """
    Insert newlines around important JD headings.

    Handles flattened input such as:

        Required Qualifications: - Bachelor's...
        Preferred Qualifications: - Docker...
    """

    heading_pattern = (
        r"\b("
        r"required qualifications|"
        r"required qualification|"
        r"preferred qualifications|"
        r"preferred qualification|"
        r"preferred requirements|"
        r"required requirements|"
        r"minimum qualifications|"
        r"mandatory qualifications|"
        r"mandatory requirements|"
        r"desired qualifications|"
        r"additional qualifications|"
        r"nice[- ]to[- ]have|"
        r"good to have"
        r")\s*:?"
    )

    return re.sub(
        heading_pattern,
        lambda match: (
            "\n"
            + match.group(1)
            + ":\n"
        ),
        text,
        flags=re.IGNORECASE
    )


def insert_bullet_boundaries(text):
    """
    Convert flattened bullets into logical lines.

    Example:

        - Python - React - Docker

    becomes:

        - Python
        - React
        - Docker

    Hyphenated words such as:

        full-stack

    are preserved.
    """

    text = text.replace(
        "•",
        "\n- "
    )

    text = text.replace(
        "●",
        "\n- "
    )

    text = text.replace(
        "▪",
        "\n- "
    )

    text = text.replace(
        "◦",
        "\n- "
    )

    text = re.sub(
        r"\s+-\s+",
        "\n- ",
        text
    )

    return text


# =========================================================
# LOGICAL LINE SPLITTING
# =========================================================

def split_logical_lines(text):
    """
    Split both multiline and flattened text into
    logical lines.
    """

    if not text:
        return []

    text = insert_heading_boundaries(
        text
    )

    text = insert_bullet_boundaries(
        text
    )

    lines = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[\-\*\u2022\u25cf\u25aa\u25e6]\s*",
            "",
            line
        )

        line = line.strip()

        if line:
            lines.append(line)

    return lines


# =========================================================
# EDUCATION REQUIREMENT DETECTION
# =========================================================

def looks_like_education_requirement(text):
    """
    Determine whether a requirement is actually about
    education.

    We require an education-level indicator OR a clearly
    education-specific phrase.

    This prevents:

        Machine Learning or Artificial Intelligence

    from being treated as an education requirement merely
    because the whole JD was flattened.
    """

    normalized = normalize_text(text)

    # -------------------------------------------------
    # Explicit degree language
    # -------------------------------------------------

    degree_patterns = [
        r"\bbachelor(?:'s|s)?\b",
        r"\bmaster(?:'s|s)?\b",
        r"\bph\.?d\.?\b",
        r"\bdoctorate\b",
        r"\bdoctoral\b",
        r"\bdiploma\b",
        r"\bdegree\b",
        r"\bundergraduate\b",
        r"\bgraduate degree\b"
    ]

    for pattern in degree_patterns:

        if re.search(
            pattern,
            normalized
        ):
            return True

    return False


# =========================================================
# EDUCATION OR GROUP EXTRACTION
# =========================================================

def extract_education_requirement_groups(text):
    """
    Extract education OR groups only from actual education
    requirements.

    Example:

        Bachelor's degree in Computer Science or
        Software Engineering.

    becomes:

        computer science OR software engineering

    It will NOT accidentally include fields from later
    Preferred Qualifications.
    """

    groups = []

    group_counter = 1

    lines = split_logical_lines(
        text
    )

    for line in lines:

        # -------------------------------------------------
        # Ignore headings
        # -------------------------------------------------

        if is_required_heading(line):
            continue

        if is_preferred_heading(line):
            continue

        # -------------------------------------------------
        # Must actually look like education
        # -------------------------------------------------

        if not looks_like_education_requirement(
            line
        ):
            continue

        normalized = normalize_text(
            line
        )

        # -------------------------------------------------
        # Must contain OR
        # -------------------------------------------------

        if not re.search(
            r"\b(or|either)\b",
            normalized
        ):
            continue

        fields = []

        # -------------------------------------------------
        # Extract fields from THIS line only
        # -------------------------------------------------

        for field, aliases in FIELD_ALIASES.items():

            for alias in aliases:

                if contains_alias(
                    normalized,
                    alias
                ):

                    if field not in fields:
                        fields.append(field)

                    break

        # -------------------------------------------------
        # Need at least two different fields
        # -------------------------------------------------

        if len(fields) < 2:
            continue

        groups.append(
            {
                "group_id":
                    f"education_or_group_{group_counter}",

                "operator":
                    "OR",

                "fields":
                    fields,

                "requirement_text":
                    line
            }
        )

        group_counter += 1

    return groups


# =========================================================
# EXTRACT NORMAL EDUCATION REQUIREMENTS
# =========================================================

def extract_education_requirements(text):
    """
    Extract education levels and fields only from lines
    that actually look like education requirements.

    This is useful for separating education requirements
    from unrelated technical requirements in a JD.
    """

    levels = []
    fields = []

    lines = split_logical_lines(
        text
    )

    for line in lines:

        if is_required_heading(line):
            continue

        if is_preferred_heading(line):
            continue

        if not looks_like_education_requirement(
            line
        ):
            continue

        line_levels = extract_education_levels(
            line
        )

        line_fields = extract_education_fields(
            line
        )

        for level in line_levels:

            if level not in levels:
                levels.append(level)

        for field in line_fields:

            if field not in fields:
                fields.append(field)

    return {
        "levels": levels,
        "fields": fields
    }


# =========================================================
# COMPLETE EDUCATION ANALYSIS
# =========================================================

def analyze_education(text):
    """
    Analyze education information.

    This function is used for both:

    1. Resume education sections
    2. Job-description education requirements

    For a resume, institution/date extraction is useful.

    For a JD, requirement groups are also extracted.
    """

    levels = extract_education_levels(
        text
    )

    fields = extract_education_fields(
        text
    )

    institution = extract_institution(
        text
    )

    dates = extract_education_dates(
        text
    )

    requirement_groups = (
        extract_education_requirement_groups(
            text
        )
    )

    return {
        "levels": levels,
        "fields": fields,
        "institution": institution,
        "dates": dates,
        "requirement_groups": requirement_groups
    }


# =========================================================
# EDUCATION REQUIREMENT CHECK
# =========================================================

def check_education_requirement(
    candidate_education,
    required_education
):
    """
    Check whether candidate education satisfies
    the required education.

    Logic:

        Required level
            AND
        Required normal fields
            AND
        Each education OR group

    For an OR group:

        Computer Science OR Software Engineering

    only one matching field is required.
    """

    candidate_levels = set(
        candidate_education.get(
            "levels",
            []
        )
    )

    candidate_fields = set(
        candidate_education.get(
            "fields",
            []
        )
    )

    required_levels = set(
        required_education.get(
            "levels",
            []
        )
    )

    required_fields = set(
    required_education.get(
        "normal_required_fields",
        required_education.get(
            "fields",
            []
            )
        )
    )

    # -------------------------------------------------
    # LEVEL CHECK
    # -------------------------------------------------

    if required_levels:

        level_satisfied = bool(
            candidate_levels.intersection(
                required_levels
            )
        )

        if not level_satisfied:
            return False

    # -------------------------------------------------
    # NORMAL FIELD CHECK
    # -------------------------------------------------

    if required_fields:

        field_satisfied = bool(
            candidate_fields.intersection(
                required_fields
            )
        )

        if not field_satisfied:
            return False

    # -------------------------------------------------
    # OR GROUP CHECK
    # -------------------------------------------------

    for group in required_education.get(
        "requirement_groups",
        []
    ):

        group_fields = set(
            group.get(
                "fields",
                []
            )
        )

        if not candidate_fields.intersection(
            group_fields
        ):
            return False

    return True


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("EDUCATION EXTRACTOR TEST")
    print("========================")
    print()

    test_cases = [

        # ---------------------------------------------
        # Basic education OR
        # ---------------------------------------------

        (
            "Bachelor's degree in Computer Science "
            "or Software Engineering."
        ),

        # ---------------------------------------------
        # Single field
        # ---------------------------------------------

        (
            "Bachelor's degree in Computer Science."
        ),

        # ---------------------------------------------
        # Master OR
        # ---------------------------------------------

        (
            "Master's degree in Data Science "
            "or Artificial Intelligence."
        ),

        # ---------------------------------------------
        # Single field
        # ---------------------------------------------

        (
            "Bachelor's degree in Information Technology."
        ),

        # ---------------------------------------------
        # Another field
        # ---------------------------------------------

        (
            "Bachelor's degree in Mechanical Engineering."
        ),

        # ---------------------------------------------
        # IMPORTANT FALSE-POSITIVE TEST
        # ---------------------------------------------

        (
            "Knowledge of Machine Learning "
            "or Artificial Intelligence."
        ),

        # ---------------------------------------------
        # IMPORTANT FULL FLATTENED JD TEST
        # ---------------------------------------------

        (
            """
            Full Stack Software Developer
            Required Qualifications: - Bachelor's degree
            in Computer Science or Software Engineering.
            - At least 2 years of professional software
            development experience.
            - Strong programming experience with Python
            or Java.
            - Experience with React.js.
            - Experience with Node.js and Express.js.
            Preferred Qualifications: - Experience with
            TypeScript.
            - Experience with Docker.
            - Familiarity with AWS.
            - Knowledge of Machine Learning or
            Artificial Intelligence.
            - Experience with PyTorch or OpenCV.
            """
        )
    ]

    for text in test_cases:

        result = analyze_education(
            text
        )

        print(
            f"Text: {text.strip()}"
        )

        print(
            f"Levels: {result['levels']}"
        )

        print(
            f"Fields: {result['fields']}"
        )

        print(
            f"OR Groups: "
            f"{result['requirement_groups']}"
        )

        print()