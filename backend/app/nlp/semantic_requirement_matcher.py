from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def load_resume_chunks(resume_text):
    """
    Split resume into meaningful chunks.
    """

    chunks = [
        chunk.strip()
        for chunk in resume_text.split("\n\n")
        if chunk.strip()
    ]

    return chunks


def find_best_evidence(requirement_text, resume_chunks, model):
    """
    Find the resume chunk that is most semantically
    similar to the given requirement.
    """

    requirement_embedding = model.encode(
        [requirement_text]
    )

    resume_embeddings = model.encode(
        resume_chunks
    )

    similarities = cosine_similarity(
        requirement_embedding,
        resume_embeddings
    )[0]

    best_index = similarities.argmax()

    best_score = similarities[best_index]

    best_evidence = resume_chunks[best_index]

    return {
        "score": float(best_score),
        "evidence": best_evidence
    }


if __name__ == "__main__":

    with open(
        "data/resume.txt",
        "r",
        encoding="utf-8"
    ) as file:
        resume = file.read()


    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


    resume_chunks = load_resume_chunks(
        resume
    )


    requirement = "experience with react"


    result = find_best_evidence(
        requirement,
        resume_chunks,
        model
    )


    print("Semantic Requirement Matching")
    print("=============================")

    print(f"\nRequirement: {requirement}")

    print(
        f"Semantic Score: {result['score']:.4f}"
    )

    print(
        f"Evidence: {result['evidence']}"
    )