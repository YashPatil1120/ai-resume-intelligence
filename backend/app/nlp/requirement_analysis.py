from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills
from requirement_matcher import requirements


# --------------------------------------------------
# Load Resume
# --------------------------------------------------

with open(
    "data/resume.txt",
    "r",
    encoding="utf-8"
) as file:
    resume = file.read()


# --------------------------------------------------
# Split Resume into Chunks
# --------------------------------------------------

resume_chunks = [
    chunk.strip()
    for chunk in resume.split("\n\n")
    if chunk.strip()
]


# --------------------------------------------------
# Extract Resume Skills
# --------------------------------------------------

resume_skills = set(
    extract_skills(resume)
)


# --------------------------------------------------
# Load MiniLM
# --------------------------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# --------------------------------------------------
# Create Resume Embeddings
# --------------------------------------------------

resume_embeddings = model.encode(
    resume_chunks
)


# --------------------------------------------------
# Analyze Every Requirement
# --------------------------------------------------

results = []


for requirement in requirements:

    skill = requirement["skill"]

    importance = requirement["importance"]

    requirement_text = requirement["requirement_text"]


    # ----------------------------------------------
    # Exact Skill Match
    # ----------------------------------------------

    exact_match = skill in resume_skills


    # ----------------------------------------------
    # Semantic Evidence
    # ----------------------------------------------

    requirement_embedding = model.encode(
        [requirement_text]
    )


    similarities = cosine_similarity(
        requirement_embedding,
        resume_embeddings
    )[0]


    best_index = similarities.argmax()

    best_score = similarities[best_index]

    best_evidence = resume_chunks[best_index]


    # ----------------------------------------------
    # Store Result
    # ----------------------------------------------

    result = {
        "skill": skill,
        "importance": importance,
        "requirement_text": requirement_text,
        "exact_match": exact_match,
        "semantic_score": float(best_score),
        "evidence": best_evidence
    }


    results.append(result)


# --------------------------------------------------
# Display Results
# --------------------------------------------------

print()
print("Requirement Intelligence Analysis")
print("=================================")


for result in results:

    print()
    print(f"Skill: {result['skill']}")
    print(f"Importance: {result['importance']}")

    if result["exact_match"]:
        print("Exact Match: ✓")
    else:
        print("Exact Match: ✗")

    print(
        f"Semantic Score: {result['semantic_score']:.4f}"
    )

    print(
        f"Evidence: {result['evidence']}"
    )