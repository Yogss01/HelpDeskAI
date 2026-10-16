import requests


API_URL = "http://127.0.0.1:8000/api/chat"

TEST_CASES = [
    {
        "question": "What environment does the company want to provide?",
        "expected_ticket": False,
        "expected_text": "productive, positive, enjoyable",
    },
    {
        "question": "What is the company's office Wi-Fi password?",
        "expected_ticket": True,
        "expected_text": (
            "I couldn't find this information "
            "in the uploaded documents."
        ),
    },
    {
        "question": "What is the capital of France?",
        "expected_ticket": True,
        "expected_text": (
            "I couldn't find this information "
            "in the uploaded documents."
        ),
    },
    {
        "question": "How do employees reset their passwords?",
        "expected_ticket": False,
        "expected_text": "Forgot Password link",
    },
    {
        "question": "What is the company dress code?",
        "expected_ticket": False,
        "expected_text": "neat, clean and appropriate",
    },
    {
        "question": "What is the test password reset code?",
        "expected_ticket": False,
        "expected_text": "BETA45ftf6",
    },
    {
        "question": "Who won yesterday's cricket match?",
        "expected_ticket": True,
        "expected_text": (
            "I couldn't find this information "
            "in the uploaded documents."
        ),
    },
]
def run_tests():
    passed = 0

    print("\nHELPDESKAI API TESTS")
    print("=" * 60)

    for number, test in enumerate(TEST_CASES, start=1):
        try:
            response = requests.post(
                API_URL,
                json={"question": test["question"]},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer", "")
            needs_ticket = data.get("needs_ticket")

            answer_ok = (
                test["expected_text"].casefold()
                in answer.casefold()
            )

            ticket_ok = (
                needs_ticket == test["expected_ticket"]
            )

            success = answer_ok and ticket_ok

            if success:
                passed += 1

            print(f"\nTest {number}: {test['question']}")
            print("Answer:", answer)
            print("Needs ticket:", needs_ticket)
            print("Result:", "PASS" if success else "FAIL")

        except requests.RequestException as error:
            print(f"\nTest {number}: ERROR - {error}")

    print("\n" + "=" * 60)
    print(f"Passed: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    run_tests()
