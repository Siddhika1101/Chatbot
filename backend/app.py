# Load environment variables and set API key
import os
from dotenv import load_dotenv
load_dotenv()

# Set API key directly for testing
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCgFSCWM0VolY6EKlI2I1DlAs8eVWX89zo'

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
# from .services.document_service import document_service
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from services.gemini_service import get_gemini_response
# from .services.document_service import load_documents, query_documents
import shutil

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot_db']
chat_sessions = db['chat_sessions']

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("No Google API key found. Please set the GOOGLE_API_KEY environment variable.")

try:
    # Configure the API
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Initialize the model
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    
    # Test the model
    print("\nTesting model connection...")
    test_response = model.generate_content("Hello")
    print("Model connection successful!")
    
except Exception as e:
    print(f"Error initializing Gemini API: {str(e)}")
    raise

# @app.route('/api/upload-document', methods=['POST'])
# def upload_document():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file provided'}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
            
#         # Process the document
#         result = document_service.process_file(file)
#         return jsonify(result)
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not request.json:
            return jsonify({'error': 'Invalid request'}), 400

        session_id = request.json.get('sessionId')
        user_message = request.json.get('message')
        
        if not session_id or not user_message:
            return jsonify({'error': 'Message and sessionId are required'}), 400
        
        if not user_message.strip():
            return jsonify({'error': 'Empty message'}), 400
        
        try:
            # Generate response using Gemini
            response = model.generate_content(user_message)
            if not response or not hasattr(response, 'text'):
                return jsonify({'error': 'Invalid response from Gemini API'}), 500
            bot_response = response.text

            # Update session in database
            chat_sessions.update_one(
                {'_id': ObjectId(session_id)},
                {
                    '$push': {
                        'messages': {
                            'user': user_message,
                            'bot': bot_response,
                            'timestamp': datetime.utcnow()
                        }
                    }
                }
            )
            
            # Get updated session
            session = chat_sessions.find_one({'_id': ObjectId(session_id)})
            return jsonify({
                'response': bot_response,
                'session': {
                    'id': str(session['_id']),
                    'title': session['title'],
                    'messages': session['messages']
                }
            })

        except Exception as api_error:
            print(f"API Error: {str(api_error)}")
            return jsonify({'error': f'API error: {str(api_error)}'}), 500
            
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    try:
        all_sessions = list(chat_sessions.find())
        return jsonify([{
            'id': str(session['_id']),
            'title': session['title'],
            'messages': session['messages']
        } for session in all_sessions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        session_count = chat_sessions.count_documents({})
        new_session = {
            'title': f'Chat {session_count + 1}',
            'messages': [],
            'created_at': datetime.utcnow()
        }
        result = chat_sessions.insert_one(new_session)
        return jsonify({
            'id': str(result.inserted_id),
            'title': new_session['title'],
            'messages': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['PUT'])
def update_session(session_id):
    try:
        updates = request.json
        chat_sessions.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': updates}
        )
        session = chat_sessions.find_one({'_id': ObjectId(session_id)})
        return jsonify({
            'id': str(session['_id']),
            'title': session['title'],
            'messages': session['messages']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        chat_sessions.delete_one({'_id': ObjectId(session_id)})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# FastAPI setup
fast_app = FastAPI()

# Configure CORS
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fast_app.post("/chat")
async def chat(session_id: str = Form(...), message: str = Form(...)):
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API key not found")
        
        response = get_gemini_response(session_id, message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    import uvicorn
    uvicorn.run(fast_app, host="0.0.0.0", port=8000)
