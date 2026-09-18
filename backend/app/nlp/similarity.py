import math


def cosine_similarity(vector_a, vector_b):

    # Step 1: Dot product
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    # Step 2: Magnitude of vector A
    magnitude_a = math.sqrt(
        sum(a ** 2 for a in vector_a)
    )

    # Step 3: Magnitude of vector B
    magnitude_b = math.sqrt(
        sum(b ** 2 for b in vector_b)
    )

    # Avoid division by zero
    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    # Step 4: Cosine similarity
    return dot_product / (magnitude_a * magnitude_b)


resume_vector = [
    0.0,
    0.0,
    0.27031007207210955,
    0.13515503603605478,
    0.0
]

job_vector = [
    0.0,
    0.3662040962227032,
    0.13515503603605478,
    0.13515503603605478,
    0.0
]


similarity = cosine_similarity(
    resume_vector,
    job_vector
)

print("Cosine Similarity:")
print(similarity)

print("\nMatch Percentage:")
print(f"{similarity * 100:.2f}%")