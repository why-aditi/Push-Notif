from flask import Flask, request, jsonify
from routes.add_user import subscription
from routes.notif import send_push_notification, send_broadcast_notification
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}}) 


@app.route("/", methods=["GET", "POST"])
def home():
    return "Hello"

@app.route("/subscription", methods=["GET", "POST"])
def subscription_route():
    return subscription()

@app.route("/notif", methods=["POST"])
def notif_route():
    try:
        data = request.get_json()
        subscription_id = data.get("subscription_id")
        message = data.get("message")

        if not message:
            return jsonify({"error": "Missing message in request"}), 400
        
        if subscription_id:
            response_message, status_code = send_push_notification(subscription_id, message)
        else:
            response_message, status_code = send_broadcast_notification(message)
        
        return jsonify({"message": response_message}), status_code
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8000, debug=True)