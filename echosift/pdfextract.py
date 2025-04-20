import pymupdf
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image
import io
from typing import Union, Tuple, Dict, Any

def extract_text_from_pdf(file: Union[str, bytes, io.BytesIO], 
                          max_page_extract: int = 50) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text and metadata from a PDF using PyMuPDF. Automatically performs OCR
    on scanned/image-based pages using Tesseract if necessary.

    Args:
        file (str | bytes | BytesIO): Path or file-like object
        max_page_extract (int): Max pages to extract text from

    Returns:
        Tuple: (Extracted Text, Metadata Dictionary)
    """
    try:
        # Load document
        if isinstance(file, str):
            doc = pymupdf.open(file)
        else:
            doc = pymupdf.open(stream=file, filetype="pdf")

        text = ""
        metadata = doc.metadata or {}

        for page_num in range(min(len(doc), max_page_extract)):
            page = doc.load_page(page_num)
            extracted = page.get_text()

            if extracted.strip():  # If text-based
                text += extracted + "\n"
            else:  # If image-based (scanned)
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes()))
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"

        doc.close()

        final_text = text.strip() or "No text found in the PDF."
        return final_text, metadata

    except Exception as e:
        return f"Error during PDF extraction: {str(e)}", {}

