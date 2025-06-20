import sys
from typing import List

from src.core.ai_processor import gather_specific_data
from src.core.excel_exporter import export_to_excel
from src.core.get_eur_to_pln_rate import get_eur_to_pln_rate_fallback
from src.core.ocr import extract_text_from_file

if __name__ == "__main__":
    file_paths = sys.argv[1:]
    all_extracted_text: List[str] = []

    # Fetch current *EurToPln* rate from internet
    eur_to_pln_rate = get_eur_to_pln_rate_fallback()

    for file_path in file_paths:
        try:
            text = extract_text_from_file(file_path)
            clean_text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])
            all_extracted_text.append(clean_text)
        except ValueError as e:
            print(f"Error processing {file_path}: {e}")
            continue

    if all_extracted_text:
        gathered_data = gather_specific_data(all_extracted_text)  
        success = export_to_excel(gathered_data, eur_to_pln_rate)
    else:
        print("No valid files to process.")
