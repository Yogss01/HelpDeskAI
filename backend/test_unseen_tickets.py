
from app.classifier import predict_category_with_confidence


# These descriptions are separate from TRAINING_DATA.
UNSEEN_TEST_DATA = [
    # Account
    ("The login page says my credentials are invalid", "account"),
    ("I no longer have access to my user profile", "account"),
    ("My password reset is not working", "account"),
    ("I need to reactivate my disabled account", "account"),
    ("I cannot sign in to the employee portal", "account"),

    # Billing
    ("The company deducted money from me twice", "billing"),
    ("Can I get a refund for my last payment", "billing"),
    ("My receipt shows the wrong total", "billing"),
    ("I do not recognize a transaction on my bill", "billing"),
    ("When will my outstanding payment be processed", "billing"),

    # Technical
    ("The browser displays a blank page when I open the portal", "technical"),
    ("I get disconnected every time I join the office network", "technical"),
    ("The software crashes when I save a document", "technical"),
    ("I cannot upload a file because the system shows an error", "technical"),
    ("The company server is unavailable", "technical"),

    # General
    ("Where can I read the company's holiday policy", "general"),
    ("Could you explain the process for requesting leave", "general"),
    ("What are the working hours of the support department", "general"),
    ("Where do I find the employee guidelines", "general"),
    ("I need information about the company's internal procedures", "general"),
]


def main():
    correct = 0
    total = len(UNSEEN_TEST_DATA)

    print("=" * 55)
    print("HELPDESKAI UNSEEN TICKET EVALUATION")
    print("=" * 55)

    for description, expected in UNSEEN_TEST_DATA:
        result = predict_category_with_confidence(description)

        predicted = result["category"]
        confidence = result["confidence"]
        passed = predicted == expected

        if passed:
            correct += 1

        status = "CORRECT" if passed else "INCORRECT"

        print(f"\nDescription: {description}")
        print(f"Expected:    {expected}")
        print(f"Predicted:   {predicted}")
        print(f"Confidence:  {confidence:.2%}")
        print(f"Result:      {status}")

    accuracy = correct / total * 100

    print("\n" + "=" * 55)
    print(f"Correct:  {correct}/{total}")
    print(f"Incorrect: {total - correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("=" * 55)


if __name__ == "__main__":
    main()
