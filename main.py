import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import cloudscraper
from bs4 import BeautifulSoup

app = FastAPI()

# Use environment variable for API key, fallback to default
API_KEY = os.getenv("API_KEY", "vedeep05harsha7586444322ud33enrjjtt")

shortcut_map = {
    "AN": "Andaman and Nicobar", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
    "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CT": "Chhattisgarh",
    "DN": "Dadra and Nagar Haveli", "DD": "Daman and Diu", "DL": "Delhi",
    "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir", "JH": "Jharkhand", "KA": "Karnataka",
    "KL": "Kerala", "MP": "Madhya Pradesh", "MH": "Maharashtra",
    "MN": "Manipur", "ML": "Meghalaya", "MZ": "Mizoram", "NL": "Nagaland",
    "OR": "Odisha", "PY": "Puducherry", "PB": "Punjab", "RJ": "Rajasthan",
    "SK": "Sikkim", "TN": "Tamil Nadu", "TG": "Telangana", "TR": "Tripura",
    "UP": "Uttar Pradesh", "UK": "Uttarakhand", "WB": "West Bengal"
}

petrol_urls = {
    state: f"https://www.goodreturns.in/petrol-price-in-{state.lower().replace(' ', '-')}-s{i+1}.html"
    for i, state in enumerate(shortcut_map.values())
}

scraper = cloudscraper.create_scraper()

def resolve_state(user_input):
    user_input = user_input.strip().lower()
    for code, full_name in shortcut_map.items():
        if user_input == code.lower():
            return full_name
    for full_name in petrol_urls.keys():
        if user_input == full_name.lower() or full_name.lower().startswith(user_input):
            return full_name
    return None

def get_price(state_name):
    url = petrol_urls.get(state_name)
    if not url:
        return None, f"State '{state_name}' not found"
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find('div', class_='gd-fuel-price')
        if price_div:
            price = price_div.text.strip().split('/')[0].strip()
            return price, None
        else:
            return None, f"Price not found for {state_name}"
    except Exception as e:
        return None, str(e)

@app.get("/petrol-price/")
async def fetch_price(state: str, api_key: Optional[str] = None):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    resolved = resolve_state(state)
    if not resolved:
        raise HTTPException(status_code=404, detail="State not recognized")

    price, error = get_price(resolved)
    if error:
        return JSONResponse(status_code=500, content={"error": error})

    return {"state": resolved, "petrol_price": price}
