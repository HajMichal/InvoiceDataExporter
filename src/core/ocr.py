import os
from pytesseract import image_to_string                 
from PIL import Image
import io
import pytesseract
import sys

# Configure Tesseract path for Windows if needed
# Try to set Tesseract path on Windows
if sys.platform.startswith('win'):
    # Common Tesseract installation paths on Windows
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"[OK] Znaleziono Tesseract: {path}")
            break
    else:
        print("[WARN] Tesseract nie został znaleziony w standardowych lokalizacjach")
        print("[INFO] Zainstaluj Tesseract z: https://github.com/UB-Mannheim/tesseract/wiki")

# Import PyMuPDF (preferred method as per user requirements)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("[INFO] Using PyMuPDF for PDF processing")
except ImportError as e:
    print(f"Error: PyMuPDF not available: {e}")
    print("Please install PyMuPDF: pip install PyMuPDF")
    PYMUPDF_AVAILABLE = False

# OCR - automatically extract text from images

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Reads data from a PDF file and extracts text using OCR with PyMuPDF.
    Uses Polish OCR first, falls back to English if Polish fails.
    """
    
    if not PYMUPDF_AVAILABLE:
        raise ValueError("PyMuPDF is required for PDF processing. Please install it with: pip install PyMuPDF")
    
    return _extract_text_from_pdf_pymupdf(pdf_path)


def _extract_text_from_pdf_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF with improved resource management"""
    pdf_document = None
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(pdf_path)
        
        extracted_text = ''
        for page_num in range(len(pdf_document)):
            # Get the page
            page = pdf_document[page_num]
            
            # Convert page to image (PNG format)
            # Use matrix for 300 DPI: 300/72 = 4.17, but 2.0 is good balance of quality/speed
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom = ~144 DPI
            pix = page.get_pixmap(matrix=mat, alpha=False)  # type: ignore
            
            try:
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                try:
                    # Try Polish OCR first
                    text = image_to_string(pil_image, lang='pol')
                except:
                    # Fallback to English OCR if Polish fails
                    text = image_to_string(pil_image, lang='eng')
                
                extracted_text += f"=== Strona {page_num + 1} ===\n{text}\n"
                
            finally:
                # Clean up pixmap to free memory
                pix = None
    
    finally:
        # Always close the PDF document
        if pdf_document:
            pdf_document.close()
    
    return extracted_text


def extract_text_from_tif(tif_path: str) -> str:
    """
    Reads data from a TIF file and extracts text using OCR.
    Uses Polish OCR first, falls back to English if Polish fails.
    """
    
    # Handle multi-page TIF files
    extracted_text = ''
    image = None
    
    try:
        # Open the TIF file
        image = Image.open(tif_path)
        
        page_num = 0
        while True:
            try:
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
                break
                
    finally:
        # Clean up image resource
        if image:
            image.close()
        
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