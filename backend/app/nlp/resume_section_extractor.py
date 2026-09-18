import re
from app.utils.pdf_parser import (
    extract_text_from_pdf
)

# ==================================================
# KNOWN RESUME SECTIONS
# ==================================================

SECTION_ALIASES = {

    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history"
    ],

    "skills": [
        "skills",
        "technical skills",
        "skills & technologies",
        "technical expertise"
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "project experience"
    ],

    "profile": [
        "profile",
        "summary",
        "professional summary",
        "objective",
        "about me"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses & certifications"
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards"
    ],

    "languages": [
        "languages",
        "language proficiency"
    ],

    "interests": [
        "interests",
        "hobbies"
    ]
}


# ==================================================
# BUILD ALIAS LOOKUP
# ==================================================

def build_section_lookup():
    """
    Create a lookup table where every known heading
    maps to its canonical section name.
    """

    lookup = {}

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            normalized_alias = (
                alias.lower()
                .strip()
            )

            lookup[
                normalized_alias
            ] = section

    return lookup


SECTION_LOOKUP = build_section_lookup()


# ==================================================
# NORMALIZE HEADING
# ==================================================

def normalize_heading(line):
    """
    Normalize a possible section heading.
    """

    line = line.strip()

    line = re.sub(
        r"[:\-]+$",
        "",
        line
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.lower().strip()


# ==================================================
# CHECK SECTION HEADING
# ==================================================

def detect_section_heading(line):
    """
    Determine whether a line is a known resume
    section heading.

    Returns
    -------
    str | None
        Canonical section name if detected.
    """

    normalized_line = normalize_heading(
        line
    )

    return SECTION_LOOKUP.get(
        normalized_line
    )


# ==================================================
# EXTRACT RESUME SECTIONS
# ==================================================

def extract_resume_sections(text):
    """
    Divide resume text into recognized sections.

    Unknown content before the first recognized
    section is stored under 'header'.

    Returns
    -------
    dict
        Mapping of section names to their text.
    """

    lines = text.splitlines()

    sections = {}

    current_section = "header"

    sections[
        current_section
    ] = []


    for line in lines:

        cleaned_line = line.strip()


        # ------------------------------------------
        # IGNORE COMPLETELY EMPTY LINES
        # ------------------------------------------

        if not cleaned_line:

            continue


        # ------------------------------------------
        # CHECK FOR SECTION HEADING
        # ------------------------------------------

        detected_section = (
            detect_section_heading(
                cleaned_line
            )
        )


        if detected_section:

            current_section = (
                detected_section
            )


            if current_section not in sections:

                sections[
                    current_section
                ] = []


            continue


        # ------------------------------------------
        # ADD CONTENT TO CURRENT SECTION
        # ------------------------------------------

        sections[
            current_section
        ].append(
            cleaned_line
        )


    # ----------------------------------------------
    # CONVERT LISTS TO TEXT
    # ----------------------------------------------

    cleaned_sections = {}


    for section, content in sections.items():

        section_text = "\n".join(
            content
        ).strip()


        if section_text:

            cleaned_sections[
                section
            ] = section_text


    return cleaned_sections


# ==================================================
# TEST
# ==================================================

# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    # ----------------------------------------------
    # LOAD REAL RESUME PDF
    # ----------------------------------------------

    resume = extract_text_from_pdf(
        "data/test_resume.pdf"
    )


    # ----------------------------------------------
    # EXTRACT SECTIONS
    # ----------------------------------------------

    sections = extract_resume_sections(
        resume
    )


    # ----------------------------------------------
    # DISPLAY RESULT
    # ----------------------------------------------

    print()

    print("RESUME SECTION EXTRACTOR")

    print("========================")


    for section, content in sections.items():

        print()

        print(
            f"[{section.upper()}]"
        )

        print(
            "-" * (
                len(section) + 2
            )
        )

        print(content)