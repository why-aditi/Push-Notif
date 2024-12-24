from db import user_info
from pywebpush import webpush  
from VAPID import VAPID_PRIVATE_KEY, VAPID_CLAIMS
import logging
from flask import json

def send_push_notification(subscription_id, message):
    try:
        subscription = user_info.find_one({"userId": subscription_id})
        if not subscription:
            return "Subscription not found", 404
        
        subscription_info = {
            "endpoint": subscription["endpoint"],
            "keys": {
                "p256dh": subscription["keys"]["p256dh"],
                "auth": subscription["keys"]["auth"]
            }
        }
        
        notification_payload = {
            "title": message["title"],
            "body": message["body"],
            "url": message.get("url", ""),
            "favicon": message.get("favicon", "")
        }
        
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(notification_payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        
        logging.info(f"Notification sent to {subscription_id}")
        return "Notification sent successfully", 200
    
    except Exception as e:
        logging.error(f"Error sending push notification: {e}")
        return str(e), 500
    
def send_broadcast_notification(message):
    try:
        subscriptions = list(user_info.find())
        
        if not subscriptions:
            return "No subscriptions found.", 404

        users = [{
            "endpoint": subs["endpoint"],
            "keys": {
                "p256dh": subs["keys"]["p256dh"],
                "auth": subs["keys"]["auth"]
            }
        } for subs in subscriptions]
        
        notification_payload = {
            "title": message["title"],
            "body": message["body"],
            "url": message.get("url", ""),
            "icon": message.get("favicon", "")
        }

        logging.info(f"Sending to {len(users)} users")
        for user in users:
            webpush(
                subscription_info=user,
                data=json.dumps(notification_payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
            logging.info(f"Notification sent to {user['endpoint']}")
        
        return "Notification sent successfully to all valid subscriptions.", 200
    
    except Exception as e:
        logging.error(f"Error during broadcast: {e}")
        return str(e), 500