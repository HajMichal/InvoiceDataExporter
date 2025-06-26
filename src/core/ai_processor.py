import os
import re
import json
from typing import List
from google import genai
from dotenv import load_dotenv

from src.models.CompanyData import CompanyDataModel

# Load environment variables from .env file
load_dotenv()

genai_api_key = os.getenv('GENAI_API_KEY')
client = genai.Client(api_key=genai_api_key)

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

def gather_specific_data(invoices_text: List[str]):
    gathered_information:List[CompanyDataModel] = []
    for text in invoices_text:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=f"""Extract company data from this invoice text. 
                Return ONLY valid JSON with clean string values (no excessive tabs or whitespace):
                
                Company name is a name of company that issued the invoice.
                Invoice ID should be the invoice number/identifier (like "INV-2024-001", "FV/123/2024", etc.)
                
                if currency is zł, pln, or zloty, use "PLN" as the currency.
                if currency is euro, use "EUR" as the currency.
                if currency is dollar, use "USD" as the currency.
                if currency is pound, use "GBP" as the currency.

                Do it with each country:
                For example if country is "Poland", "PL", "POL", "Polska", return "Polska" as the country.
                The same with other countries, like "Germany", "DE", "GER", "Niemcy" should return "Niemcy", etc....
                
                If net_value is not present, but tax_value and gross_value are present, calculate net_value as gross_value-tax_value
                
                Make sure you are gathering finall values of net_value, gross_value, tax_value, after corrects.

                When invoice contains both PLN and EUR currencies:
                - Set currency to "EUR" 
                - Use PLN values for gross_value, net_value, tax_value
                - Set euro_net_value to the EUR net amount found in the invoice
                - If only EUR currency exists, set currency to "EUR" and euro_net_value to 0
                {text}""",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CompanyDataModel,
                    "temperature": 0.1,
                },
            )
            cleaned_response = clean_json_response(response.text)
            data_dict = json.loads(cleaned_response)

            # Clean company name if present
            if 'company_name' in data_dict and isinstance(data_dict['company_name'], str):
                data_dict['company_name'] = re.sub(r'\s+', ' ', data_dict['company_name']).strip()
           
            # Handle Euro currency logic
            if 'euro_net_value' not in data_dict or data_dict['euro_net_value'] == 0.0:
                if 'currency' in data_dict and data_dict['currency'] == 'EUR':
                    data_dict['euro_net_value'] = data_dict.get('net_value', 0.0)
                else:
                    # Keep the euro_net_value from AI response if it exists, otherwise set to 0
                    data_dict['euro_net_value'] = data_dict.get('euro_net_value', 0.0)
            

            company_data = CompanyDataModel(**data_dict)
            gathered_information.append(company_data)

    
        except json.JSONDecodeError as e:
            # Try to create a default CompanyDataModel with fallback values
            try:
                fallback_data = CompanyDataModel(
                    company_name="Błąd danych",
                    invoice_id="",
                    invoice_date="1900-01-01",
                    gross_value=0.0,
                    net_value=0.0,
                    tax_value=0.0,
                    euro_net_value=0.0,
                    currency="Brak",
                    company_country="Brak"
                )
                gathered_information.append(fallback_data)
            except Exception as fallback_error:
                print(f"Failed to create fallback data: {fallback_error}")
                

    return gathered_information