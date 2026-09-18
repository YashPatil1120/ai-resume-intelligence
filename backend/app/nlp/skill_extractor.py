import re


# ==================================================
# SKILL ALIASES
# ==================================================

SKILL_ALIASES = {

    "python": [
        "python"
    ],

    "java": [
        "java"
    ],

    "javascript": [
        "javascript"
    ],

    "typescript": [
        "typescript",
        "ts"
    ],

    "react": [
        "react",
        "react.js",
        "reactjs"
    ],

    "node.js": [
        "node.js",
        "nodejs",
        "node"
    ],

    "express.js": [
        "express.js",
        "expressjs",
        "express"
    ],

    "spring boot": [
        "spring boot",
        "springboot"
    ],

    "mongodb": [
        "mongodb",
        "mongo db"
    ],

    "mysql": [
        "mysql"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ],

    "sql": [
        "sql"
    ],

    "git": [
        "git"
    ],

    "github": [
        "github",
        "git hub"
    ],

    "docker": [
        "docker"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure"
    ],

    "gcp": [
        "gcp",
        "google cloud",
        "google cloud platform"
    ],

    "html": [
        "html",
        "html5"
    ],

    "css": [
        "css",
        "css3"
    ],

    "tailwind css": [
        "tailwind css",
        "tailwind"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "data science": [
        "data science"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "pytorch": [
        "pytorch"
    ],

    "opencv": [
        "opencv",
        "open cv"
    ],

    "langchain": [
        "langchain"
    ],

    "rag": [
        "rag",
        "retrieval augmented generation"
    ],

    "rest api": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ]
}


# ==================================================
# BUILD ALIAS → CANONICAL LOOKUP
# ==================================================

def build_alias_lookup():
    """
    Create a lookup table mapping every alias to
    its canonical skill name.
    """

    lookup = {}

    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            lookup[
                alias.lower().strip()
            ] = canonical_skill

    return lookup


ALIAS_LOOKUP = build_alias_lookup()


# ==================================================
# NORMALIZE TEXT
# ==================================================

def normalize_text(text):
    """
    Normalize text for skill matching.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==================================================
# MATCH SKILL ALIAS
# ==================================================

def contains_skill_alias(
    text,
    skill
):
    """
    Check whether a skill or any of its aliases
    occurs in the supplied text.

    Returns
    -------
    str | None
        The matched alias if found.
    """

    text = normalize_text(text)

    canonical_skill = skill.lower().strip()

    aliases = SKILL_ALIASES.get(
        canonical_skill,
        [canonical_skill]
    )

    for alias in aliases:

        pattern = (
            r"(?<!\w)"
            + re.escape(alias.lower())
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text
        ):

            return alias

    return None


# ==================================================
# EXTRACT SKILLS
# ==================================================

def extract_skills(text):
    """
    Extract canonical skills from text.

    Matching is alias-aware.

    Example:
        "React.js and RESTful APIs"

    becomes:

        ["react", "rest api"]
    """

    found_skills = []

    for canonical_skill in SKILL_ALIASES:

        matched_alias = contains_skill_alias(
            text,
            canonical_skill
        )

        if matched_alias:

            found_skills.append(
                canonical_skill
            )

    return found_skills


# ==================================================
# FIND SKILL EVIDENCE
# ==================================================

def find_skill_evidence(
    text,
    skill
):
    """
    Find the exact alias used for a skill.

    Returns
    -------
    dict
        {
            "found": bool,
            "skill": canonical skill,
            "matched_alias": alias or None
        }
    """

    matched_alias = contains_skill_alias(
        text,
        skill
    )

    return {
        "found": matched_alias is not None,
        "skill": skill,
        "matched_alias": matched_alias
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print()
    print("SKILL EXTRACTOR")
    print("================")


    # ----------------------------------------------
    # TEST TEXT
    # ----------------------------------------------

    text = """
    Developed responsive applications using React.js,
    Node.js and RESTful APIs.

    Worked with Python, MongoDB and Git/GitHub.

    Built machine learning models using PyTorch.
    """


    # ----------------------------------------------
    # EXTRACT SKILLS
    # ----------------------------------------------

    skills = extract_skills(
        text
    )

    print()
    print("Extracted Skills")
    print("----------------")

    for skill in skills:

        print(
            f"- {skill}"
        )


    # ----------------------------------------------
    # TEST ALIAS MATCHING
    # ----------------------------------------------

    print()
    print("Alias Tests")
    print("-----------")

    tests = [
        ("React.js", "react"),
        ("RESTful APIs", "rest api"),
        ("Node.js", "node.js"),
        ("Git/GitHub", "git"),
        ("Git/GitHub", "github"),
        ("PyTorch", "pytorch"),
        ("MongoDB", "mongodb")
    ]

    for text_value, skill in tests:

        result = find_skill_evidence(
            text_value,
            skill
        )

        print(
            f"{text_value} → "
            f"{skill} → "
            f"{result}"
        )