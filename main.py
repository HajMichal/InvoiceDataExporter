import sys
from typing import List

from src.core.ai_processor import gather_specific_data
from src.core.excel_exporter import export_to_excel
from src.core.ocr import extract_text_from_pdf

if __name__ == "__main__":
    pdf_paths = sys.argv[1:]
    all_extracted_text: List[str] = []

    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(pdf_path)
        clean_text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])
        all_extracted_text.append(clean_text)

    gathered_data = gather_specific_data(all_extracted_text)  
    success = export_to_excel(gathered_data)  
