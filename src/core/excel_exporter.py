from typing import List
import pandas as pd
import os
from openpyxl import load_workbook
from src.models.CompanyData import CompanyDataModel

def export_to_excel(gathered_data: List[CompanyDataModel], eur_to_pln_rate: float, excel_file=None):
    """
    Export company data to Excel file without overwriting existing data.
    Uses the new simplified data model with filename-based company information.
    """
    
    # Set default path to Downloads folder if not specified
    if excel_file is None:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        excel_file = os.path.join(downloads_path, "faktury_data.xlsx")
    
    # Convert CompanyDataModel objects to dictionaries
    new_data = []
    for company_data in gathered_data:
        if isinstance(company_data, CompanyDataModel):
            # Handle EUR currency conversion
            if company_data.currency == "EUR":
                # Convert EUR amounts to PLN
                pln_net = company_data.net_value * eur_to_pln_rate
                pln_gross = company_data.gross_value * eur_to_pln_rate
                pln_vat = company_data.vat_value * eur_to_pln_rate
                
                new_data.append({
                    'Firma': company_data.company_name,
                    'Numer Faktury': company_data.invoice_number,
                    'Temat': company_data.topic_number,
                    'Typ': company_data.invoice_type if company_data.invoice_type else "",
                    'Netto': round(pln_net, 2),  # Converted to PLN
                    'Brutto': round(pln_gross, 2),  # Converted to PLN
                    'VAT': round(pln_vat, 2),  # Converted to PLN
                    'Waluta': company_data.currency,
                    'Netto EUR': round(company_data.net_value, 2),  # Original EUR amount
                    'Plik': os.path.basename(company_data.filepath),
                })
            else:
                # PLN or other currencies - use original amounts
                new_data.append({
                    'Firma': company_data.company_name,
                    'Numer Faktury': company_data.invoice_number,
                    'Temat': company_data.topic_number,
                    'Typ': company_data.invoice_type if company_data.invoice_type else "",
                    'Netto': round(company_data.net_value, 2),
                    'Brutto': round(company_data.gross_value, 2),
                    'VAT': round(company_data.vat_value, 2),
                    'Waluta': company_data.currency,
                    'Netto EUR': "",  # Empty for non-EUR currencies
                    'Plik': os.path.basename(company_data.filepath),
                })
        else:
            print(f"Warning: Expected CompanyDataModel but got {type(company_data)}: {company_data}")
    
    if not new_data:
        print("No valid CompanyDataModel objects found to export.")
        return False

    # Create DataFrame from new data
    new_df = pd.DataFrame(new_data)
    
    # Check if Excel file already exists
    if os.path.exists(excel_file):
        try:
            # Read existing data
            existing_df = pd.read_excel(excel_file)
            # Append new data to existing data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            print(f"Warning: Could not read existing Excel file: {e}")
            print("Creating new file with current data.")
            combined_df = new_df
    else:
        # If file doesn't exist, use only new data
        combined_df = new_df
    
    try:
        # Save to Excel
        combined_df.to_excel(excel_file, index=False)


        workbook = load_workbook(excel_file)
        worksheet = workbook.active
        
        if worksheet:
            # Set column widths for new structure
            worksheet.column_dimensions['A'].width = 30  # Firma
            worksheet.column_dimensions['B'].width = 20  # Numer Faktury
            worksheet.column_dimensions['C'].width = 15  # Temat
            worksheet.column_dimensions['D'].width = 10  # Typ
            worksheet.column_dimensions['E'].width = 15  # Netto
            worksheet.column_dimensions['F'].width = 15  # Brutto
            worksheet.column_dimensions['G'].width = 15  # VAT
            worksheet.column_dimensions['H'].width = 10  # Waluta
            worksheet.column_dimensions['I'].width = 15  # Netto EUR
            worksheet.column_dimensions['J'].width = 25  # Plik

        workbook.save(excel_file)
        workbook.close()
        
        print(f"Udało się wyeksprtować {len(new_data)} rekordów do {excel_file}")
        print(f"Suma rekordów w pliku: {len(combined_df)}")

        return True
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return False