import json
from flask import jsonify, request, Response, abort
from db import user_info
from schema.user import Subscriber
from pydantic import ValidationError
from VAPID import VAPID_PUBLIC_KEY
import traceback

def subscription():
    """
    POST: Creates a subscription and saves it to the database.
    GET: Returns the VAPID public key which clients use to send push notifications.
    """
    if request.method == "GET":
        # Return VAPID public key
        return Response(
            response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
            headers={"Access-Control-Allow-Origin": "*"},
            content_type="application/json"
        )

    if request.method == "POST":
        try:
            # Parse subscription token from request
            subscription_data = request.get_json()
            if not subscription_data:
                abort(400, "Missing subscription data")
            
            # Validate subscription with Pydantic
            try:
                subscriber = Subscriber(**subscription_data)
            except ValidationError as e:
                return jsonify({"error": "Invalid subscription data", "details": e.errors()}), 400
            
            # Check if the user exists based on some unique identifier (e.g., user_id or email)
            existing_user = user_info.find_one({"user_id": subscriber.userId})
            if existing_user:
                # If user exists but endpoint is different, add a new subscription entry
                existing_endpoint = existing_user.get('endpoint')
                if existing_endpoint != subscriber.endpoint:
                    # Insert the new subscription
                    user_info.insert_one(subscriber.dict())
                    return jsonify({"message": "New subscription added for user"}), 201
                else:
                    return jsonify({"message": "Subscription already exists for this user"}), 200

            # If the user does not exist, create a new entry with the subscription
            user_info.insert_one(subscriber.dict())
            return jsonify({"message": "Subscription saved successfully"}), 201


        except Exception as e:
            print(f"Error: {str(e)}")
            print("Stack trace:")
            traceback.print_exc()
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
