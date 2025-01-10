from flask import Flask, request, jsonify, send_from_directory
from chromadb_services import chain
from mongo_service import save_chat_to_mongodb, fetch_chat_history, fetch_conversation_messages
from auth_service import sign_up, sign_in
from bson.objectid import ObjectId
import os

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Remove individual routes for static files as Flask will handle them automatically
# with the static_folder configuration

@app.route('/sign-in', methods=['POST'])
def handle_sign_in():
    data = request.json
    user_id = sign_in(data['email'], data['password'])
    if ObjectId.is_valid(user_id):
        return jsonify({"success": True, "userId": str(user_id)})
    else:
        return jsonify({"success": False, "message": user_id})

@app.route('/sign-up', methods=['POST'])
def handle_sign_up():
    data = request.json
    result = sign_up(data['email'], data['password'])
    if result == "Sign-up successful. Please sign in.":
        return jsonify({"success": True, "message": result})
    else:
        return jsonify({"success": False, "message": result})

@app.route('/chat-history', methods=['GET'])
def handle_chat_history():
    user_id = request.args.get('userId')
    chat_history = fetch_chat_history(user_id)
    return jsonify(chat_history)

@app.route('/chat', methods=['POST'])
def handle_chat():
    data = request.json
    user_id = data['userId']
    message = data['message']
    
    save_chat_to_mongodb(user_id, "user", message)
    response = chain.invoke(message)
    save_chat_to_mongodb(user_id, "assistant", response)
    
    return jsonify({"response": response})

@app.route('/chat', methods=['GET'])
def handle_get_chat():
    conversation_id = request.args.get('conversationId')
    messages = fetch_conversation_messages(conversation_id)
    return jsonify(messages)

if __name__ == '__main__':
    # Make sure the static files exist
    required_files = ['index.html', 'styles.css', 'script.js']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Warning: {file} not found in the current directory")
    
    app.run(debug=True, port=7860)