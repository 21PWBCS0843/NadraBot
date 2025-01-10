// Global variables
let currentUserId = null;
let currentConversationId = null;

// DOM Elements
const authContainer = document.getElementById('authContainer');
const chatInterface = document.getElementById('chatInterface');
const chatHistory = document.getElementById('chatHistory');
const chatHistoryList = document.getElementById('chatHistoryList');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const loginButton = document.getElementById('loginButton');
const registerButton = document.getElementById('registerButton');
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// Tab switching functionality
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.add('hidden'));
        
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab') + 'Tab';
        document.getElementById(tabId).classList.remove('hidden');
    });
});

// Login functionality
loginButton.addEventListener('click', async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        alert('Please enter both email and password');
        return;
    }
    
    try {
        const response = await fetch('/sign-in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUserId = data.userId;
            authContainer.classList.add('hidden');
            chatInterface.classList.remove('hidden');
            await loadChatHistory();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred during login. Please try again.');
    }
});

// Register functionality
registerButton.addEventListener('click', async () => {
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const fullName = document.getElementById('fullName').value;
    
    if (!email || !password || !confirmPassword || !fullName) {
        alert('Please fill in all fields');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    try {
        const response = await fetch('/sign-up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, fullName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Switch to login tab
            document.querySelector('[data-tab="login"]').click();
            // Clear registration form
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerPassword').value = '';
            document.getElementById('confirmPassword').value = '';
            document.getElementById('fullName').value = '';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error during registration:', error);
        alert('An error occurred during registration. Please try again.');
    }
});

// Chat functionality
sendButton.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentUserId) return;
    
    chatInput.value = '';
    appendMessage('user', message);
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userId: currentUserId,
                conversationId: currentConversationId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        appendMessage('assistant', data.response);
        
        // Refresh chat history to show new conversation
        await loadChatHistory();
    } catch (error) {
        console.error('Error sending message:', error);
        appendMessage('system', 'Error sending message. Please try again.');
    }
}

function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    if (role === 'assistant') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js';
        document.head.appendChild(script);
        
        script.onload = () => {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
            messageDiv.innerHTML = marked.parse(content);
        };
    } else {
        messageDiv.textContent = content;
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Add these functions to script.js

async function loadChatHistory() {
    try {
        const response = await fetch(`/chat-history?userId=${currentUserId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch chat history');
        }
        
        const history = await response.json();
        chatHistoryList.innerHTML = '';
        
        if (history.length === 0) {
            const emptyState = document.createElement('li');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = `
                <div class="empty-state-message">
                    <p>No conversations yet</p>
                    <p class="subtitle">Start a new conversation!</p>
                </div>
            `;
            chatHistoryList.appendChild(emptyState);
            return;
        }
        
        history.forEach((conversation) => {
            const li = document.createElement('li');
            
            // Format the date nicely
            const date = new Date(conversation.created_at);
            const formattedDate = new Intl.DateTimeFormat('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);
            
            li.innerHTML = `
                <div class="chat-history-item">
                    <div class="chat-history-date">${formattedDate}</div>
                    <div class="chat-preview">
                        <div class="chat-history-preview">${conversation.last_message}</div>
                        <div class="message-count">${conversation.message_count || 0} messages</div>
                    </div>
                </div>
            `;
            
            li.setAttribute('data-id', conversation._id);
            li.addEventListener('click', async () => {
                document.querySelectorAll('#chatHistoryList li').forEach(item => {
                    item.classList.remove('active');
                });
                li.classList.add('active');
                await loadConversation(conversation._id);
            });
            
            chatHistoryList.appendChild(li);
        });
        
        // Select the most recent conversation by default
        if (history.length > 0 && !currentConversationId) {
            const firstItem = chatHistoryList.firstChild;
            firstItem.classList.add('active');
            await loadConversation(history[0]._id);
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
        appendMessage('system', 'Failed to load chat history. Please try again.');
    }
}

async function loadConversation(conversationId) {
    try {
        currentConversationId = conversationId;
        const response = await fetch(`/chat?conversationId=${conversationId}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch conversation messages');
        }
        
        const messages = await response.json();
        
        // Clear current chat display
        chatHistory.innerHTML = '';
        
        if (messages.length === 0) {
            appendMessage('system', 'Start a new conversation!');
            return;
        }
        
        // Display all messages in the conversation
        messages.forEach(message => {
            appendMessage(message.role, message.content);
        });
        
        // Scroll to bottom of chat
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
    } catch (error) {
        console.error('Error loading conversation:', error);
        appendMessage('system', 'Failed to load conversation messages. Please try again.');
    }
}


// Add a system message style to CSS for error messages
const style = document.createElement('style');
style.textContent = `
    .system-message {
        background-color: #ffebee;
        color: #c62828;
        text-align: center;
        font-style: italic;
    }
`;
document.head.appendChild(style);

