
from pathlib import Path
from app.document_store import extract_document

# Check whether the original PDF exists in the project.
pdf_files = list(Path("..").rglob("*.pdf"))

if pdf_files:
    pdf_path = pdf_files[0]
    print("PDF found:", pdf_path)
    text = extract_document(pdf_path.name, pdf_path.read_bytes())
    print("\n--- EXTRACTED TEXT ---")
    print(text[:3000])
else:
    print("Original PDF not found in project.")
    print("The uploaded PDF is processed in memory.")
    print("Please upload the PDF again after the next diagnostic change.")
