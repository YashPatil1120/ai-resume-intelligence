from skill_extractor import extract_skills


# Read resume
with open("data/resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()


# Read job description
with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# Extract skills
resume_skills = set(extract_skills(resume))
job_skills = set(extract_skills(job_description))


# Find matched and missing skills
matched_skills = resume_skills.intersection(job_skills)
missing_skills = job_skills.difference(resume_skills)


# Calculate skill match percentage
if len(job_skills) > 0:
    skill_match_percentage = (
        len(matched_skills) / len(job_skills)
    ) * 100
else:
    skill_match_percentage = 0


print("Skill Match Analysis")
print("--------------------")

print("\nResume Skills:")
for skill in sorted(resume_skills):
    print(f"✓ {skill}")


print("\nJob Required Skills:")
for skill in sorted(job_skills):
    print(f"• {skill}")


print("\nMatched Skills:")
for skill in sorted(matched_skills):
    print(f"✓ {skill}")


print("\nMissing Skills:")
for skill in sorted(missing_skills):
    print(f"✗ {skill}")


print(f"\nSkill Match: {skill_match_percentage:.2f}%")