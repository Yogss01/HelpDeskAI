
from app.rag import search_documents


# Start with questions supported by the previews we inspected.
# Add more questions after checking the complete document text.
TEST_CASES = [
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
    {
        "question": "What is the capital of France?",
        "expected_source": None,
        "answerable": False,
    },
]


def run_evaluation():
    total = len(TEST_CASES)
    expected_source_found = 0
    results = []

    print("\n" + "=" * 70)
    print("HELPDESKAI RAG RETRIEVAL EVALUATION")
    print("=" * 70)

    for number, test in enumerate(TEST_CASES, start=1):
        question = test["question"]
        expected_source = test["expected_source"]

        matches = search_documents(question, top_k=4)

        retrieved_sources = [
            match.get("source", "Unknown source")
            for match in matches
        ]

        found = (
            expected_source is not None
            and expected_source in retrieved_sources
        )

        if found:
            expected_source_found += 1

        top_score = matches[0]["score"] if matches else None

        print(f"\nTest {number}/{total}")
        print(f"Question: {question}")
        print(f"Expected source: {expected_source or 'None'}")
        print(f"Retrieved sources: {retrieved_sources}")
        print(
            "Top similarity score:",
            f"{top_score:.3f}" if top_score is not None else "No results",
        )

        if expected_source is None:
            print(
                "Expected-source check: NOT APPLICABLE "
                "(unsupported question)"
            )
        else:
            print(
                "Expected source found:",
                "YES" if found else "NO",
            )

        results.append({
            "question": question,
            "expected_source": expected_source,
            "retrieved_sources": retrieved_sources,
            "top_score": top_score,
            "expected_source_found": found,
            "answerable": test["answerable"],
        })

    answerable_tests = [
        result for result in results
        if result["answerable"]
    ]

    successful_answerable = sum(
        result["expected_source_found"]
        for result in answerable_tests
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total}")
    print(f"Answerable tests: {len(answerable_tests)}")
    print(
        "Expected source found:",
        f"{successful_answerable}/{len(answerable_tests)}",
    )

    if answerable_tests:
        hit_rate = successful_answerable / len(answerable_tests) * 100
        print(f"Retrieval Hit@4: {hit_rate:.1f}%")

    print(
        "\nNote: The unsupported question is not included in Hit@4. "
        "This script measures retrieval, not answer correctness."
    )


if __name__ == "__main__":
    run_evaluation()
