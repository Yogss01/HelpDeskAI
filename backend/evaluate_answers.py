
from app.rag import search_documents
from app.llm import generate_answer, FALLBACK_ANSWER


TEST_CASES = [
    {
        "question": "How do employees reset their passwords?",
        "should_answer": True,
    },
    {
        "question": "How is the password reset link delivered?",
        "should_answer": True,
    },
    {
        "question": "What is the purpose of the Code of Conduct?",
        "should_answer": True,
    },
    {
        "question": "What is the capital of France?",
        "should_answer": False,
    },
]


def run_evaluation():
    total = len(TEST_CASES)
    results = []

    print("\n" + "=" * 70)
    print("HELPDESKAI ANSWER EVALUATION")
    print("=" * 70)

    for number, test in enumerate(TEST_CASES, start=1):
        question = test["question"]
        should_answer = test["should_answer"]

        sources = search_documents(question, top_k=4)
        answer = generate_answer(question, sources)

        used_fallback = answer.strip() == FALLBACK_ANSWER.strip()

        if should_answer:
            passed = bool(sources) and not used_fallback
        else:
            passed = used_fallback

        results.append(passed)

        print(f"\nTest {number}/{total}")
        print(f"Question: {question}")
        print(f"Sources found: {len(sources)}")
        print(f"Answer: {answer}")
        print(f"Fallback returned: {used_fallback}")
        print(f"Test result: {'PASS' if passed else 'CHECK'}")

    passed_count = sum(results)

    print("\n" + "=" * 70)
    print("ANSWER EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total}")
    print(f"Passed: {passed_count}")
    print(f"Needs review: {total - passed_count}")

    if total:
        print(f"Pass rate: {passed_count / total * 100:.1f}%")

    print(
        "\nImportant: PASS checks fallback behavior and whether an answer "
        "was returned. It does not prove factual correctness."
    )


if __name__ == "__main__":
    run_evaluation()
