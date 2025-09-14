import os
import re
from typing import Optional, Tuple


def parse_invoice_filename(filename: str) -> Tuple[str, str, str, Optional[str]]:
    """
    Parse invoice filename to extract company name, invoice number, topic number, and optional type.
    
    Expected format: "companyNum invoiceNum topicNum type(optional).pdf"
    
    Args:
        filename: The filename to parse (with or without extension)
    
    Returns:
        Tuple of (company_name, invoice_number, topic_number, type_or_none)
    
    Raises:
        ValueError: If filename doesn't match expected format
    """
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Split by spaces
    parts = name_without_ext.split()
    
    if len(parts) < 3:
        raise ValueError(f"Plik '{filename}' nie pasuje do oczekiwanego formatu: 'nazwa_firmy numer_faktury numer_tematu typ(opcjonalnie).pdf'")
    elif len(parts) == 3:
        # No type specified
        company_name, invoice_number, topic_number = parts
        invoice_type = None
    elif len(parts) == 4:
        # Type specified
        company_name, invoice_number, topic_number, invoice_type = parts
    else:
        # More than 4 parts - assume the first part is company, last 2-3 are invoice/topic/type
        if len(parts) > 4:
            # Join all parts except the last 2-3 as company name
            company_name = " ".join(parts[:-3]) if len(parts) > 4 else parts[0]
            invoice_number = parts[-3]
            topic_number = parts[-2]
            invoice_type = parts[-1]
        else:
            company_name, invoice_number, topic_number, invoice_type = parts
    
    # Clean up the extracted values
    company_name = company_name.strip()
    invoice_number = invoice_number.strip()
    topic_number = topic_number.strip()
    invoice_type = invoice_type.strip() if invoice_type else None
    
    return company_name, invoice_number, topic_number, invoice_type


def validate_filename_format(filename: str) -> bool:
    """
    Validate if filename matches expected format.
    
    Args:
        filename: The filename to validate
    
    Returns:
        True if filename matches expected format, False otherwise
    """
    try:
        parse_invoice_filename(filename)
        return True
    except ValueError:
        return False


def get_display_name_from_filename(filename: str) -> str:
    """
    Get a display-friendly name from filename for UI purposes.
    
    Args:
        filename: The filename to process
    
    Returns:
        Display-friendly string with parsed information
    """
    try:
        company_name, invoice_number, topic_number, invoice_type = parse_invoice_filename(filename)
        
        display_parts = [
            f"Firma: {company_name}",
            f"Faktury: {invoice_number}",
            f"Temat: {topic_number}"
        ]
        
        if invoice_type:
            display_parts.append(f"Typ: {invoice_type}")
        
        return " | ".join(display_parts)
    
    except ValueError:
        return f"Nieprawidłowy format: {filename}"
