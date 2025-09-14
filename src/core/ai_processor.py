import os
import re
import json
from typing import List, Tuple
from google import genai
from dotenv import load_dotenv

from src.models.CompanyData import CompanyDataModel
from src.core.filename_parser import parse_invoice_filename
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

genai_api_key = os.getenv('GENAI_API_KEY')
client = genai.Client(api_key=genai_api_key)


class InvoiceAmountsModel(BaseModel):
    """Simplified model for AI to extract only financial amounts from invoice content"""
    net_value: float      # Net amount (netto)
    gross_value: float    # Gross amount (brutto)
    vat_value: float      # VAT amount (podatek VAT)
    currency: str = "PLN" # Currency (PLN, EUR, USD, etc.)

def clean_json_response(response_text: str | None) -> str:
    """Clean up malformed JSON response from AI"""

    if(response_text is None): 
         raise ValueError("Coś poszło nie tak z wyciąganiem danych przez AI")
    
    # Remove excessive whitespace and tab characters
    cleaned = re.sub(r'\\t+', ' ', response_text)  # Replace multiple \t with single space
    cleaned = re.sub(r'\t+', ' ', cleaned)         # Replace actual tabs with space
    cleaned = re.sub(r'\s+', ' ', cleaned)         # Replace multiple spaces with single space
    
    # Fix unterminated strings by ensuring quotes are properly closed
    # This regex finds strings that might be malformed and cleans them
    cleaned = re.sub(r'"([^"]*?)\\+$', r'"\1"', cleaned)  # Fix strings ending with backslashes
    
    return cleaned.strip()

def extract_amounts_from_invoice(invoice_text: str) -> InvoiceAmountsModel:
    """
    Extract only financial amounts (net, gross, VAT) and currency from invoice text using AI.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"""Extract ONLY the financial amounts from this invoice text. 
            Return ONLY valid JSON with the amounts:
            
            - net_value: Net amount (netto) - the amount before tax
            - gross_value: Gross amount (brutto) - the total amount including tax  
            - vat_value: VAT/tax amount (podatek VAT) - the tax amount
            - currency: Currency code (PLN, EUR, USD, GBP, etc.)
            
            Currency normalization:
            - If currency is zł, pln, or zloty, use "PLN"
            - If currency is euro, use "EUR" 
            - If currency is dollar, use "USD"
            - If currency is pound, use "GBP"
            
            If net_value is not present but vat_value and gross_value are present, calculate net_value as gross_value - vat_value
            
            Focus on the FINAL amounts after any corrections or totals.
            
            Invoice text:
            {invoice_text}""",
            config={
                "response_mime_type": "application/json",
                "response_schema": InvoiceAmountsModel,
                "temperature": 0.1,
            },
        )
        
        cleaned_response = clean_json_response(response.text)
        data_dict = json.loads(cleaned_response)
        
        return InvoiceAmountsModel(**data_dict)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Return fallback data
        return InvoiceAmountsModel(
            net_value=0.0,
            gross_value=0.0,
            vat_value=0.0,
            currency="PLN"
        )
    except Exception as e:
        print(f"Error extracting amounts: {e}")
        # Return fallback data  
        return InvoiceAmountsModel(
            net_value=0.0,
            gross_value=0.0,
            vat_value=0.0,
            currency="PLN"
        )


def gather_specific_data(invoice_data: List[Tuple[str, str]]) -> List[CompanyDataModel]:
    """
    Process invoice data combining filename parsing with AI content extraction.
    
    Args:
        invoice_data: List of tuples (file_path, extracted_text)
    
    Returns:
        List of CompanyDataModel objects with complete invoice information
    """
    gathered_information: List[CompanyDataModel] = []
    
    for file_path, invoice_text in invoice_data:
        try:
            # Parse filename to get company info
            filename = os.path.basename(file_path)
            company_name, invoice_number, topic_number, invoice_type = parse_invoice_filename(filename)
            
            # Extract amounts from invoice content using AI
            amounts = extract_amounts_from_invoice(invoice_text)
            
            # Create complete CompanyDataModel
            company_data = CompanyDataModel(
                company_name=company_name,
                invoice_number=invoice_number,
                topic_number=topic_number,
                invoice_type=invoice_type,
                net_value=amounts.net_value,
                gross_value=amounts.gross_value,
                vat_value=amounts.vat_value,
                currency=amounts.currency,
                filepath=file_path
            )
            
            gathered_information.append(company_data)
            
        except ValueError as filename_error:
            print(f"Error parsing filename {file_path}: {filename_error}")
            # Create fallback data with error indication
            fallback_data = CompanyDataModel(
                company_name=f"Error: {os.path.basename(file_path)}",
                invoice_number="N/A",
                topic_number="N/A",
                invoice_type=None,
                net_value=0.0,
                gross_value=0.0,
                vat_value=0.0,
                currency="PLN",
                filepath=file_path
            )
            gathered_information.append(fallback_data)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            # Create fallback data
            fallback_data = CompanyDataModel(
                company_name=f"Error: {os.path.basename(file_path)}",
                invoice_number="N/A", 
                topic_number="N/A",
                invoice_type=None,
                net_value=0.0,
                gross_value=0.0,
                vat_value=0.0,
                currency="PLN",
                filepath=file_path
            )
            gathered_information.append(fallback_data)
    
    return gathered_information