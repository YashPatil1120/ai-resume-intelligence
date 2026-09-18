from skill_extractor import extract_skills
from experience_extractor import extract_years_of_experience
from education_extractor import extract_education


# ==================================================
# 1. Read Resume and Job Description
# ==================================================

with open("data/resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()

with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# ==================================================
# 2. SKILL ANALYSIS
# ==================================================

resume_skills = set(extract_skills(resume))

sentences = job_description.replace("\n", " ").split(".")

required_skills = set()
preferred_skills = set()

for sentence in sentences:

    sentence = sentence.strip()

    if not sentence:
        continue

    sentence_lower = sentence.lower()

    skills = extract_skills(sentence)

    if not skills:
        continue

    if "preferred" in sentence_lower or "plus" in sentence_lower:
        preferred_skills.update(skills)
    else:
        required_skills.update(skills)


matched_required = resume_skills.intersection(required_skills)
missing_required = required_skills.difference(resume_skills)

matched_preferred = resume_skills.intersection(preferred_skills)
missing_preferred = preferred_skills.difference(resume_skills)


if required_skills:
    skill_coverage = (
        len(matched_required) / len(required_skills)
    ) * 100
else:
    skill_coverage = 100


# ==================================================
# 3. EXPERIENCE ANALYSIS
# ==================================================

resume_experience = extract_years_of_experience(resume)
required_experience = extract_years_of_experience(job_description)

experience_satisfied = (
    resume_experience >= required_experience
)


# ==================================================
# 4. EDUCATION ANALYSIS
# ==================================================

resume_education = extract_education(resume)
job_education = extract_education(job_description)


education_level_satisfied = True

if job_education["levels"]:

    education_level_satisfied = bool(
        resume_education["levels"].intersection(
            job_education["levels"]
        )
    )


education_field_satisfied = True

if job_education["fields"]:

    education_field_satisfied = bool(
        resume_education["fields"].intersection(
            job_education["fields"]
        )
    )


education_satisfied = (
    education_level_satisfied
    and education_field_satisfied
)


# ==================================================
# 5. FINAL ELIGIBILITY
# ==================================================

eligible = (
    len(missing_required) == 0
    and experience_satisfied
    and education_satisfied
)


if eligible:
    eligibility = "ELIGIBLE"
else:
    eligibility = "NOT ELIGIBLE"


# ==================================================
# 6. FINAL RESULT
# ==================================================

print("\n")
print("=" * 45)
print("        RESUME INTELLIGENCE REPORT")
print("=" * 45)


print("\nSKILLS")
print("-" * 45)

print(f"Required Skill Coverage: {skill_coverage:.2f}%")

print("\nMatched Required Skills:")
for skill in sorted(matched_required):
    print(f"✓ {skill}")

print("\nMissing Required Skills:")
if missing_required:
    for skill in sorted(missing_required):
        print(f"✗ {skill}")
else:
    print("None")


print("\nPreferred Skills Matched:")
for skill in sorted(matched_preferred):
    print(f"✓ {skill}")


print("\nPreferred Skills Missing:")
for skill in sorted(missing_preferred):
    print(f"✗ {skill}")


print("\nEXPERIENCE")
print("-" * 45)

print(f"Candidate Experience: {resume_experience} years")
print(f"Required Experience: {required_experience} years")

if experience_satisfied:
    print("✓ Experience requirement satisfied")
else:
    print("✗ Experience requirement NOT satisfied")


print("\nEDUCATION")
print("-" * 45)

print(
    f"Candidate Level: "
    f"{', '.join(resume_education['levels']) or 'Not detected'}"
)

print(
    f"Candidate Field: "
    f"{', '.join(resume_education['fields']) or 'Not detected'}"
)

if education_satisfied:
    print("✓ Education requirement satisfied")
else:
    print("✗ Education requirement NOT satisfied")


print("\nFINAL DECISION")
print("-" * 45)

print(f"Eligibility: {eligibility}")

print("=" * 45)