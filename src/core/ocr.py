import os
from pytesseract import image_to_string                 
from pdf2image import convert_from_path
from PIL import Image

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

def extract_text_from_tif(tif_path: str) -> str:
    """
    Reads data form a TIF file and extracts text using OCR.
    Uses Polish OCR first, falls back to English if Polish fails.
    """
    
    # Handle multi-page TIF files
    try:
        # Open the TIF file
        image = Image.open(tif_path)
        
        extracted_text = ''
        page_num = 0
        while True:
            image.seek(page_num)
            try:
                # Try Polish OCR first
                text = image_to_string(image, lang='pol')
            except:
                # Fallback to English OCR if Polish fails
                text = image_to_string(image, lang='eng')
            
            extracted_text += f"=== Strona {page_num + 1} ===\n{text}\n"
            page_num += 1
    except EOFError:
        # End of pages reached
        pass
        
    return extracted_text

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from either PDF or TIF files based on file extension.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.tif', '.tiff']:
        return extract_text_from_tif(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")