
from app.rag import search_documents


TEST_CASES = [
    # Existing Code of Conduct tests
    {
        "question": "What is the purpose of the Code of Conduct?",
        "expected_source": "Code of Conduct_Policy - QR-3764.pdf",
        "answerable": True,
    },
    {
        "question": "How does the Code of Conduct support a safe workplace?",
        "expected_source": "Code of Conduct_Policy - QR-3764.pdf",
        "answerable": True,
    },
    {
        "question": "What kind of working environment does the Code aim to support?",
        "expected_source": "Code of Conduct_Policy - QR-3764.pdf",
        "answerable": True,
    },

    # Existing password-reset tests
    {
        "question": "How do employees reset their passwords?",
        "expected_source": "test_faq.txt",
        "answerable": True,
    },
    {
        "question": "How is the password reset link delivered?",
        "expected_source": "test_faq.txt",
        "answerable": True,
    },

    # New paraphrased questions
    {
        "question": "Which link should an employee use to reset a password?",
        "expected_source": "test_faq.txt",
        "answerable": True,
    },
    {
        "question": "Do employees receive the password reset link by email?",
        "expected_source": "test_faq.txt",
        "answerable": True,
    },
    {
        "question": "What appearance standards must employees follow?",
        "expected_source": "Code of Conduct_Policy - QR-3764.pdf",
        "answerable": True,
    },
    {
        "question": "What environment does the company want to provide?",
        "expected_source": "Code of Conduct_Policy - QR-3764.pdf",
        "answerable": True,
    },

    # Exact fact from test.txt
    {
        "question": "What is the test password reset code?",
        "expected_source": "test.txt",
        "answerable": True,
    },

    # Unsupported questions
    {
        "question": "What is the capital of France?",
        "expected_source": None,
        "answerable": False,
    },
    {
        "question": "Who won yesterday's cricket match?",
        "expected_source": None,
        "answerable": False,
    },
    {
        "question": "What is the company's office Wi-Fi password?",
        "expected_source": None,
        "answerable": False,
    },
]


EXPECTED_PHRASES = {
    "What is the purpose of the Code of Conduct?":
        "Code of Conduct is established",

    "How does the Code of Conduct support a safe workplace?":
        "safe and free from harassment and discrimination",

    "What kind of working environment does the Code aim to support?":
        "productive, positive, enjoyable",

    "How do employees reset their passwords?":
        "Forgot Password link",

    "How is the password reset link delivered?":
        "The link is sent by email",

    "Which link should an employee use to reset a password?":
        "Forgot Password link",

    "Do employees receive the password reset link by email?":
        "The link is sent by email",

    "What appearance standards must employees follow?":
        "appearance is neat, clean and appropriate",

    "What environment does the company want to provide?":
        "productive, positive, enjoyable",

    "What is the test password reset code?":
        "BETA45ftf6",
}



def run_evaluation():
    total = len(TEST_CASES)
    results = []

    print("\n" + "=" * 70)
    print("HELPDESKAI RAG RETRIEVAL EVALUATION")
    print("=" * 70)

    for number, test in enumerate(TEST_CASES, start=1):
        question = test["question"]
        expected_source = test["expected_source"]
        answerable = test["answerable"]

        matches = search_documents(question, top_k=4)
        expected_phrase = EXPECTED_PHRASES.get(question)
        phrase_ranks = [
            rank
            for rank, match in enumerate(matches, start=1)
            if expected_phrase
            and expected_phrase.casefold()
            in match.get("text", "").casefold()
        ]

        phrase_hit_at_1 = 1 in phrase_ranks
        phrase_hit_at_4 = bool(phrase_ranks)

        if expected_phrase:
            print(
                "Expected passage at rank 1:",
                "YES" if phrase_hit_at_1 else "NO",
            )
            print(
                "Expected passage in top 4:",
                "YES" if phrase_hit_at_4 else "NO",
            )


        retrieved_sources = [
            match.get("source", "Unknown source")
            for match in matches
        ]

        # Is the expected document ranked first?
        hit_at_1 = (
            answerable
            and bool(matches)
            and matches[0].get("source") == expected_source
        )

        # Does the expected document appear anywhere in top four?
        hit_at_4 = (
            answerable
            and expected_source in retrieved_sources
        )

        results.append({
            "question": question,
            "answerable": answerable,
            "hit_at_1": hit_at_1,
            "hit_at_4": hit_at_4,
            "has_results": bool(matches),
        })

        print("\n" + "-" * 70)
        print(f"Test {number}/{total}")
        print(f"Question: {question}")
        print(f"Expected source: {expected_source or 'None'}")

        if not matches:
            print("No chunks retrieved.")
        else:
            print("Retrieved chunks:")

            for rank, match in enumerate(matches, start=1):
                source = match.get("source", "Unknown source")
                score = float(match.get("score", 0))
                rerank_score = match.get("rerank_score")

                excerpt = " ".join(
                    match.get("text", "").split()
                )

                if len(excerpt) > 220:
                    excerpt = excerpt[:220] + "..."

                print(f"\n  Rank: {rank}")
                print(f"  Source: {source}")
                print(f"  Similarity score: {score:.3f}")

                if rerank_score is not None:
                    print(f"  Rerank score: {rerank_score:.3f}")

                print(f"  Excerpt: {excerpt}")

        if answerable:
            print(f"\nHit@1: {'PASS' if hit_at_1 else 'FAIL'}")
            print(f"Hit@4: {'PASS' if hit_at_4 else 'FAIL'}")
        else:
            print(
                "\nUnsupported retrieval:",
                "NO CHUNKS" if not matches else "CHUNKS FOUND",
            )

    answerable_results = [
        result for result in results
        if result["answerable"]
    ]

    unsupported_results = [
        result for result in results
        if not result["answerable"]
    ]

    hit_at_1_count = sum(
        result["hit_at_1"]
        for result in answerable_results
    )

    hit_at_4_count = sum(
        result["hit_at_4"]
        for result in answerable_results
    )

    unsupported_with_results = sum(
        result["has_results"]
        for result in unsupported_results
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Total tests: {total}")
    print(f"Answerable tests: {len(answerable_results)}")

    print(
        f"Hit@1: {hit_at_1_count}/{len(answerable_results)}"
    )

    if answerable_results:
        hit_at_1_rate = (
            hit_at_1_count / len(answerable_results) * 100
        )
        print(f"Hit@1 rate: {hit_at_1_rate:.1f}%")

    print(
        f"Hit@4: {hit_at_4_count}/{len(answerable_results)}"
    )

    if answerable_results:
        hit_at_4_rate = (
            hit_at_4_count / len(answerable_results) * 100
        )
        print(f"Hit@4 rate: {hit_at_4_rate:.1f}%")

    print(
        "Unsupported questions returning chunks:",
        f"{unsupported_with_results}/{len(unsupported_results)}",
    )

    print(
        "\nNote: Hit@1 and Hit@4 measure document retrieval, "
        "not answer correctness."
    )
    print(
        "Unsupported retrieval is a warning signal, not proof "
        "that the final answer is incorrect."
    )


if __name__ == "__main__":
    run_evaluation()
