from flask import Blueprint, request, jsonify
from services.gemini_service import get_gemini_response
from models.chat_history import save_message, get_history

# ✅ Define the Blueprint
chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    session_id = request.json.get('session_id', 'default')

    bot_response = get_gemini_response(session_id, user_message)
    save_message(user_message, bot_response, session_id)

    return jsonify({'response': bot_response})

# ✅ Route to get chat history
@chat_bp.route('/history', methods=['GET'])
def history():
    session_id = request.args.get('session_id', 'default')
    history = get_history(session_id)

    cleaned_history = [
        {"user": chat["user"], "bot": chat["bot"]}
        for chat in history
    ]
    return jsonify({"history": cleaned_history})
