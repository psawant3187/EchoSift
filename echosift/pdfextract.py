import pdfplumber

# Extract text from PDF
def extract_text_from_pdf(file):
    """Extracts text and metadata from a PDF file."""
    try:
        with pdfplumber.open(file) as pdf:
            # Extract text from all pages
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text()).strip()
            
            # Extract metadata from PDF
            metadata = pdf.metadata or {}

            # Return extracted text and metadata dictionary
            return text if text else "No text found in the PDF.", metadata

    except Exception as e:
        return f"Error extracting PDF text: {e}", {}