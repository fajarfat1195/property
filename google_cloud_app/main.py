import os
from flask import Flask, jsonify, request
import zoho_crm_api_module as crm  
import hmac
import hashlib

# AUTH_TOKEN di define ulang disini, supaya ketika menjalankannya di lokal. AUTH_TOKEN tetap dikenali
# Value variable ini juga di taruh di variable and secrets
# Jadi jika ingin digunakan di project sungguhan dan running di cloud, cukup get "AUTH TOKEN" saja. Jangan define valuenya lagi
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "fajarfatoni123456")  # Static password

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))

# --- Fungsi Bantuan ---
def footer(author="Gemini"):
    return f"\n\n--- Dibuat oleh {author} untuk Cloud Run ---"

def require_auth(func):
    """Decorator untuk proteksi endpoint dengan static token."""
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-API-KEY")
        if token != AUTH_TOKEN:
            return jsonify({"status": "ERROR", "message": "Unauthorized"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# --- ROUTES ---

@app.route("/", methods=["GET", "POST"])
@require_auth
def home():
    """Endpoint utama untuk pengecekan deploy."""
    message = f". Aplikasi Cloud Run Anda berhasil di-deploy."
    return message + footer()

@app.route("/get-leads", methods=["GET", "POST"])
@require_auth
def get_leads():
    # Alphabetical order for local variables
    access_token_val = crm.get_crm_token()
    get_id = request.args.get("id") or request.form.get("id")
    target_columns = ["id", "Last_Name", "Email", "Lead_Status"] 
    
    # Conditional logic for fetching data
    if get_id:
        leads_list = crm.get_leads_data(access_token_val, cols=target_columns, id=get_id)
    else:
        leads_list = crm.get_leads_data(access_token_val, cols=target_columns)
    
    data_response = {
        "access_token": access_token_val,
        "footer": footer(),
        "leads": leads_list,
        "status": "SUCCESS"
    }
    
    return jsonify(data_response), 200


@app.route("/push-leads", methods=["POST"])
@require_auth
def push_leads():
    # A. Get the JSON data sent to this API
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({"status": "ERROR", "message": "No data provided"}), 400

    # B. Get the access token
    token_value = crm.get_crm_token()
    
    # C. Push to Zoho
    result, status_code = crm.push_leads_data(token_value, request_data)
    
    # D. Return the Zoho response
    return jsonify({
        "status": "SUCCESS" if status_code in [200, 201] else "FAILED",
        "zoho_response": result
    }), status_code

@app.route("/update-lead", methods=["PUT"])
@require_auth
def update_lead():
    # Mengambil token dan body request
    access_token_val = crm.get_crm_token()
    request_data = request.json.get("data") # Mengambil list 'data' dari JSON input
    
    if not request_data:
        return jsonify({"message": "Data tidak ditemukan", "status": "ERROR"}), 400
    
    # Memanggil fungsi update
    update_result = crm.update_lead_data(access_token_val, request_data)
    
    # Menyusun respons secara alfabetis
    data_response = {
        "access_token": access_token_val,
        "footer": footer(),
        "result": update_result,
        "status": "SUCCESS"
    }
    
    return jsonify(data_response), 200


# --- Mode Lokal ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

