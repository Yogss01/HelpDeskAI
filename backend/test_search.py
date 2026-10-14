from app.rag import add_document, search_documents

add_document(
    "Employees reset their passwords using the "
    "Forgot Password link. The link is sent by email.",
    "test_faq.txt",
)

results = search_documents("How can I reset my password?")

assert results, "No results returned"
print(results[0])