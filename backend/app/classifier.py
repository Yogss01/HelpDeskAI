from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Example training data for HelpDeskAI.
TRAINING_DATA = [
    # Account-related tickets
    ("I cannot log in to my account", "account"),
    ("I forgot my password", "account"),
    ("Please help me reset my password", "account"),
    ("My account has been locked", "account"),
    ("I cannot access my employee account", "account"),
    ("How do I change my username", "account"),

    # Billing-related tickets
    ("My invoice has an incorrect amount", "billing"),
    ("I have a question about my payment", "billing"),
    ("I was charged twice for the same service", "billing"),
    ("Please explain my billing statement", "billing"),
    ("My payment has not been processed", "billing"),
    ("I need a copy of my invoice", "billing"),

    # Technical support tickets
    ("My application keeps crashing", "technical"),
    ("The software is running very slowly", "technical"),
    ("I am getting a server error", "technical"),
    ("My computer cannot connect to the network", "technical"),
    ("The application displays an error message", "technical"),
    ("The system is not working correctly", "technical"),

    # General support tickets
    ("I have a general question", "general"),
    ("Please provide more information about the service", "general"),
    ("I need help understanding the company process", "general"),
    ("Where can I find the support documentation", "general"),
    ("I would like to request some information", "general"),
    ("Please help me with a general enquiry", "general"),
]


def train_classifier():
    """Create and train the ticket classification model."""

    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

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

    model.fit(texts, labels)

    return model


# Train the model when this module is imported.
classifier = train_classifier()


def predict_category(description: str) -> str:
    """Predict a ticket category from its description."""

    description = description.strip()

    if not description:
        return "general"

    prediction = classifier.predict([description])[0]

    return str(prediction)
