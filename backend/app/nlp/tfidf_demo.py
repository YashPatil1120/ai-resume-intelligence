import math


documents = [
    "Python Python React",
    "Python React Node",
    "Java SQL"
]

# --------------------------------
# Step 1: Tokenize documents
# --------------------------------

tokenized_documents = [
    document.lower().split()
    for document in documents
]

print("Tokenized documents:")
print(tokenized_documents)


# --------------------------------
# Step 2: Build vocabulary
# --------------------------------

vocabulary = sorted(
    set(word for document in tokenized_documents for word in document)
)

print("\nVocabulary:")
print(vocabulary)


# --------------------------------
# Step 3: Calculate TF
# --------------------------------

def calculate_tf(document, word):
    return document.count(word) / len(document)


# --------------------------------
# Step 4: Calculate IDF
# --------------------------------

def calculate_idf(documents, word):
    total_documents = len(documents)

    document_frequency = sum(
        1 for document in documents
        if word in document
    )

    return math.log(total_documents / document_frequency)


# --------------------------------
# Step 5: Calculate TF-IDF
# --------------------------------

def calculate_tfidf(document, word, documents):
    tf = calculate_tf(document, word)
    idf = calculate_idf(documents, word)

    return tf * idf


# --------------------------------
# Step 6: Create TF-IDF vectors
# --------------------------------

vectors = []

for document in tokenized_documents:

    vector = [
        calculate_tfidf(document, word, tokenized_documents)
        for word in vocabulary
    ]

    vectors.append(vector)


print("\nTF-IDF vectors:")

for document, vector in zip(documents, vectors):
    print(document)
    print(vector)