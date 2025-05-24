# 🌦️ Weather Agentic AI

An intelligent, conversational weather assistant built with **Streamlit**, **Firebase**, and **ElevenLabs**. Ask weather-related questions via **text or voice**, get precise answers, and hear them spoken back to you.

<div align="center">
  <img src="https://img.shields.io/github/languages/top/Saon110/Weather_Agentic_Ai" />
  <img src="https://img.shields.io/github/last-commit/Saon110/Weather_Agentic_Ai" />
</div>

---

## 🧠 Features

- 💬 Conversational weather assistant
- 🎙️ Voice input using **ElevenLabs Speech-to-Text**
- 🔊 Voice responses with **ElevenLabs Text-to-Speech**
- 💾 Chat memory with Firebase (multiple chat sessions)
- 🧭 Real-time weather data fetching via LLM agent
- 🧹 Delete individual chat sessions
- 📋 Intuitive chat-style UI using **Streamlit**

---

## 📸 Demo

> A screenshot or short gif of your chatbot in action would go here.

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/Saon110/Weather_Agentic_Ai.git
cd Weather_Agentic_Ai
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

**`requirements.txt` includes:**
- `streamlit`
- `speechrecognition`
- `pyaudio`
- `elevenlabs`
- `firebase-admin`
- `requests`
- `python-dotenv`

### 3. Setup API Keys

Create a `.env` file with the following:

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Configure Firebase

Add your Firebase credentials in a `firebase_config.json` file, or modify `firebase_setup.py` to use environment variables.

### 5. Run the App

```bash
streamlit run app.py
```

---

## 🗂 Project Structure

```
.
├── app.py                  # Main Streamlit app
├── firebase_chat.py        # Firebase chat handling
├── firebase_setup.py       # Firebase setup
├── weather_agent.py        # Weather reasoning agent
├── voice_io.py             # Combined voice input/output with ElevenLabs
├── requirements.txt
└── .env
```

---

## 🛠️ TODO

- [ ] Add unit tests
- [ ] Add a frontend for selecting city/location
- [ ] Deploy on Streamlit Cloud or Hugging Face Spaces
- [ ] Support more languages in STT/TTS

---

## 🧑‍💻 Author

Made with 💙 by [**Sijon Chisty Saon**](https://github.com/Saon110)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
