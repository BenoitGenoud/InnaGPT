from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_offers(location=None, category=None, accessible_only=False):
    url = "https://www.passeport-valaisan.ch/wp-json/passval/v1/getAllOffers"
    response = requests.get(url)
    offers = response.json()
    filtered = []

    for offer in offers:
        title = offer.get("title", {}).get("rendered", "")
        region = offer.get("acf", {}).get("region", "").lower()
        thematics = offer.get("acf", {}).get("thematique", [])
        access_info = offer.get("acf", {}).get("mobilite_reduite", "")

        if location and location.lower() not in region:
            continue
        if category and category.lower() not in [cat.lower() for cat in thematics]:
            continue
        if accessible_only and access_info.lower() != "oui":
            continue

        filtered.append({
            "title": title,
            "region": region,
            "category": thematics,
            "accessible": access_info,
            "description": offer.get("acf", {}).get("description", "")
        })

    return filtered

@app.route("/getOffers", methods=["GET"])
def offers():
    location = request.args.get("location")
    category = request.args.get("category")
    accessible = request.args.get("accessible", "false").lower() == "true"
    data = get_offers(location, category, accessible)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
