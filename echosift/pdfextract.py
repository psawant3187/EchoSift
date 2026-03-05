import pdfplumber
import pytesseract
from PIL import Image
import io
from typing import Union, Tuple, Dict, Any

# Set the path for Tesseract executable (Ensure Tesseract is installed and path is correct)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(file: Union[str, bytes, io.BytesIO], 
                          max_page_extract: int = 50) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text and metadata from a PDF using PDFPlumber. Automatically performs OCR
    on scanned/image-based pages using Tesseract if necessary.

    Args:
        file (str | bytes | BytesIO): Path or file-like object (e.g., pdf file, byte stream)
        max_page_extract (int): Max pages to extract text from

    Returns:
        Tuple: (Extracted Text, Metadata Dictionary)
    """
    try:
        # If the input is a file path (str), open the file directly
        if isinstance(file, str):
            with pdfplumber.open(file) as doc:
                return extract_text_from_doc(doc, max_page_extract)
        
        # If the input is a byte-like object, create a file-like object from it
        elif isinstance(file, (bytes, io.BytesIO)):
            # Ensure the file is a BytesIO object
            if isinstance(file, bytes):
                file = io.BytesIO(file)
            with pdfplumber.open(file) as doc:
                return extract_text_from_doc(doc, max_page_extract)
        
        else:
            raise TypeError("Input must be a string (file path), bytes, or io.BytesIO")

    except Exception as e:
        return f"Error during PDF extraction: {str(e)}", {}

def extract_text_from_doc(doc, max_page_extract: int) -> Tuple[str, Dict[str, Any]]:
    """
    Helper function to extract text from a PDF document.
    This handles both text-based and image-based pages (OCR for image-based pages).

    Args:
        doc: PDF document opened by PDFPlumber
        max_page_extract: Max number of pages to process

    Returns:
        Tuple: (Extracted Text, Metadata Dictionary)
    """
    text = ""
    metadata = doc.metadata or {}

    # Loop over pages and extract text
    for page_num in range(min(len(doc.pages), max_page_extract)):
        page = doc.pages[page_num]
        
        # Try extracting text from the page (for text-based content)
        extracted_text = page.extract_text()
        
        if extracted_text and extracted_text.strip():  # Text-based page
            text += extracted_text + "\n"
        else:  # Image-based page (OCR processing)
            img = page.to_image(resolution=300)  # Convert page to an image (for OCR)
            ocr_text = pytesseract.image_to_string(img.original)  # OCR extraction
            text += ocr_text + "\n"

    # Return the extracted text (or a message if no text was found)
    final_text = text.strip() or "No text found in the PDF."
    return final_text, metadata
