import re


with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# Split job description into sentences
sentences = re.split(r"[.!?]", job_description)


requirements = []


for sentence in sentences:

    sentence = sentence.strip()

    if not sentence:
        continue

    sentence_lower = sentence.lower()

    # Determine whether this sentence contains requirements
    is_requirement = any(keyword in sentence_lower for keyword in [
        "experience",
        "required",
        "should have",
        "looking for",
        "preferred",
        "knowledge",
        "proficient"
    ])

    if not is_requirement:
        continue


    # Determine importance
    if "preferred" in sentence_lower or "plus" in sentence_lower:
        importance = "preferred"
    else:
        importance = "required"


    # Remove introductory phrases
    sentence = re.sub(
        r"^we are looking for\s+",
        "",
        sentence,
        flags=re.IGNORECASE
    )

    sentence = re.sub(
        r"^the candidate should have experience with\s+",
        "",
        sentence,
        flags=re.IGNORECASE
    )

    sentence = re.sub(
        r"^experience with\s+",
        "",
        sentence,
        flags=re.IGNORECASE
    )


    # Remove importance phrases
    sentence = re.sub(
        r"\s+is preferred$",
        "",
        sentence,
        flags=re.IGNORECASE
    )

    sentence = re.sub(
        r"\s+is a plus$",
        "",
        sentence,
        flags=re.IGNORECASE
    )


    # Split individual requirements
    parts = re.split(r",|\band\b", sentence, flags=re.IGNORECASE)


    for part in parts:

        part = part.strip()

        if part:
            requirements.append({
                "requirement": part,
                "importance": importance
            })


print("Extracted Requirements")
print("----------------------")


for i, item in enumerate(requirements, start=1):

    print(
        f"{i}. {item['requirement']} "
        f"({item['importance']})"
    )