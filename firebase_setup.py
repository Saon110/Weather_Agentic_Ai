import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate("weather-ai-agent-1c82f-firebase-adminsdk-fbsvc-6133cd3cea.json")  # Download this from Firebase Console
        firebase_admin.initialize_app(cred)
    return firestore.client()




