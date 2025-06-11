from database.mongodb import chat_collection

def save_message(user_msg, bot_msg, session_id):
    chat_collection.insert_one({
        "session_id": session_id,
        "user": user_msg,
        "bot": bot_msg
    })

def get_history(session_id):
    return list(chat_collection.find({"session_id": session_id}))
