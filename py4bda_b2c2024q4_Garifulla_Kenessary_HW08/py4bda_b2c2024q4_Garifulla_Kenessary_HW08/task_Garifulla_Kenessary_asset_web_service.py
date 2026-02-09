from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from typing import Dict

app = Flask(__name__)

# Global portfolio to store assets
class Asset:
    def __init__(self, char_code, name, capital, interest):
        self.char_code = char_code
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    def __repr__(self):
        return f"Asset({self.name}, {self.capital}, {self.interest})"

    def __eq__(self, rhs):
        return self.name == rhs.name and self.capital == rhs.capital and self.interest == rhs.interest

class Portfolio:
    def __init__(self):
        self.assets = []

    def add(self, asset):
        self.assets.append(asset)

    def list(self):
        return sorted(self.assets, key=lambda x: (x.char_code, x.name))

# Initialize an empty portfolio
app.bank = Portfolio()

# Function to parse the daily currency rates from the CBR website
def parse_cbr_currency_base_daily(html_data: str) -> Dict[str, float]:
    soup = BeautifulSoup(html_data, "html.parser")
    currencies = {}
    for row in soup.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        char_code = cols[0].text.strip()
        try:
            rate = float(cols[1].text.strip().replace(",", "."))
            currencies[char_code] = rate
        except ValueError:
            continue  # Skip rows where the rate cannot be converted to float
    return currencies

# Function to parse the key indicators page from the CBR website
def parse_cbr_key_indicators(html_data: str) -> Dict[str, float]:
    soup = BeautifulSoup(html_data, "html.parser")
    indicators = {}
    for row in soup.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        char_code = cols[0].text.strip()
        if char_code in ["USD", "EUR", "XAU", "XAG", "XPT", "XPD"]:  # Currencies and precious metals
            try:
                rate = float(cols[1].text.strip().replace(",", "."))
                indicators[char_code] = rate
            except ValueError:
                continue  # Skip rows where the rate can't be parsed
    return indicators

@app.route("/cbr/daily", methods=["GET"])
def cbr_currency_base_daily():
    try:
        response = requests.get("https://www.cbr.ru/eng/currency_base/daily/")
        response.raise_for_status()
        data = parse_cbr_currency_base_daily(response.text)
        return jsonify(data)
    except requests.exceptions.RequestException:
        return "CBR service is unavailable", 503

@app.route("/cbr/key_indicators", methods=["GET"])
def cbr_key_indicators():
    try:
        response = requests.get("https://www.cbr.ru/eng/key-indicators/")
        response.raise_for_status()
        data = parse_cbr_key_indicators(response.text)
        return jsonify(data)
    except requests.exceptions.RequestException:
        return "CBR service is unavailable", 503

@app.route("/api/asset/add/<char_code>/<name>/<float:capital>/<float:interest>", methods=["GET"])
def add_asset(char_code, name, capital, interest):
    for asset in app.bank.assets:
        if asset.name == name:
            return f"Asset '{name}' already exists", 403
    
    asset = Asset(char_code, name, capital, interest)
    app.bank.add(asset)
    return f"Asset '{name}' was successfully added", 200

@app.route("/api/asset/list", methods=["GET"])
def list_assets():
    assets = app.bank.list()
    return jsonify([[asset.char_code, asset.name, asset.capital, asset.interest] for asset in assets])

@app.route("/api/asset/get", methods=["GET"])
def get_assets():
    names = request.args.getlist("name")
    assets = [asset for asset in app.bank.assets if asset.name in names]
    return jsonify([[asset.char_code, asset.name, asset.capital, asset.interest] for asset in assets])

@app.route("/api/asset/calculate_revenue", methods=["GET"])
def calculate_revenue():
    period_1 = int(request.args.get("period_1"))
    period_2 = int(request.args.get("period_2"))
    
    revenue = {}
    for asset in app.bank.assets:
        if asset.char_code in ["USD", "EUR", "XAU", "XAG", "XPT", "XPD"]:
            response = requests.get("https://www.cbr.ru/eng/key-indicators/")
            data = parse_cbr_key_indicators(response.text)
            rate = data.get(asset.char_code, 1)
        else:
            response = requests.get("https://www.cbr.ru/eng/currency_base/daily/")
            data = parse_cbr_currency_base_daily(response.text)
            rate = data.get(asset.char_code, 1)
        
        revenue[asset.name] = asset.capital * (1 + asset.interest * (period_2 - period_1))
    
    return jsonify({"period_1": revenue})

@app.route("/api/asset/cleanup", methods=["GET"])
def cleanup_assets():
    app.bank.assets = []
    return "There are no more assets", 200

@app.errorhandler(404)
def page_not_found(error):
    return "This route is not found", 404

if __name__ == "__main__":
    app.run(debug=True)

