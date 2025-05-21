from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

API_URL = "https://www.passeport-valaisan.ch/wp-json/passval/v1/getAllOffers"

def parse_category(cat_string):
    try:
        return json.loads(cat_string)
    except Exception:
        return []

def filter_offers(offers, location=None, category=None, accessible_only=False):
    filtered = []

    for offer in offers:
        if not isinstance(offer, dict):
            continue

        try:
            title = offer.get("Titre", "")
            partner = offer.get("Partenaire", "")
            description = offer.get("Description", "")
            address = offer.get("Localisation", {}).get("address", "")
            categories = parse_category(offer.get("Catégorie", "[]"))
            # NOTE : pas d'info réelle sur l'accessibilité, donc ignorée ici
        except Exception as e:
            print(f"Erreur de parsing pour une offre : {e}")
            continue

        # Filtrage par lieu
        if location and location.lower() not in address.lower():
            continue

        # Filtrage par catégorie
        if category and category.lower() not in [c.lower() for c in categories]:
            continue

        filtered.append({
            "title": title,
            "partner": partner,
            "description": description,
            "address": address,
            "category": categories,
            "image": offer.get("Image", ""),
            "discount": offer.get("Rabais", "")
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
        all_offers = list(response.json().values())
        results = filter_offers(all_offers, location, category, accessible)
        return jsonify(results)

    except Exception as e:
        import traceback
        print("Erreur serveur :", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
