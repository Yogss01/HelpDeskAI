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



    # Additional account-related examples
    ("I need help unlocking my user account", "account"),
    ("I cannot sign in after changing my password", "account"),
    ("My login credentials are not working", "account"),
    ("I need to update my account details", "account"),
    ("I am unable to access my profile", "account"),
    ("How can I recover my username", "account"),

    # Additional billing-related examples
    ("There is a mistake on my bill", "billing"),
    ("I need help understanding a payment charge", "billing"),
    ("My refund has not arrived", "billing"),
    ("The amount deducted from my account is incorrect", "billing"),
    ("I need assistance with a payment receipt", "billing"),
    ("Why was I charged for this service", "billing"),

    # Additional technical examples
    ("I cannot open the application", "technical"),
    ("My computer freezes when I run the software", "technical"),
    ("The website returns an internal server error", "technical"),
    ("I am unable to connect to the company network", "technical"),
    ("The program crashes when I click submit", "technical"),
    ("The application is not responding", "technical"),

    # Additional general examples
    ("Who should I contact for general assistance", "general"),
    ("I would like information about company services", "general"),
    ("Where can I find company guidelines", "general"),
    ("I have a question about an internal process", "general"),
    ("Please explain how this service works", "general"),
    ("I need some general information", "general"),

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

def predict_category_with_confidence(
    description: str,
) -> dict:
    """Predict a category and return its model confidence."""

    description = description.strip()

    if not description:
        return {
            "category": "general",
            "confidence": 0.0,
        }

    # Get the predicted category.
    prediction = classifier.predict([description])[0]

    # Get the model's estimated probability for each category.
    probabilities = classifier.predict_proba([description])[0]

    # Find the probability associated with the predicted category.
    predicted_index = list(classifier.classes_).index(prediction)
    confidence = float(probabilities[predicted_index])

    return {
        "category": str(prediction),
        "confidence": round(confidence, 4),
    }


def predict_category(description: str) -> str:
    """Return only the predicted category."""

    result = predict_category_with_confidence(description)

    return result["category"]



