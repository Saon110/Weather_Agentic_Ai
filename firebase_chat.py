from firebase_setup import init_firestore
from google.cloud import firestore
from datetime import datetime
import uuid
import pytz

db = init_firestore()
bd_tz = pytz.timezone("Asia/Dhaka")  # Bangladesh Time Zone

def create_new_chat(user_id="default"):
    chat_id = str(uuid.uuid4())
    db.collection("chats").document(chat_id).set({
        "user_id": user_id,
        "created_at": firestore.SERVER_TIMESTAMP,
    })
    return chat_id

def add_message(chat_id, role, content):
    db.collection("chats").document(chat_id).collection("messages").add({
        "role": role,
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })

def get_recent_messages(chat_id):
    chat_ref = db.collection("chats").document(chat_id).collection("messages")
    messages = chat_ref.order_by("timestamp").stream()
    return [{"role": msg.to_dict()["role"], "content": msg.to_dict()["content"]} for msg in messages]

def list_user_chats(user_id="default"):
    chats = db.collection("chats").where("user_id", "==", user_id).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    
    chat_list = []
    for chat in chats:
        data = chat.to_dict()
        created_at_utc = data.get("created_at")

        if created_at_utc:
            created_at_bd = created_at_utc.astimezone(bd_tz)
        else:
            created_at_bd = None

        chat_list.append((chat.id, created_at_bd))

    return chat_list

def delete_chat(chat_id):
    messages_ref = db.collection("chats").document(chat_id).collection("messages")
    for msg in messages_ref.stream():
        msg.reference.delete()
    db.collection("chats").document(chat_id).delete()
