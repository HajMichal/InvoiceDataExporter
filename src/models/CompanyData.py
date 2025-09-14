from pydantic import BaseModel
from typing import Optional


class CompanyDataModel(BaseModel):
    # Data extracted from filename
    company_name: str           # Company name from filename
    invoice_number: str         # Invoice number from filename
    topic_number: str           # Topic number from filename  
    invoice_type: Optional[str] = None  # Optional type from filename
    
    # Data extracted from invoice content via AI
    net_value: float            # Net amount (netto)
    gross_value: float          # Gross amount (brutto) 
    vat_value: float            # VAT amount (podatek VAT)
    
    # Derived/calculated fields
    currency: str = "PLN"       # Currency detected from invoice
    filepath: str = ""          # Original file path for reference
