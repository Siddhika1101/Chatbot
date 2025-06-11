# services/gemini_service.py
import os
import google.generativeai as genai

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("No Google API key found. Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Keep track of chat context per session
chat_sessions = {}

def get_gemini_response(session_id, message):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
    
    chat = chat_sessions[session_id]
    
    try:
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
