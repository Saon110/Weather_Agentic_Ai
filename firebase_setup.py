import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate("weather-ai-agent-1c82f-firebase-adminsdk-fbsvc-6133cd3cea.json")  # Download this from Firebase Console
        firebase_admin.initialize_app(cred)
    return firestore.client()




# // Import the functions you need from the SDKs you need
# import { initializeApp } from "firebase/app";
# import { getAnalytics } from "firebase/analytics";
# // TODO: Add SDKs for Firebase products that you want to use
# // https://firebase.google.com/docs/web/setup#available-libraries

# // Your web app's Firebase configuration
# // For Firebase JS SDK v7.20.0 and later, measurementId is optional
# const firebaseConfig = {
#   apiKey: "AIzaSyByqvVr04fryNuMlsxLu5PpU5GxaD4iauY",
#   authDomain: "weather-ai-agent-1c82f.firebaseapp.com",
#   projectId: "weather-ai-agent-1c82f",
#   storageBucket: "weather-ai-agent-1c82f.firebasestorage.app",
#   messagingSenderId: "737206906452",
#   appId: "1:737206906452:web:2472ce19cce68d63da87c1",
#   measurementId: "G-FCH9N2LXNZ"
# };

# // Initialize Firebase
# const app = initializeApp(firebaseConfig);
# const analytics = getAnalytics(app);