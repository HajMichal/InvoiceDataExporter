from pydantic import BaseModel


class CompanyDataModel(BaseModel):
    company_name: str           # XYZ Company Sp. z o.o.
    invoice_date: str           # 2024-01-01
    invoice_id: str = ""        # 123/2024  
    gross_value: float          # 1000.00
    net_value: float            # 800.00
    tax_value: float            # 200.00
    euro_net_value: float = 0.0   
    currency: str = "PLN"  
    company_country: str = "Polska"
