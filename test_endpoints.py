import requests
import os

def test_upload():
    # Test file upload
    files = [('files', ('test_document.txt', open('uploaded_documents/test_document.txt', 'rb')))]
    response = requests.post('http://localhost:8000/upload', files=files)
    print("Upload response:", response.json())

def test_chat():
    # Test chat endpoint
    data = {
        'session_id': '123',
        'message': 'What are the key components of AI mentioned in the document?'
    }
    response = requests.post('http://localhost:8000/chat', data=data)
    print("Chat response:", response.json())

if __name__ == '__main__':
    test_upload()
    test_chat() 