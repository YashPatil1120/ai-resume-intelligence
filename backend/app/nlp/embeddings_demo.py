from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


sentences = [
    "I am a frontend developer using React.",
    "I build user interfaces with React.",
    "I enjoy playing cricket."
]


# Generate embeddings
embeddings = model.encode(sentences)


# ---------------------------------------
# Compare sentence 1 and sentence 2
# ---------------------------------------

similarity_1_2 = cosine_similarity(
    [embeddings[0]],
    [embeddings[1]]
)[0][0]


# ---------------------------------------
# Compare sentence 1 and sentence 3
# ---------------------------------------

similarity_1_3 = cosine_similarity(
    [embeddings[0]],
    [embeddings[2]]
)[0][0]


print("Semantic Similarity Results")
print("--------------------------------")

print(
    f"\nFrontend sentence ↔ React UI sentence:"
)
print(f"Similarity: {similarity_1_2:.4f}")
print(f"Percentage: {similarity_1_2 * 100:.2f}%")


print(
    f"\nFrontend sentence ↔ Cricket sentence:"
)
print(f"Similarity: {similarity_1_3:.4f}")
print(f"Percentage: {similarity_1_3 * 100:.2f}%")