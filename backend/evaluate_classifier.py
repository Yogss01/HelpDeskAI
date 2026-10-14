
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.classifier import TRAINING_DATA


def evaluate_classifier():
    """Evaluate the classifier using a held-out portion of the dataset."""

    # Separate descriptions and their correct categories.
    texts = [description for description, category in TRAINING_DATA]
    labels = [category for description, category in TRAINING_DATA]

    # Keep some examples aside for testing.
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    # Build the same type of model used by HelpDeskAI.
    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42,
            ),
        ),
    ])

    # Train only on the training portion.
    model.fit(X_train, y_train)

    # Predict categories for descriptions not used in training.
    predictions = model.predict(X_test)

    # Display evaluation results.
    accuracy = accuracy_score(y_test, predictions)

    print("=" * 50)
    print("HELPDESKAI CLASSIFIER EVALUATION")
    print("=" * 50)

    print(f"Total examples: {len(texts)}")
    print(f"Training examples: {len(X_train)}")
    print(f"Testing examples: {len(X_test)}")
    print(f"Accuracy: {accuracy:.2%}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=["account", "billing", "technical", "general"],
            zero_division=0,
        )
    )

    print("\nIndividual Test Results:")

    for description, actual, predicted in zip(
        X_test,
        y_test,
        predictions,
    ):
        result = "CORRECT" if actual == predicted else "INCORRECT"

        print(f"\nDescription: {description}")
        print(f"Expected:    {actual}")
        print(f"Predicted:   {predicted}")
        print(f"Result:      {result}")


if __name__ == "__main__":
    evaluate_classifier()
