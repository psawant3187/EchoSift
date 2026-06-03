"""
echosift/extractors/pdfextract.py
PDF text extraction with OCR fallback for image-based pages.
"""
import io
from typing import Any, Dict, Tuple, Union

import pdfplumber
import pytesseract

from config import PDF_MAX_PAGE_EXTRACT, TESSERACT_CMD

# Set Tesseract path from config (can be overridden via env var)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_pdf(
    file: Union[str, bytes, io.BytesIO],
    max_page_extract: int = PDF_MAX_PAGE_EXTRACT,
) -> Tuple[str, Dict[str, Any]]:
    """
    Extract text and metadata from a PDF.

    Automatically falls back to OCR (Tesseract) for image-based pages.

    Args:
        file: File path (str), raw bytes, or a BytesIO object.
        max_page_extract: Maximum number of pages to process.

    Returns:
        (extracted_text, metadata_dict)
    """
    try:
        if isinstance(file, str):
            with pdfplumber.open(file) as doc:
                return _extract_from_doc(doc, max_page_extract)
        elif isinstance(file, (bytes, io.BytesIO)):
            if isinstance(file, bytes):
                file = io.BytesIO(file)
            with pdfplumber.open(file) as doc:
                return _extract_from_doc(doc, max_page_extract)
        else:
            raise TypeError("Input must be a str path, bytes, or io.BytesIO.")
    except Exception as e:
        return f"Error during PDF extraction: {e}", {}


def _extract_from_doc(
    doc: pdfplumber.PDF,
    max_page_extract: int,
) -> Tuple[str, Dict[str, Any]]:
    """Internal helper: iterate pages and extract/OCR text."""
    text = ""
    metadata = doc.metadata or {}

    for page_num in range(min(len(doc.pages), max_page_extract)):
        page = doc.pages[page_num]
        extracted = page.extract_text()

        if extracted and extracted.strip():
            text += extracted + "\n"
        else:
            # Image-based page — run OCR
            img = page.to_image(resolution=300)
            ocr_text = pytesseract.image_to_string(img.original)
            text += ocr_text + "\n"

    return text.strip() or "No text found in the PDF.", metadata