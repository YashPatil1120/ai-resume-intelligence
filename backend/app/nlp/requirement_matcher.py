import re

from app.nlp.skill_extractor import (
    SKILL_ALIASES,
    extract_skills
)


# ==================================================
# REQUIREMENT HEADING DETECTION
# ==================================================

REQUIRED_HEADINGS = [
    "required qualifications",
    "required qualification",
    "requirements",
    "required requirements",
    "must have",
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


# ==================================================
# TEXT NORMALIZATION
# ==================================================

def normalize_text(text):
    """
    Normalize whitespace and common punctuation.

    This does NOT destroy useful separators such as
    '-' because they may represent flattened bullets.
    """

    text = text.lower()

    text = text.replace("•", " - ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==================================================
# HEADING NORMALIZATION
# ==================================================

def normalize_heading(text):
    """
    Normalize a heading for comparison.
    """

    text = normalize_text(text)

    text = re.sub(
        r"[^a-z0-9\s-]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==================================================
# REQUIREMENT HEADING DETECTION
# ==================================================

def detect_heading_importance(line):
    """
    Detect whether a line is a requirement heading.

    Returns:

        'required'
        'preferred'
        None
    """

    cleaned = normalize_heading(line)

    if cleaned in REQUIRED_HEADINGS:
        return "required"

    if cleaned in PREFERRED_HEADINGS:
        return "preferred"

    return None


# ==================================================
# FLATTENED JD PREPROCESSING
# ==================================================

def insert_heading_boundaries(text):
    """
    Insert newlines around Required/Preferred headings.

    This is important because text submitted through
    Swagger/FastAPI can sometimes arrive without the
    original newline formatting.

    Example:

        "... Required Qualifications: - Python ..."

    becomes:

        "... \nRequired Qualifications:\n- Python ..."
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

    text = re.sub(
        heading_pattern,
        lambda match: (
            "\n"
            + match.group(1)
            + ":\n"
        ),
        text,
        flags=re.IGNORECASE
    )

    return text


# ==================================================
# FLATTENED BULLET PREPROCESSING
# ==================================================

def insert_bullet_boundaries(text):
    """
    Detect flattened bullet points.

    Example:

        '- Python - React - Node.js'

    becomes logically:

        '- Python'
        '- React'
        '- Node.js'

    Important:
    We only treat '-' as a bullet when it has whitespace
    around it. Therefore:

        full-stack

    is NOT split.
    """

    # Convert bullet characters into normal bullet markers
    text = text.replace("•", "\n- ")
    text = text.replace("●", "\n- ")
    text = text.replace("▪", "\n- ")
    text = text.replace("◦", "\n- ")

    # Detect flattened bullets.
    #
    # We require whitespace before '-' and whitespace after '-'
    # so words like "full-stack" are not broken.
    text = re.sub(
        r"\s+-\s+",
        "\n- ",
        text
    )

    return text


# ==================================================
# REQUIREMENT LINE SPLITTING
# ==================================================

def split_requirement_lines(text):
    """
    Convert both normal multiline JDs and flattened JDs
    into logical requirement lines.

    Handles:

        Required Qualifications:
        - Python
        - React

    and flattened input:

        Required Qualifications: - Python - React
    """

    if not text:
        return []

    # --------------------------------------------------
    # Step 1: Normalize headings
    # --------------------------------------------------

    text = insert_heading_boundaries(text)

    # --------------------------------------------------
    # Step 2: Normalize flattened bullets
    # --------------------------------------------------

    text = insert_bullet_boundaries(text)

    # --------------------------------------------------
    # Step 3: Split actual lines
    # --------------------------------------------------

    raw_lines = text.splitlines()

    lines = []

    for raw_line in raw_lines:

        line = raw_line.strip()

        if not line:
            continue

        # Remove bullet prefix
        line = re.sub(
            r"^[\-\*\u2022\u25cf\u25aa\u25e6]\s*",
            "",
            line
        ).strip()

        if line:
            lines.append(line)

    return lines


# ==================================================
# IMPORTANCE DETECTION
# ==================================================

def detect_requirement_importance(
    text,
    current_importance
):
    """
    Determine importance of an individual requirement.

    Heading state is inherited unless the requirement
    explicitly contains preferred/required wording.
    """

    normalized = normalize_text(text)

    # ----------------------------------------------
    # Preferred indicators
    # ----------------------------------------------

    preferred_patterns = [
        r"\bpreferred\b",
        r"\bnice\s+to\s+have\b",
        r"\bgood\s+to\s+have\b",
        r"\bdesired\b",
        r"\bplus\b"
    ]

    for pattern in preferred_patterns:

        if re.search(
            pattern,
            normalized
        ):
            return "preferred"

    # ----------------------------------------------
    # Required indicators
    # ----------------------------------------------

    required_patterns = [
        r"\brequired\b",
        r"\bmandatory\b",
        r"\bmust\s+have\b"
    ]

    for pattern in required_patterns:

        if re.search(
            pattern,
            normalized
        ):
            return "required"

    return current_importance


# ==================================================
# SKILL EXTRACTION
# ==================================================

def extract_requirement_skills(text):
    """
    Extract canonical skills from one requirement.
    """

    return extract_skills(text)


# ==================================================
# OR DETECTION
# ==================================================

def detect_or_group(text, skills):
    """
    Detect whether skills belong to an OR requirement.

    Example:

        Python or Java

    -> ['python', 'java']

    But:

        React and Node.js

    -> None

    because both are independently required.
    """

    if len(skills) < 2:
        return None

    normalized = normalize_text(text)

    # --------------------------------------------------
    # Explicit OR
    # --------------------------------------------------

    if re.search(
        r"\b(or|either)\b",
        normalized
    ):

        return sorted(
            set(skills)
        )

    return None


# ==================================================
# REQUIREMENT ENTRY CREATION
# ==================================================

def create_requirement_entry(
    skill,
    importance,
    requirement_text,
    group_id=None,
    group_operator=None,
    group_skills=None
):
    """
    Create a standardized requirement dictionary.
    """

    if group_skills is None:
        group_skills = [skill]

    return {
        "skill": skill,
        "importance": importance,
        "requirement_text": requirement_text,
        "group_id": group_id,
        "group_operator": group_operator,
        "group_skills": group_skills
    }


# ==================================================
# REQUIREMENT EXTRACTION
# ==================================================

def extract_requirements(job_description):
    """
    Extract structured skill requirements from a job description.

    Supports:

    1. Required / Preferred sections
    2. Normal multiline JDs
    3. Flattened Swagger/API JDs
    4. AND requirements
    5. OR requirements

    Example:

        Python or Java

    creates:

        python -> OR group
        java   -> OR group

    Example:

        Node.js and Express.js

    creates:

        node.js
        express.js

    as separate requirements.
    """

    requirements = []

    current_importance = "required"

    group_counter = 0

    lines = split_requirement_lines(
        job_description
    )

    for line in lines:

        # ==================================================
        # CHECK FOR HEADING
        # ==================================================

        heading_importance = (
            detect_heading_importance(line)
        )

        if heading_importance:

            current_importance = (
                heading_importance
            )

            continue

        # ==================================================
        # SKILL EXTRACTION
        # ==================================================

        skills = extract_requirement_skills(
            line
        )

        if not skills:
            continue

        # Remove duplicates while preserving canonical names
        skills = sorted(set(skills))

        # ==================================================
        # IMPORTANCE
        # ==================================================

        importance = (
            detect_requirement_importance(
                line,
                current_importance
            )
        )

        # ==================================================
        # OR GROUP
        # ==================================================

        or_group = detect_or_group(
            line,
            skills
        )

        if or_group:

            group_counter += 1

            group_id = (
                f"or_group_{group_counter}"
            )

            for skill in or_group:

                requirements.append(
                    create_requirement_entry(
                        skill=skill,
                        importance=importance,
                        requirement_text=line,
                        group_id=group_id,
                        group_operator="OR",
                        group_skills=or_group
                    )
                )

        # ==================================================
        # NORMAL / AND REQUIREMENT
        # ==================================================

        else:

            for skill in skills:

                requirements.append(
                    create_requirement_entry(
                        skill=skill,
                        importance=importance,
                        requirement_text=line,
                        group_id=None,
                        group_operator=None,
                        group_skills=[skill]
                    )
                )

    return requirements


# ==================================================
# TERMINAL TEST
# ==================================================

if __name__ == "__main__":

    # --------------------------------------------------
    # TEST 1: NORMAL MULTILINE JD
    # --------------------------------------------------

    job_description_multiline = """
    Full Stack Software Developer

    Required Qualifications:
    - Bachelor's degree in Computer Science.
    - At least 1 year of professional software development experience.
    - Strong programming experience with Python or Java.
    - Experience with React.js.
    - Experience with Node.js and Express.js.
    - Experience building RESTful APIs.
    - Experience working with MySQL or MongoDB.
    - Familiarity with Git and GitHub.

    Preferred Qualifications:
    - Experience with TypeScript.
    - Experience with Docker.
    - Familiarity with AWS.
    - Knowledge of Machine Learning or Artificial Intelligence.
    - Experience with PyTorch or OpenCV.
    """

    # --------------------------------------------------
    # TEST 2: FLATTENED JD
    # --------------------------------------------------

    job_description_flattened = """
    Full Stack Software Developer
    Required Qualifications: - Bachelor's degree in Computer Science.
    - At least 1 year of professional software development experience.
    - Strong programming experience with Python or Java.
    - Experience with React.js.
    - Experience with Node.js and Express.js.
    - Experience building RESTful APIs.
    - Experience working with MySQL or MongoDB.
    - Familiarity with Git and GitHub.
    Preferred Qualifications: - Experience with TypeScript.
    - Experience with Docker.
    - Familiarity with AWS.
    - Knowledge of Machine Learning or Artificial Intelligence.
    - Experience with PyTorch or OpenCV.
    """

    # --------------------------------------------------
    # RUN TESTS
    # --------------------------------------------------

    for test_name, jd in [
        ("MULTILINE JD", job_description_multiline),
        ("FLATTENED JD", job_description_flattened)
    ]:

        requirements = extract_requirements(jd)

        print()
        print("=" * 70)
        print(test_name)
        print("=" * 70)

        for requirement in requirements:

            print()
            print(
                f"Skill: "
                f"{requirement['skill']}"
            )

            print(
                f"Importance: "
                f"{requirement['importance']}"
            )

            print(
                f"Requirement: "
                f"{requirement['requirement_text']}"
            )

            print(
                f"Group ID: "
                f"{requirement['group_id']}"
            )

            print(
                f"Operator: "
                f"{requirement['group_operator']}"
            )

            print(
                f"Group Skills: "
                f"{requirement['group_skills']}"
            )

        # --------------------------------------------------
        # BASIC VALIDATION
        # --------------------------------------------------

        required = [
            r for r in requirements
            if r["importance"] == "required"
        ]

        preferred = [
            r for r in requirements
            if r["importance"] == "preferred"
        ]

        print()
        print("SUMMARY")
        print("-" * 70)

        print(
            "Required skills:",
            sorted(
                set(
                    r["skill"]
                    for r in required
                )
            )
        )

        print(
            "Preferred skills:",
            sorted(
                set(
                    r["skill"]
                    for r in preferred
                )
            )
        )

        print(
            "OR groups:",
            sorted(
                set(
                    r["group_id"]
                    for r in requirements
                    if r["group_id"]
                )
            )
        )