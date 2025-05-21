from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://www.passeport-valaisan.ch/wp-json/passval/v1/getAllOffers"

def filter_offers(offers, location=None, category=None, accessible_only=False):
    filtered = []

    for offer in offers:
        title = offer.get("title", {}).get("rendered", "")
        region = offer.get("acf", {}).get("region", "").lower()
        thematics = offer.get("acf", {}).get("thematique", [])
        access_info = offer.get("acf", {}).get("mobilite_reduite", "").lower()
        description = offer.get("acf", {}).get("description", "")

        # Filtrage
        if location and location.lower() not in region:
            continue
        if category and category.lower() not in [cat.lower() for cat in thematics]:
            continue
        if accessible_only and access_info != "oui":
            continue

        filtered.append({
            "title": title,
            "region": region,
            "category": thematics,
            "accessible": access_info,
            "description": description
        })

    return filtered

@app.route("/getOffers", methods=["GET"])
def get_filtered_offers():
    location = request.args.get("location")
    category = request.args.get("category")
    accessible = request.args.get("accessible", "false").lower() == "true"

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        all_offers = response.json()
        results = filter_offers(all_offers, location, category, accessible)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
