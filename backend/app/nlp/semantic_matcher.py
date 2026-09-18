import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.nlp.skill_extractor import find_skill_evidence


# ==================================================
# LOAD MODEL
# ==================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==================================================
# TEXT NORMALIZATION
# ==================================================

def normalize_text(text):
    """
    Normalize text for comparison.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==================================================
# SENTENCE SPLITTING
# ==================================================

def split_into_sentences(text):
    """
    Split resume text into meaningful sentences.

    Also handles resume bullet-style text where
    newline boundaries represent separate pieces
    of evidence.
    """

    text = text.strip()

    if not text:
        return []

    # Normalize spaces while preserving line boundaries.
    lines = re.split(
        r"[\r\n]+",
        text
    )

    sentences = []

    for line in lines:

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if not line:
            continue

        # Split normal sentences inside each line.
        parts = re.split(
            r"(?<=[.!?])\s+",
            line
        )

        for part in parts:

            part = part.strip()

            if part:
                sentences.append(part)

    return sentences


# ==================================================
# CREATE EMBEDDINGS
# ==================================================

def create_embeddings(texts):
    """
    Convert text into sentence embeddings.
    """

    if not texts:
        return []

    return model.encode(
        texts
    )


# ==================================================
# EVIDENCE STRENGTH
# ==================================================

def classify_evidence(score):
    """
    Classify semantic similarity.

    These thresholds are development heuristics,
    not probabilities.
    """

    if score >= 0.70:
        return "STRONG"

    elif score >= 0.50:
        return "MODERATE"

    return "WEAK"


# ==================================================
# FIND EXPLICIT EVIDENCE
# ==================================================

def find_explicit_evidence(
    skill,
    texts
):
    """
    Search resume text for an exact skill alias.

    Uses the centralized skill vocabulary.
    """

    for text in texts:

        result = find_skill_evidence(
            text,
            skill
        )

        if result["found"]:

            return {
                "found": True,
                "evidence": text,
                "matched_alias": result["matched_alias"]
            }

    return {
        "found": False,
        "evidence": None,
        "matched_alias": None
    }


# ==================================================
# BUILD SEMANTIC QUERY
# ==================================================

def build_semantic_query(
    skill,
    requirement_text
):
    """
    Build the semantic query used by the embedding model.

    The requirement itself is the primary semantic
    signal. The skill is included as additional context.
    """

    return (
        f"Job requirement: {requirement_text}. "
        f"Related skill: {skill}."
    )


# ==================================================
# FIND SEMANTIC EVIDENCE
# ==================================================

def find_semantic_evidence(
    skill,
    requirement_text,
    texts,
    embeddings
):
    """
    Find resume sentences that are semantically related
    to a job requirement.

    This is used when an exact skill alias was not found.
    """

    semantic_query = build_semantic_query(
        skill,
        requirement_text
    )

    if not texts:

        return {
            "score": 0.0,
            "evidence_strength": "WEAK",
            "evidence_status": "NO_SEMANTIC_EVIDENCE",
            "evidence": "No resume evidence found.",
            "semantic_query": semantic_query
        }

    query_embedding = model.encode(
        [semantic_query]
    )

    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    best_index = int(
        similarities.argmax()
    )

    score = float(
        similarities[best_index]
    )

    strength = classify_evidence(
        score
    )

    # ----------------------------------------------
    # WEAK
    # ----------------------------------------------

    if strength == "WEAK":

        return {
            "score": score,
            "evidence_strength": "WEAK",
            "evidence_status": "NO_SEMANTIC_EVIDENCE",
            "evidence": "No strong semantic evidence found.",
            "semantic_query": semantic_query
        }

    # ----------------------------------------------
    # MODERATE / STRONG
    # ----------------------------------------------

    return {
        "score": round(score, 4),
        "evidence_strength": strength,
        "evidence_status": "SEMANTIC",
        "evidence": texts[best_index],
        "semantic_query": semantic_query
    }


# ==================================================
# FIND BEST EVIDENCE
# ==================================================

def find_best_evidence(
    skill,
    requirement_text,
    texts,
    embeddings
):
    """
    Find the strongest available evidence.

    Priority:

        1. Explicit skill evidence
        2. Semantic contextual evidence
        3. No evidence
    """

    # ----------------------------------------------
    # STEP 1: EXPLICIT
    # ----------------------------------------------

    explicit_result = find_explicit_evidence(
        skill,
        texts
    )

    if explicit_result["found"]:

        return {
            "score": 1.0,
            "evidence_strength": "EXPLICIT",
            "evidence_status": "EXPLICIT",
            "evidence": explicit_result["evidence"],
            "matched_alias": explicit_result["matched_alias"],
            "semantic_query": None
        }

    # ----------------------------------------------
    # STEP 2: SEMANTIC
    # ----------------------------------------------

    return find_semantic_evidence(
        skill,
        requirement_text,
        texts,
        embeddings
    )


# ==================================================
# MAIN SEMANTIC MATCHER
# ==================================================

def semantic_resume_match(
    skill,
    requirement_text,
    resume_text
):
    """
    Find the strongest evidence for a requirement
    inside the resume.
    """

    sentences = split_into_sentences(
        resume_text
    )

    embeddings = create_embeddings(
        sentences
    )

    return find_best_evidence(
        skill,
        requirement_text,
        sentences,
        embeddings
    )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    resume = """
    Developed responsive web applications using React.js
    and Node.js.

    Built RESTful APIs using Python and Express.js.

    Worked with MongoDB and Git/GitHub.

    Developed machine learning models using PyTorch.

    Deployed applications and managed cloud infrastructure.
    """

    print()
    print("SEMANTIC EVIDENCE MATCHER")
    print("=========================")

    # ==================================================
    # TEST 1: EXPLICIT ALIAS
    # ==================================================

    result_1 = semantic_resume_match(
        "rest api",
        "The candidate should have experience with REST APIs.",
        resume
    )

    print()
    print("TEST 1: REST API")
    print("-----------------")
    print(result_1)

    # ==================================================
    # TEST 2: EXPLICIT SKILL
    # ==================================================

    result_2 = semantic_resume_match(
        "react",
        "The candidate should have experience with React.",
        resume
    )

    print()
    print("TEST 2: REACT")
    print("-------------")
    print(result_2)

    # ==================================================
    # TEST 3: EXPLICIT SKILL
    # ==================================================

    result_3 = semantic_resume_match(
        "node.js",
        "The candidate should have experience with Node.js.",
        resume
    )

    print()
    print("TEST 3: NODE.JS")
    print("----------------")
    print(result_3)

    # ==================================================
    # TEST 4: SEMANTIC EVIDENCE
    # ==================================================

    result_4 = semantic_resume_match(
        "cloud computing",
        "The candidate should have experience with cloud infrastructure.",
        resume
    )

    print()
    print("TEST 4: CLOUD COMPUTING")
    print("-----------------------")
    print(result_4)

    # ==================================================
    # TEST 5: NO STRONG EVIDENCE
    # ==================================================

    result_5 = semantic_resume_match(
        "docker",
        "The candidate should have experience with Docker containers.",
        resume
    )

    print()
    print("TEST 5: DOCKER")
    print("--------------")
    print(result_5)