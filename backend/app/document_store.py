
from io import BytesIO

import pytesseract
from pdf2image import convert_from_bytes
from pypdf import PdfReader

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\YogyasreeGurram(Quad\Downloads"
    r"\Release-26.09.0-0\poppler-26.09.0\Library\bin"
)


def extract_document(filename: str, content: bytes) -> str:
    name = filename.lower()

    if name.endswith(".pdf"):
        # First, try extracting selectable text directly.
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)

        # If little text was found, OCR the rendered PDF pages.
        if len(text.strip()) < 500:
            images = convert_from_bytes(
                content,
                dpi=250,
                poppler_path=POPPLER_PATH,
            )

            ocr_pages = [
                pytesseract.image_to_string(image, lang="eng")
                for image in images
            ]
            ocr_text = "\n".join(ocr_pages)

            print("Direct extraction characters:", len(text.strip()))
            print("OCR characters:", len(ocr_text.strip()))
            print("OCR text length:", len(ocr_text))
            print("OCR preview:")
            print(repr(ocr_text[:2500]))

            # Use whichever extraction produced more text.
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text

    elif name.endswith(".txt"):
        text = content.decode("utf-8")

    else:
        raise ValueError("Only PDF and TXT files are supported")

    if not text.strip():
        raise ValueError("No readable text found in this document")

    return text
