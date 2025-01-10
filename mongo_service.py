from pymongo import MongoClient, ASCENDING
from datetime import datetime
from bson.objectid import ObjectId

# MongoDB connection string
connection_string = "mongodb://localhost:27017"

def save_chat_to_mongodb(user_id, role, content):
    """
    Save a chat message in the MongoDB database.

    Args:
        user_id (str): User's unique ID.
        role (str): Role of the message sender ("user" or "assistant").
        content (str): Message content.
    """
    with MongoClient(connection_string) as client:
        db = client["nadra"]
        
        # Get or create a new conversation
        conversations = db["conversations"]
        current_conversation = conversations.find_one(
            {"user_id": user_id, "status": "active"},
            sort=[("created_at", -1)]
        )
        
        if not current_conversation:
            conversation_id = conversations.insert_one({
                "user_id": user_id,
                "status": "active",
                "created_at": datetime.utcnow(),
                "last_message": content[:50] + "..." if len(content) > 50 else content
            }).inserted_id
        else:
            conversation_id = current_conversation["_id"]
            conversations.update_one(
                {"_id": conversation_id},
                {"$set": {"last_message": content[:50] + "..." if len(content) > 50 else content}}
            )
        
        # Save the message
        messages = db["messages"]
        messages.insert_one({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        })

def fetch_chat_history(user_id: str):
    """
    Fetch all conversations for a user.

    Args:
        user_id (str): The user's unique identifier.

    Returns:
        list: List of conversations with their last messages.
    """
    with MongoClient(connection_string) as client:
        conversations = client["nadra"]["conversations"]
        history = list(conversations.find(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        ))
        
        # Convert ObjectId to string for JSON serialization
        for conv in history:
            conv["_id"] = str(conv["_id"])
        
        return history

def fetch_conversation_messages(conversation_id: str):
    """
    Fetch all messages for a specific conversation.

    Args:
        conversation_id (str): The conversation's unique identifier.

    Returns:
        list: List of messages in the conversation.
    """
    with MongoClient(connection_string) as client:
        messages = client["nadra"]["messages"]
        conversation_messages = list(messages.find(
            {"conversation_id": ObjectId(conversation_id)},
            sort=[("timestamp", ASCENDING)]
        ))
        
        # Convert ObjectId to string for JSON serialization
        for msg in conversation_messages:
            msg["_id"] = str(msg["_id"])
            msg["conversation_id"] = str(msg["conversation_id"])
        
        return conversation_messages

        # Update the fetch_chat_history function in mongo_service.py

def fetch_chat_history(user_id: str):
    """
    Fetch all conversations for a user with message counts.

    Args:
        user_id (str): The user's unique identifier.

    Returns:
        list: List of conversations with their last messages and message counts.
    """
    with MongoClient(connection_string) as client:
        db = client["nadra"]
        conversations = db["conversations"]
        messages = db["messages"]
        
        # Get all conversations for the user
        user_conversations = list(conversations.find(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        ))
        
        # Add message count for each conversation
        for conv in user_conversations:
            message_count = messages.count_documents({"conversation_id": conv["_id"]})
            conv["message_count"] = message_count
            conv["_id"] = str(conv["_id"])
        
        return user_conversations