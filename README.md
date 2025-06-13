# NADRA Virtual Assistant

![NADRA Virtual Assistant](https://placeholder.svg?height=200&width=600&text=NADRA+Virtual+Assistant)

A conversational AI assistant that provides information about NADRA (National Database and Registration Authority) services and documentation requirements. This application uses Retrieval Augmented Generation (RAG) to deliver accurate, context-aware responses based on official NADRA documentation.

## Features

- 🔐 **Secure Authentication**: User registration and login system
- 💬 **Conversational Interface**: Natural language chat interface for user queries
- 📚 **Knowledge Base**: Powered by official NADRA documentation
- 📝 **Conversation History**: Persistent storage of user conversations
- 📱 **Responsive Design**: Works on both desktop and mobile devices
- 🧠 **Context-Aware Responses**: AI-generated responses based on document context

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python, Flask
- **Databases**: 
  - MongoDB (user data, conversations)
  - ChromaDB (vector database for RAG)
- **AI/ML**: 
  - OpenAI API
  - LangChain
  - Text Embeddings
- **Authentication**: Custom implementation with password hashing

## Installation

### Prerequisites

- Python 3.8+
- MongoDB
- OpenAI API key

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/nadra-virtual-assistant.git
cd nadra-virtual-assistant
