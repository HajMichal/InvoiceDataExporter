import requests
from typing import Optional


def get_eur_to_pln_rate() -> Optional[float]:
    """
    Fetch current EUR to PLN exchange rate from NBP API (Polish National Bank).
    Returns None if fetching fails.
    """
    try:
        # NBP API endpoint for EUR exchange rate
        url = "http://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rate = data['rates'][0]['mid']
        
        print(f"[OK] Pobrano aktualny kurs EUR/PLN: {rate:.4f}")
        return float(rate)
        
    except Exception as e:
        print(f"[WARN] Nie udało się pobrać kursu EUR/PLN: {e}")
        return None


def get_eur_to_pln_rate_fallback() -> float:
    """
    Try to get current EUR/PLN rate, fallback to multiple sources if primary fails.
    Returns default rate if all sources fail.
    """
    default_rate = 4.25  # Updated to more current rate (as of 2024)
    
    # Try NBP API first (Polish National Bank - official source)
    rate = get_eur_to_pln_rate()
    if rate:
        return rate
    
    # Fallback to exchangerate-api.com
    try:
        url = "https://api.exchangerate-api.com/v4/latest/EUR"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rate = data['rates']['PLN']
        
        print(f"[OK] Pobrano kurs EUR/PLN z exchangerate-api: {rate:.4f}")
        return float(rate)
        
    except Exception as e:
        print(f"[WARN] Backup API też nie działa: {e}")
    
    # Last fallback to fixer.io (requires free API key but has free tier)
    try:
        # You can get free API key at https://fixer.io/
        # For now, we'll use a public endpoint that might work
        url = "https://api.fixer.io/latest?base=EUR&symbols=PLN"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'PLN' in data['rates']:
                rate = data['rates']['PLN']
                print(f"[OK] Pobrano kurs EUR/PLN z fixer.io: {rate:.4f}")
                return float(rate)
                
    except Exception:
        pass
    
    print(f"[WARN] Używam domyślnego kursu EUR/PLN: {default_rate}")
    return default_rate