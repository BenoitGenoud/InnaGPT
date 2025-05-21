from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://www.passeport-valaisan.ch/wp-json/passval/v1/getAllOffers"

def filter_offers(offers, location=None, category=None, accessible_only=False):
    filtered = []

    for offer in offers:
        if not isinstance(offer, dict):
            continue  # On ignore les formats inattendus

        try:
            title = offer.get("title", "")
            region = offer.get("region", "").lower()
            thematics = offer.get("thematique", [])
            access_info = offer.get("mobilite_reduite", "").lower()
            description = offer.get("description", "")
        except Exception as e:
            print(f"Erreur de parsing pour une offre : {e}")
            continue

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

        # Convertit le dict en liste
        all_offers = list(all_offers.values())

        results = filter_offers(all_offers, location, category, accessible)
        return jsonify(results)

    except Exception as e:
        import traceback
        print("Erreur serveur :", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
