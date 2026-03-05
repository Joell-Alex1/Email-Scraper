from flask import Flask, request, jsonify
from email_scraper import scrape_website

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape():

    url = request.args.get("url")

    if not url:
        return jsonify({"error": "URL parameter missing"}), 400

    emails = scrape_website(url)

    return jsonify({
        "emails": list(emails)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)