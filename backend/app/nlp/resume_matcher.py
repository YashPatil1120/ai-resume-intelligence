from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------
# Load documents
# --------------------------------

with open("data/resume.txt", "r", encoding="utf-8") as file:
    resume = file.read()

with open("data/job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()


# --------------------------------
# Create TF-IDF vectors
# --------------------------------

documents = [
    resume,
    job_description
]

vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform(documents)


# --------------------------------
# Calculate similarity
# --------------------------------

similarity = cosine_similarity(
    tfidf_matrix[0],
    tfidf_matrix[1]
)[0][0]


# --------------------------------
# Display result
# --------------------------------

print("Resume ↔ Job Description")

print(f"\nSimilarity Score: {similarity:.4f}")

print(f"Match Percentage: {similarity * 100:.2f}%")