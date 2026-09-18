from skill_extractor import extract_skills


# --------------------------------------------------
# 1. Read Resume
# --------------------------------------------------

with open("data/resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()


# --------------------------------------------------
# 2. Read Job Description
# --------------------------------------------------

with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# --------------------------------------------------
# 3. Extract skills from Resume
# --------------------------------------------------

resume_skills = set(extract_skills(resume))


# --------------------------------------------------
# 4. Extract skills + importance from JD
# --------------------------------------------------

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

    # Determine requirement importance
    if "preferred" in sentence_lower or "plus" in sentence_lower:
        preferred_skills.update(skills)
    else:
        required_skills.update(skills)


# --------------------------------------------------
# 5. Find matches
# --------------------------------------------------

matched_required = resume_skills.intersection(required_skills)

missing_required = required_skills.difference(resume_skills)

matched_preferred = resume_skills.intersection(preferred_skills)

missing_preferred = preferred_skills.difference(resume_skills)


# --------------------------------------------------
# 6. Calculate required skill coverage
# --------------------------------------------------

if required_skills:

    required_coverage = (
        len(matched_required) / len(required_skills)
    ) * 100

else:

    required_coverage = 0


# --------------------------------------------------
# 7. Determine eligibility
# --------------------------------------------------

if len(missing_required) == 0:

    eligibility = "ELIGIBLE"

else:

    eligibility = "NOT ELIGIBLE"


# --------------------------------------------------
# 8. Display results
# --------------------------------------------------

print("Resume Eligibility Analysis")
print("===========================")


print("\nRequired Skills:")
for skill in sorted(required_skills):
    print(f"• {skill}")


print("\nMatched Required Skills:")
for skill in sorted(matched_required):
    print(f"✓ {skill}")


print("\nMissing Required Skills:")
for skill in sorted(missing_required):
    print(f"✗ {skill}")


print("\nPreferred Skills:")
for skill in sorted(preferred_skills):
    print(f"• {skill}")


print("\nMatched Preferred Skills:")
for skill in sorted(matched_preferred):
    print(f"✓ {skill}")


print("\nMissing Preferred Skills:")
for skill in sorted(missing_preferred):
    print(f"✗ {skill}")


print("\n---------------------------")

print(f"Required Skill Coverage: {required_coverage:.2f}%")

print(f"Eligibility: {eligibility}")