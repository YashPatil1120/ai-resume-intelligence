from app.nlp.skill_extractor import extract_skills

from app.nlp.experience_extractor import (
    analyze_experience,
    check_experience_requirement
)

from app.nlp.experience_requirement import (
    extract_required_experience
)

from app.nlp.education_extractor import (
    analyze_education,
    check_education_requirement,
    extract_education_requirements,
    extract_education_requirement_groups
)

from app.nlp.requirement_matcher import (
    extract_requirements
)

from app.nlp.resume_section_extractor import (
    extract_resume_sections
)

from app.nlp.semantic_matcher import (
    split_into_sentences,
    create_embeddings,
    find_best_evidence
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def calculate_skill_coverage(
    satisfied_groups,
    total_groups
):
    """
    Calculate required skill coverage.

    Coverage is based on logical requirement groups,
    not individual skills.

    Example:

        Python OR Java
        React
        MySQL OR MongoDB

    = 3 requirement groups

    If all 3 are satisfied:

        100%
    """

    if total_groups == 0:
        return 0.0

    return (
        len(satisfied_groups)
        / total_groups
    ) * 100


# ==================================================
# SKILL ANALYSIS
# ==================================================

def build_skill_analysis(
    job_skills,
    resume_skills
):
    """
    Compare individual job skills with resume skills.
    """

    matched = sorted(
        skill
        for skill in job_skills
        if skill in resume_skills
    )

    missing = sorted(
        skill
        for skill in job_skills
        if skill not in resume_skills
    )

    return {
        "matched": matched,
        "missing": missing
    }


# ==================================================
# RESUME SECTION PREPARATION
# ==================================================

def prepare_resume_sections(resume):
    """
    Extract resume sections.

    If recognizable sections are found, use them.

    If the resume has no recognizable headings,
    use the complete resume as fallback content.
    """

    sections = extract_resume_sections(
        resume
    )

    meaningful_sections = [
        section
        for section in sections
        if section != "header"
    ]

    # --------------------------------------------------
    # SECTIONLESS RESUME FALLBACK
    # --------------------------------------------------

    if not meaningful_sections:

        fallback_text = sections.get(
            "header",
            ""
        ).strip()

        if fallback_text:

            sections = {
                "header": fallback_text,
                "profile": fallback_text,
                "skills": fallback_text,
                "experience": fallback_text,
                "education": fallback_text,
                "projects": fallback_text
            }

    return sections


# ==================================================
# BUILD REQUIREMENT GROUPS
# ==================================================

def build_requirement_groups(
    requirements
):
    """
    Convert individual requirement entries into
    logical requirement groups.

    Example:

        Python OR Java

    becomes:

        {
            "group_id": "or_group_1",
            "operator": "OR",
            "skills": ["java", "python"]
        }

    Normal requirements become single-skill groups.
    """

    groups = {}

    for requirement in requirements:

        group_id = requirement.get(
            "group_id"
        )

        operator = requirement.get(
            "group_operator"
        )

        skill = requirement["skill"]

        importance = requirement[
            "importance"
        ]

        requirement_text = requirement[
            "requirement_text"
        ]

        # --------------------------------------------------
        # OR GROUP
        # --------------------------------------------------

        if group_id:

            if group_id not in groups:

                groups[group_id] = {
                    "group_id": group_id,
                    "operator": operator,
                    "skills": [],
                    "importance": importance,
                    "requirement_text":
                        requirement_text
                }

            if skill not in groups[
                group_id
            ]["skills"]:

                groups[
                    group_id
                ]["skills"].append(
                    skill
                )

        # --------------------------------------------------
        # NORMAL SINGLE REQUIREMENT
        # --------------------------------------------------

        else:

            generated_group_id = (
                f"single_{skill}"
            )

            groups[
                generated_group_id
            ] = {
                "group_id":
                    generated_group_id,

                "operator":
                    "AND",

                "skills":
                    [skill],

                "importance":
                    importance,

                "requirement_text":
                    requirement_text
            }

    return list(
        groups.values()
    )


# ==================================================
# EVALUATE REQUIREMENT GROUPS
# ==================================================

def evaluate_requirement_groups(
    groups,
    resume_skills
):
    """
    Evaluate required/preferred requirement groups.

    OR group:
        At least one skill must be present.

    AND/single group:
        Every skill must be present.
    """

    evaluated_groups = []

    for group in groups:

        skills = group[
            "skills"
        ]

        operator = group[
            "operator"
        ]

        matched = [
            skill
            for skill in skills
            if skill in resume_skills
        ]

        missing = [
            skill
            for skill in skills
            if skill not in resume_skills
        ]

        # --------------------------------------------------
        # OR
        # --------------------------------------------------

        if operator == "OR":

            satisfied = (
                len(matched) > 0
            )

        # --------------------------------------------------
        # AND / SINGLE
        # --------------------------------------------------

        else:

            satisfied = (
                len(missing) == 0
            )

        evaluated_groups.append(
            {
                "group_id":
                    group["group_id"],

                "operator":
                    operator,

                "skills":
                    sorted(skills),

                "importance":
                    group["importance"],

                "requirement_text":
                    group["requirement_text"],

                "matched":
                    sorted(matched),

                "missing":
                    sorted(missing),

                "satisfied":
                    satisfied
            }
        )

    return evaluated_groups


# ==================================================
# EDUCATION REQUIREMENT PREPARATION
# ==================================================

def prepare_job_education_requirements(
    job_description
):
    """
    Extract only education-related requirements from
    the job description.

    IMPORTANT:

    We do NOT call:

        analyze_education(job_description)

    because that would analyze unrelated technical
    requirements such as:

        Machine Learning
        Artificial Intelligence
        PyTorch
        AWS

    as if they were education fields.

    Instead we specifically extract education
    requirements.
    """

    education_requirements = (
        extract_education_requirements(
            job_description
        )
    )

    education_or_groups = (
        extract_education_requirement_groups(
            job_description
        )
    )

    required_levels = education_requirements.get(
        "levels",
        []
    )

    all_fields = education_requirements.get(
        "fields",
        []
    )

    # --------------------------------------------------
    # Remove fields that belong to OR groups
    # --------------------------------------------------

    grouped_fields = set()

    for group in education_or_groups:

        grouped_fields.update(
            group.get(
                "fields",
                []
            )
        )

    normal_required_fields = [
        field
        for field in all_fields
        if field not in grouped_fields
    ]

    return {
        "levels":
            sorted(
                set(required_levels)
            ),

        "fields":
            sorted(
                set(all_fields)
            ),

        "normal_required_fields":
            sorted(
                set(normal_required_fields)
            ),

        "requirement_groups":
            education_or_groups
    }


# ==================================================
# EDUCATION GROUP EVALUATION
# ==================================================

def evaluate_education_groups(
    candidate_education,
    education_groups
):
    """
    Evaluate education OR groups.

    Example:

        Computer Science OR
        Software Engineering

    Candidate:

        Computer Science

    Result:

        satisfied = True
    """

    candidate_fields = set(
        candidate_education.get(
            "fields",
            []
        )
    )

    evaluated_groups = []

    for group in education_groups:

        group_fields = set(
            group.get(
                "fields",
                []
            )
        )

        matched = sorted(
            candidate_fields.intersection(
                group_fields
            )
        )

        satisfied = (
            len(matched) > 0
        )

        evaluated_groups.append(
            {
                "group_id":
                    group["group_id"],

                "operator":
                    group["operator"],

                "fields":
                    sorted(
                        group_fields
                    ),

                "requirement_text":
                    group[
                        "requirement_text"
                    ],

                "matched":
                    matched,

                "satisfied":
                    satisfied
            }
        )

    return evaluated_groups


# ==================================================
# MAIN ANALYSIS FUNCTION
# ==================================================

def analyze_resume(
    resume,
    job_description
):
    """
    Analyze a resume against a job description.

    Pipeline:

        Resume
          ↓
        Section Extraction
          ↓
        Skills
        Experience
        Education
          ↓
        Job Requirement Extraction
          ↓
        Required / Preferred
          ↓
        OR / AND Groups
          ↓
        Exact / Alias Evidence
          ↓
        Semantic Evidence
          ↓
        Experience Requirement
          ↓
        Education Requirement
          ↓
        Final Eligibility
    """

    # ==================================================
    # 1. RESUME SECTIONS
    # ==================================================

    sections = prepare_resume_sections(
        resume
    )

    # ==================================================
    # 2. PREPARE SECTION TEXT
    # ==================================================

    skills_text = sections.get(
        "skills",
        ""
    )

    projects_text = sections.get(
        "projects",
        ""
    )

    experience_text = sections.get(
        "experience",
        ""
    )

    education_text = sections.get(
        "education",
        ""
    )

    profile_text = sections.get(
        "profile",
        ""
    )

    # ==================================================
    # 3. RESUME SKILLS
    # ==================================================

    # Skills can legitimately appear in:
    #
    #   Skills
    #   Projects
    #   Experience
    #   Profile
    #
    # so we combine these sections.

    skill_source_text = "\n".join(
        section
        for section in [
            skills_text,
            projects_text,
            experience_text,
            profile_text
        ]
        if section
    )

    resume_skills = set(
        extract_skills(
            skill_source_text
        )
    )

    # ==================================================
    # 4. EXPERIENCE ANALYSIS
    # ==================================================

    # IMPORTANT:
    #
    # Only the Experience section is analyzed.
    #
    # Projects and Education dates are not counted
    # as professional experience.

    experience_result = analyze_experience(
        experience_text
    )

    if (
        experience_result[
            "explicit_years"
        ] > 0
    ):

        candidate_years = (
            experience_result[
                "explicit_years"
            ]
        )

    elif experience_result[
        "date_ranges"
    ]:

        candidate_years = (
            experience_result[
                "calculated_years"
            ]
        )

    else:

        candidate_years = 0.0

    # ==================================================
    # 5. CANDIDATE EDUCATION
    # ==================================================

    # This is safe because education_text is the
    # resume's actual education section.

    candidate_education = analyze_education(
        education_text
    )

    # ==================================================
    # 6. JOB REQUIREMENTS
    # ==================================================

    requirements = extract_requirements(
        job_description
    )

    # ==================================================
    # 7. REQUIREMENT GROUPS
    # ==================================================

    requirement_groups = (
        build_requirement_groups(
            requirements
        )
    )

    # ==================================================
    # 8. REQUIRED / PREFERRED GROUPS
    # ==================================================

    required_groups = [
        group
        for group in requirement_groups
        if group["importance"] == "required"
    ]

    preferred_groups = [
        group
        for group in requirement_groups
        if group["importance"] == "preferred"
    ]

    # ==================================================
    # 9. EVALUATE REQUIRED GROUPS
    # ==================================================

    evaluated_required_groups = (
        evaluate_requirement_groups(
            required_groups,
            resume_skills
        )
    )

    # ==================================================
    # 10. EVALUATE PREFERRED GROUPS
    # ==================================================

    evaluated_preferred_groups = (
        evaluate_requirement_groups(
            preferred_groups,
            resume_skills
        )
    )

    # ==================================================
    # 11. FLAT REQUIRED SKILLS
    # ==================================================

    required_skills = set()

    for group in required_groups:

        required_skills.update(
            group["skills"]
        )

    # ==================================================
    # 12. FLAT PREFERRED SKILLS
    # ==================================================

    preferred_skills = set()

    for group in preferred_groups:

        preferred_skills.update(
            group["skills"]
        )

    # ==================================================
    # 13. MATCHED REQUIRED SKILLS
    # ==================================================

    matched_required = sorted(
        skill
        for skill in required_skills
        if skill in resume_skills
    )

    # ==================================================
    # 14. MISSING REQUIRED REQUIREMENTS
    # ==================================================

    missing_required = []

    for group in evaluated_required_groups:

        if not group[
            "satisfied"
        ]:

            if group[
                "operator"
            ] == "OR":

                missing_required.append(
                    " OR ".join(
                        group["skills"]
                    )
                )

            else:

                missing_required.extend(
                    group["missing"]
                )

    missing_required = sorted(
        set(missing_required)
    )

    # ==================================================
    # 15. PREFERRED SKILL ANALYSIS
    # ==================================================

    matched_preferred = sorted(
        skill
        for skill in preferred_skills
        if skill in resume_skills
    )

    missing_preferred = []

    for group in evaluated_preferred_groups:

        if not group[
            "satisfied"
        ]:

            if group[
                "operator"
            ] == "OR":

                missing_preferred.append(
                    " OR ".join(
                        group["skills"]
                    )
                )

            else:

                missing_preferred.extend(
                    group["missing"]
                )

    missing_preferred = sorted(
        set(missing_preferred)
    )

    # ==================================================
    # 16. REQUIRED SKILL COVERAGE
    # ==================================================

    satisfied_required_groups = [
        group
        for group in evaluated_required_groups
        if group["satisfied"]
    ]

    required_skill_coverage = (
        calculate_skill_coverage(
            satisfied_required_groups,
            len(
                evaluated_required_groups
            )
        )
    )

    # ==================================================
    # 17. SEMANTIC EVIDENCE TEXT
    # ==================================================

    evidence_text = "\n".join(
        section
        for section in [
            skills_text,
            projects_text,
            experience_text,
            profile_text
        ]
        if section
    )

    resume_sentences = split_into_sentences(
        evidence_text
    )

    resume_embeddings = create_embeddings(
        resume_sentences
    )

    # ==================================================
    # 18. REQUIREMENT EVIDENCE
    # ==================================================

    requirement_evidence = []

    for requirement in requirements:

        skill = requirement[
            "skill"
        ]

        importance = requirement[
            "importance"
        ]

        requirement_text = requirement[
            "requirement_text"
        ]

        # --------------------------------------------------
        # Find explicit / semantic evidence
        # --------------------------------------------------

        semantic_result = find_best_evidence(
            skill,
            requirement_text,
            resume_sentences,
            resume_embeddings
        )

        exact_match = (
            skill in resume_skills
        )

        requirement_evidence.append(
            {
                "skill":
                    skill,

                "importance":
                    importance,

                "requirement_context":
                    requirement_text,

                "exact_match":
                    exact_match,

                "evidence_status":
                    semantic_result.get(
                        "evidence_status",
                        "NO_SEMANTIC_EVIDENCE"
                    ),

                "semantic_query":
                    semantic_result.get(
                        "semantic_query"
                    ),

                "semantic_score":
                    round(
                        semantic_result.get(
                            "score",
                            0.0
                        ),
                        4
                    ),

                "evidence_strength":
                    semantic_result.get(
                        "evidence_strength",
                        "WEAK"
                    ),

                "evidence":
                    semantic_result.get(
                        "evidence"
                    ),

                "group_id":
                    requirement.get(
                        "group_id"
                    ),

                "group_operator":
                    requirement.get(
                        "group_operator"
                    ),

                "group_skills":
                    requirement.get(
                        "group_skills",
                        [skill]
                    )
            }
        )

    # ==================================================
    # 19. REQUIRED EXPERIENCE
    # ==================================================

    required_experience = (
        extract_required_experience(
            job_description
        )
    )

    experience_satisfied = (
        check_experience_requirement(
            candidate_years,
            required_experience
        )
    )

    # ==================================================
    # 20. REQUIRED EDUCATION
    # ==================================================

    # IMPORTANT:
    #
    # Do NOT do:
    #
    #     analyze_education(job_description)
    #
    # because the JD contains many non-education terms.
    #
    # Instead, specifically extract education
    # requirements.

    required_education = (
        prepare_job_education_requirements(
            job_description
        )
    )

    # --------------------------------------------------
    # Evaluate education OR groups
    # --------------------------------------------------

    evaluated_education_groups = (
        evaluate_education_groups(
            candidate_education,
            required_education[
                "requirement_groups"
            ]
        )
    )

    # --------------------------------------------------
    # Build object used by education checker
    # --------------------------------------------------

    education_check_data = {
        "levels":
            required_education[
                "levels"
            ],

        "fields":
            required_education[
                "fields"
            ],

        "normal_required_fields":
            required_education[
                "normal_required_fields"
            ],

        "requirement_groups":
            required_education[
                "requirement_groups"
            ]
    }

    education_satisfied = (
        check_education_requirement(
            candidate_education,
            education_check_data
        )
    )

    # --------------------------------------------------
    # Extra safety:
    #
    # Explicitly evaluate the education groups too.
    # --------------------------------------------------

    for group in evaluated_education_groups:

        if not group[
            "satisfied"
        ]:

            education_satisfied = False

    # ==================================================
    # 21. FINAL ELIGIBILITY
    # ==================================================

    eligible = (

        len(
            missing_required
        ) == 0

        and

        experience_satisfied

        and

        education_satisfied

    )

    # ==================================================
    # 22. RETURN RESULT
    # ==================================================

    return {

        # ------------------------------------------
        # RESUME
        # ------------------------------------------

        "sections_detected":
            sorted(
                sections.keys()
            ),

        "resume_skills":
            sorted(
                resume_skills
            ),

        # ------------------------------------------
        # REQUIRED SKILLS
        # ------------------------------------------

        "required_skills": {

            "matched":
                matched_required,

            "missing":
                missing_required
        },

        # ------------------------------------------
        # PREFERRED SKILLS
        # ------------------------------------------

        "preferred_skills": {

            "matched":
                matched_preferred,

            "missing":
                missing_preferred
        },

        # ------------------------------------------
        # SKILL GROUPS
        # ------------------------------------------

        "required_skill_groups":
            evaluated_required_groups,

        "preferred_skill_groups":
            evaluated_preferred_groups,

        # ------------------------------------------
        # COVERAGE
        # ------------------------------------------

        "required_skill_coverage":
            round(
                required_skill_coverage,
                2
            ),

        # ------------------------------------------
        # EVIDENCE
        # ------------------------------------------

        "requirement_evidence":
            requirement_evidence,

        # ------------------------------------------
        # EXPERIENCE
        # ------------------------------------------

        "experience": {

            "candidate_years":
                candidate_years,

            "explicit_years":
                experience_result[
                    "explicit_years"
                ],

            "calculated_years":
                experience_result[
                    "calculated_years"
                ],

            "source":
                experience_result[
                    "source"
                ],

            "date_ranges":
                experience_result[
                    "date_ranges"
                ],

            "required_years":
                required_experience,

            "satisfied":
                experience_satisfied
        },

        # ------------------------------------------
        # EDUCATION
        # ------------------------------------------

        "education": {

            "candidate_levels":
                sorted(
                    candidate_education[
                        "levels"
                    ]
                ),

            "candidate_fields":
                sorted(
                    candidate_education[
                        "fields"
                    ]
                ),

            "institution":
                candidate_education[
                    "institution"
                ],

            "dates":
                candidate_education[
                    "dates"
                ],

            "required_levels":
                sorted(
                    required_education[
                        "levels"
                    ]
                ),

            "required_fields":
                sorted(
                    required_education[
                        "normal_required_fields"
                    ]
                ),

            "required_education_groups":
                evaluated_education_groups,

            "satisfied":
                education_satisfied
        },

        # ------------------------------------------
        # FINAL
        # ------------------------------------------

        "eligibility":
            eligible
    }


# ==================================================
# TERMINAL TEST
# ==================================================

if __name__ == "__main__":

    # ----------------------------------------------
    # LOAD RESUME
    # ----------------------------------------------

    with open(
        "data/resume.txt",
        "r",
        encoding="utf-8"
    ) as file:

        resume = file.read()

    # ----------------------------------------------
    # LOAD JOB DESCRIPTION
    # ----------------------------------------------

    with open(
        "data/job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    # ----------------------------------------------
    # RUN ANALYSIS
    # ----------------------------------------------

    result = analyze_resume(
        resume,
        job_description
    )

    # ==================================================
    # DISPLAY RESULT
    # ==================================================

    print()
    print(
        "RESUME DECISION ENGINE"
    )
    print(
        "======================"
    )

    # ==================================================
    # SECTIONS
    # ==================================================

    print()
    print(
        "Detected Sections"
    )
    print(
        "-----------------"
    )

    for section in result[
        "sections_detected"
    ]:

        print(
            f"- {section}"
        )

    # ==================================================
    # RESUME SKILLS
    # ==================================================

    print()
    print(
        "Resume Skills"
    )
    print(
        "-------------"
    )

    for skill in result[
        "resume_skills"
    ]:

        print(
            f"- {skill}"
        )

    # ==================================================
    # REQUIRED GROUPS
    # ==================================================

    print()
    print(
        "Required Skill Groups"
    )
    print(
        "---------------------"
    )

    for group in result[
        "required_skill_groups"
    ]:

        operator = (
            f" {group['operator']} "
        )

        requirement = operator.join(
            group["skills"]
        )

        if group["satisfied"]:

            print(
                f"✓ {requirement}"
            )

            print(
                f"  Matched: "
                f"{group['matched']}"
            )

        else:

            print(
                f"✗ {requirement}"
            )

            print(
                f"  Missing: "
                f"{group['missing']}"
            )

    # ==================================================
    # REQUIRED COVERAGE
    # ==================================================

    print()
    print(
        "Required Skill Coverage"
    )
    print(
        "-----------------------"
    )

    print(
        f"{result['required_skill_coverage']:.2f}%"
    )

    # ==================================================
    # PREFERRED GROUPS
    # ==================================================

    print()
    print(
        "Preferred Skill Groups"
    )
    print(
        "----------------------"
    )

    for group in result[
        "preferred_skill_groups"
    ]:

        operator = (
            f" {group['operator']} "
        )

        requirement = operator.join(
            group["skills"]
        )

        if group["satisfied"]:

            print(
                f"✓ {requirement}"
            )

        else:

            print(
                f"✗ {requirement}"
            )

            print(
                f"  Missing: "
                f"{group['missing']}"
            )

    # ==================================================
    # EXPERIENCE
    # ==================================================

    print()
    print(
        "Experience"
    )
    print(
        "----------"
    )

    print(
        f"Candidate Experience: "
        f"{result['experience']['candidate_years']} years"
    )

    print(
        f"Required Experience: "
        f"{result['experience']['required_years']} years"
    )

    print(
        f"Experience Source: "
        f"{result['experience']['source']}"
    )

    if result[
        "experience"
    ]["satisfied"]:

        print(
            "✓ Experience requirement satisfied"
        )

    else:

        print(
            "✗ Experience requirement not satisfied"
        )

    # ==================================================
    # EDUCATION
    # ==================================================

    print()
    print(
        "Education"
    )
    print(
        "---------"
    )

    print(
        f"Candidate Levels: "
        f"{result['education']['candidate_levels']}"
    )

    print(
        f"Candidate Fields: "
        f"{result['education']['candidate_fields']}"
    )

    print(
        f"Institution: "
        f"{result['education']['institution']}"
    )

    print(
        f"Education Dates: "
        f"{result['education']['dates']}"
    )

    print(
        f"Required Levels: "
        f"{result['education']['required_levels']}"
    )

    print(
        f"Required Fields: "
        f"{result['education']['required_fields']}"
    )

    print(
        "Required Education OR Groups:"
    )

    for group in result[
        "education"
    ].get(
        "required_education_groups",
        []
    ):

        requirement = (
            f" {group['operator']} "
        ).join(
            group["fields"]
        )

        if group["satisfied"]:

            print(
                f"✓ {requirement}"
            )

            print(
                f"  Matched: "
                f"{group['matched']}"
            )

        else:

            print(
                f"✗ {requirement}"
            )

            print(
                f"  Missing: "
                f"{group['fields']}"
            )

    if result[
        "education"
    ]["satisfied"]:

        print(
            "✓ Education requirement satisfied"
        )

    else:

        print(
            "✗ Education requirement not satisfied"
        )

    # ==================================================
    # EVIDENCE
    # ==================================================

    print()
    print(
        "Requirement Evidence"
    )
    print(
        "--------------------"
    )

    for evidence in result[
        "requirement_evidence"
    ]:

        print()

        print(
            f"Skill: "
            f"{evidence['skill']}"
        )

        print(
            f"Importance: "
            f"{evidence['importance']}"
        )

        print(
            f"Group: "
            f"{evidence['group_id']}"
        )

        print(
            f"Status: "
            f"{evidence['evidence_status']}"
        )

        print(
            f"Strength: "
            f"{evidence['evidence_strength']}"
        )

        print(
            f"Score: "
            f"{evidence['semantic_score']}"
        )

        print(
            f"Evidence: "
            f"{evidence['evidence']}"
        )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    print()
    print(
        "Eligibility"
    )
    print(
        "----------"
    )

    if result[
        "eligibility"
    ]:

        print(
            "✓ ELIGIBLE"
        )

    else:

        print(
            "✗ NOT ELIGIBLE"
        )