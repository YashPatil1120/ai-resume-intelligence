from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills


# ==================================================
# 1. Read files
# ==================================================

with open("data/resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()

with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# ==================================================
# 2. Load model
# ==================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ==================================================
# 3. Create resume chunks
# ==================================================

resume_chunks = [
    chunk.strip()
    for chunk in resume.split("\n\n")
    if chunk.strip()
]


# ==================================================
# 4. Extract JD skills
# ==================================================

job_skills = extract_skills(job_description)


# ==================================================
# 5. Generate embeddings for resume chunks
# ==================================================

resume_embeddings = model.encode(resume_chunks)


# ==================================================
# 6. Compare each requirement
# ==================================================

print("Requirement → Resume Evidence")
print("=============================")


for skill in job_skills:

    requirement_text = f"experience with {skill}"

    requirement_embedding = model.encode(
        [requirement_text]
    )

    similarities = cosine_similarity(
        requirement_embedding,
        resume_embeddings
    )[0]

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    best_chunk = resume_chunks[best_index]

    print(f"\nRequirement: {requirement_text}")
    print(f"Best Score: {best_score:.4f}")
    print(f"Evidence: {best_chunk}")