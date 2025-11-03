import os
import json
import logging
import boto3
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from db import get_db_connection  # Import the connection pool function
from config import AWS_REGION, AWS_SECRET_NAME # Import AWS config

# --- App Setup ---
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_fallback_123!@#')

# --- Logging Setup ---
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# Suppress boto3 logging unless it's an error
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# --- AWS Secrets Manager ---
def get_secret(secret_name=AWS_SECRET_NAME, region_name=AWS_REGION):
    """Fetch the Gemini API key from AWS Secrets Manager."""
    logging.info(f"Attempting to fetch secret '{secret_name}' from region '{region_name}'...")
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]

        try:
            # Look for the key 'GEMINI_SECRET_ID' inside the JSON string
            secret_dict = json.loads(secret)
            api_key = secret_dict.get("GEMINI_SECRET_ID")

            # Fallback to the whole secret string if key missing
            if not api_key:
                api_key = secret
        except json.JSONDecodeError:
            # If secret is a plain string
            api_key = secret

        # Ensure no leading/trailing whitespace
        api_key = api_key.strip()

        logging.info(f"✅ Successfully loaded secret '{secret_name}' from Secrets Manager.")
        return api_key

    except Exception as e:
        logging.error(f"❌ Error fetching secret '{secret_name}': {e}")
        return None

# Fetch secret at startup
GEMINI_API_KEY = get_secret()

# --- Standard Routes ---
@app.route("/")
def index():
    """Renders the home page."""
    return render_template("index.html")

@app.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html")

@app.route("/services")
def services():
    """Renders the services page, fetching data from the DB."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, description, image_url FROM services")
        services_data = cursor.fetchall()
        cursor.close()
        return render_template("services.html", services=services_data)
    except Exception as e:
        logging.error(f"Error fetching services: {e}")
        return render_template("services.html", services=[], error="Could not load services data.")
    finally:
        if conn:
            conn.close()

@app.route("/solutions")
def solutions():
    """Renders the solutions page, fetching data from the DB."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, description, image_url FROM solutions")
        solutions_data = cursor.fetchall()
        cursor.close()
        return render_template("solutions.html", solutions=solutions_data)
    except Exception as e:
        logging.error(f"Error fetching solutions: {e}")
        return render_template("solutions.html", solutions=[], error="Could not load solutions data.")
    finally:
        if conn:
            conn.close()

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Renders the contact page and handles form submission."""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            flash("All fields are required.", "error")
            return render_template("contact.html")

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO contact_submissions (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, message))
            conn.commit() # Commit the transaction
            cursor.close()
            logging.info(f"New contact submission from {name} ({email})")
            flash("Thank you for your message! We will get back to you soon.", "success")
            return redirect(url_for("contact"))
        except Exception as e:
            logging.error(f"Error saving contact submission: {e}")
            flash("An error occurred while sending your message. Please try again.", "error")
        finally:
            if conn:
                conn.close()

    return render_template("contact.html")

# --- AI Lab Routes ---
@app.route("/ai_lab")
def ai_lab():
    """AI Lab interactive image generation page."""
    if not GEMINI_API_KEY:
        logging.warning("⚠️ AI Lab page loaded, but server-side API key is missing.")
    return render_template("ai_lab.html", api_key_available=bool(GEMINI_API_KEY))

@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    """Proxy request to Gemini API, securing the key server-side."""
    if not GEMINI_API_KEY:
        logging.error("❌ /api/generate-image called, but server-side API key is missing.")
        return jsonify({"error": "Server-side API key missing or invalid. Check Flask logs."}), 500

    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    logging.info(f"Generating image for prompt: '{prompt}'")

    # --- Call Google AI API (Imagen 2) ---
    # Note: Using 'imagen-3.0-generate-002' which is a newer model
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    try:
        response = requests.post(API_URL, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status() # Raise an error for bad status codes
        
        result = response.json()

        if "predictions" in result and len(result["predictions"]) > 0 and "bytesBase64Encoded" in result["predictions"][0]:
            base64_image = result["predictions"][0]["bytesBase64Encoded"]
            
            # --- Log successful prompt to DB ---
            conn = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "INSERT INTO ai_lab_generations (prompt) VALUES (%s)"
                cursor.execute(query, (prompt,))
                conn.commit() # <-- **** THIS WAS THE MISSING PIECE ****
                logging.info(f"✅ Successfully logged prompt to DB.")
                cursor.close()
            except Exception as db_e:
                logging.error(f"❌ CRITICAL: Failed to log prompt to DB after generation: {db_e}")
                # Don't fail the whole request, just log the error
            finally:
                if conn:
                    conn.close()
            # ------------------------------------

            return jsonify({"image_data": f"data:image/png;base64,{base64_image}"})
        else:
            logging.error(f"❌ API response was successful but had no valid 'predictions' key. Response: {result}")
            return jsonify({"error": "API returned an unexpected response. Check server logs."}), 500

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"❌ HTTP error calling Google AI: {http_err} - Response: {http_err.response.text}")
        return jsonify({"error": f"API request failed: {http_err}"}), 502
    except Exception as e:
        logging.error(f"❌ Unexpected error during image generation: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500


# --- Main ---
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

