from pytesseract import image_to_string                 
from pdf2image import convert_from_path

# OCR - automatically extract text from images
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Reads data form a PDF file and extracts text using OCR.
    Uses Polish OCR first, falls back to English if Polish fails.
    """

    # Convert pdf to images
    pages = convert_from_path(pdf_path, 300)
    
    extracted_text = ''
    for i, page in enumerate(pages):
        try:
            # Try Polish OCR first
            text = image_to_string(page, lang='pol')
        except:
            # Fallback to English OCR if Polish fails
            text = image_to_string(page, lang='eng')
        extracted_text += f"=== Strona {i+1} ===\n{text}\n"

    return extracted_text