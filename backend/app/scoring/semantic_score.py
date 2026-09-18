def calculate_semantic_score(
    requirement_evidence
):
    """
    Calculate semantic similarity score from genuine
    semantic evidence only.

    EXPLICIT matches are excluded because they are already
    handled by exact skill matching.

    STRONG semantic evidence:
        Uses the actual semantic similarity score.

    MODERATE semantic evidence:
        Receives 50% of the semantic similarity score.

    WEAK / NO_SEMANTIC_EVIDENCE:
        Does not contribute.
    """

    semantic_candidates = []

    for evidence in requirement_evidence:

        evidence_strength = evidence.get(
            "evidence_strength",
            "WEAK"
        )

        semantic_score = float(
            evidence.get(
                "semantic_score",
                0.0
            )
        )

        # ------------------------------------------
        # Ignore explicit matches
        # ------------------------------------------

        if evidence_strength == "EXPLICIT":
            continue

        # ------------------------------------------
        # Strong semantic evidence
        # ------------------------------------------

        if evidence_strength == "STRONG":

            semantic_candidates.append(
                max(
                    0.0,
                    min(
                        semantic_score,
                        1.0
                    )
                )
            )

        # ------------------------------------------
        # Moderate semantic evidence
        # ------------------------------------------

        elif evidence_strength == "MODERATE":

            semantic_candidates.append(
                max(
                    0.0,
                    min(
                        semantic_score * 0.5,
                        1.0
                    )
                )
            )

        # ------------------------------------------
        # Weak / no evidence
        # ------------------------------------------

        elif evidence_strength in (
            "WEAK",
            "NO_SEMANTIC_EVIDENCE"
        ):

            continue

    # ------------------------------------------
    # No genuine semantic candidates
    # ------------------------------------------

    if not semantic_candidates:
        return 0.0

    # ------------------------------------------
    # Average semantic evidence
    # ------------------------------------------

    semantic_score = (
        sum(semantic_candidates)
        /
        len(semantic_candidates)
    ) * 100

    return round(
        semantic_score,
        2
    )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    test_evidence = [

        # Exact match → ignored
        {
            "skill": "react",
            "exact_match": True,
            "semantic_score": 1.0,
            "evidence_strength": "EXPLICIT"
        },

        # Strong semantic evidence
        {
            "skill": "docker",
            "exact_match": False,
            "semantic_score": 0.72,
            "evidence_strength": "STRONG"
        },

        # Moderate semantic evidence
        {
            "skill": "aws",
            "exact_match": False,
            "semantic_score": 0.60,
            "evidence_strength": "MODERATE"
        },

        # Weak evidence
        {
            "skill": "kubernetes",
            "exact_match": False,
            "semantic_score": 0.20,
            "evidence_strength": "WEAK"
        }
    ]

    score = calculate_semantic_score(
        test_evidence
    )

    print()
    print("SEMANTIC SCORE")
    print("==============")
    print()
    print(
        f"Semantic Score: {score:.2f}"
    )