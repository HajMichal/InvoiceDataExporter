from typing import List
import pandas as pd
import os
from openpyxl import load_workbook
from src.models.CompanyData import CompanyDataModel

def export_to_excel(gathered_data: List[CompanyDataModel],eur_to_pln_rate: float, excel_file="faktury_data.xlsx"):
    """
    Export company data to Excel file without overwriting existing data.
    Each CompanyDataModel field becomes a separate column.
    """
    # Convert CompanyDataModel objects to dictionaries
    new_data = []
    for company_data in gathered_data:
        if isinstance(company_data, CompanyDataModel):
            if company_data.currency == "EUR":
                # For EUR currency, calculate PLN equivalent and leave brutto/VAT empty
                euro_netto = company_data.euro_net_value if company_data.euro_net_value > 0 else company_data.net_value
                pln_netto = euro_netto * eur_to_pln_rate
                
                new_data.append({
                    'Firma': company_data.comapny_name,
                    'Numer Faktury': company_data.invoice_id, 
                    'Data': company_data.invoice_date,
                    'Brutto': "",  # Empty for EUR currency
                    'Netto': round(pln_netto, 2),  # Converted to PLN
                    'Vat': "",  # Empty for EUR currency
                    'Waluta': "EUR",
                    'NettoEUR': round(euro_netto, 2),
                    'Kraj': company_data.company_country,
                })
            else:
                euro_netto = ""
                if(company_data.euro_net_value > 0): euro_netto = round(company_data.euro_net_value, 2)

                new_data.append({
                    'Firma': company_data.comapny_name,
                    'Numer Faktury': company_data.invoice_id, 
                    'Data': company_data.invoice_date,
                    'Brutto': company_data.gross_value,
                    'Netto': company_data.net_value,
                    'Vat': company_data.tax_value,
                    'Waluta': company_data.currency,
                    'NettoEUR': euro_netto,
                    'Kraj': company_data.company_country,
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
        
        worksheet.column_dimensions['A'].width = 50
        worksheet.column_dimensions['B'].width = 25
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 15
        worksheet.column_dimensions['E'].width = 15
        worksheet.column_dimensions['F'].width = 10
        worksheet.column_dimensions['H'].width = 15

        workbook.save(excel_file)
        workbook.close()
        
        print(f"Udało się wyeksprtować {len(new_data)} rekordów do {excel_file}")
        print(f"Suma rekordów w pliku: {len(combined_df)}")

        return True
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return False