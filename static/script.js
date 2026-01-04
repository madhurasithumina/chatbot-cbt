let sessionId = null;
const API_BASE_URL = 'http://localhost:8000';

// Initialize the chat
async function initializeChat() {
    try {
        const response = await fetch(`${API_BASE_URL}/session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error('Failed to create session');
        }
        
        const data = await response.json();
        sessionId = data.session_id;
        
        updateStatus('connected', 'Connected');
        removeWelcomeMessage();
    } catch (error) {
        console.error('Error initializing chat:', error);
        updateStatus('error', 'Connection Error - Start API Server');
        showErrorMessage('Could not connect to server. Make sure to run: python main.py');
    }
}

function updateStatus(status, text) {
    const indicator = document.getElementById('status');
    const statusText = document.getElementById('status-text');
    
    indicator.className = `status-indicator ${status}`;
    statusText.textContent = text;
}

function removeWelcomeMessage() {
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
}

function showErrorMessage(message) {
    const chatContainer = document.getElementById('chat-container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message bot';
    errorDiv.innerHTML = `
        <div class="message-content" style="background: #fee2e2; color: #991b1b; border-left: 4px solid #ef4444;">
            <strong>⚠️ Error:</strong> ${message}
        </div>
    `;
    chatContainer.appendChild(errorDiv);
    scrollToBottom();
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!sessionId) {
        await initializeChat();
        if (!sessionId) return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response
        addMessage(data.response, 'bot', data.emotional_state, data.metadata);
        
        // Update emotional state
        updateEmotionalState(data.emotional_state);
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        showErrorMessage('Failed to get response. Please try again.');
    }
}

function addMessage(text, sender, emotionalState = null, metadata = null) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    let metaInfo = '';
    if (sender === 'bot' && metadata) {
        const source = metadata.primary_source || 'hybrid';
        const confidence = metadata.custom_confidence ? 
            `${(metadata.custom_confidence * 100).toFixed(0)}%` : 'N/A';
        metaInfo = `<div class="message-meta">Source: ${source} | Confidence: ${confidence}</div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${text}
            ${metaInfo}
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const chatContainer = document.getElementById('chat-container');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function updateEmotionalState(state) {
    const emotionalStateEl = document.getElementById('emotional-state');
    if (state && state !== 'NEUTRAL') {
        const emoji = {
            'ANXIOUS': '😰',
            'DEPRESSED': '😔',
            'STRESSED': '😓',
            'CALM': '😌',
            'UNKNOWN': '🤔'
        };
        emotionalStateEl.textContent = `${emoji[state] || '💭'} Detected: ${state.toLowerCase()}`;
    } else {
        emotionalStateEl.textContent = '';
    }
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendQuickMessage(message) {
    document.getElementById('user-input').value = message;
    sendMessage();
}

async function clearChat() {
    if (!confirm('Are you sure you want to clear the conversation?')) {
        return;
    }
    
    // End current session
    if (sessionId) {
        try {
            await fetch(`${API_BASE_URL}/session/${sessionId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }
    
    // Clear chat container
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <div class="bot-icon">🤖</div>
            <h2>Welcome!</h2>
            <p>I'm here to provide CBT-based support and guidance. How are you feeling today?</p>
            <div class="quick-buttons">
                <button class="quick-btn" onclick="sendQuickMessage('I\\'ve been feeling anxious lately')">😰 Feeling Anxious</button>
                <button class="quick-btn" onclick="sendQuickMessage('I\\'m feeling stressed about work')">😓 Work Stress</button>
                <button class="quick-btn" onclick="sendQuickMessage('I\\'m having trouble sleeping')">😴 Sleep Issues</button>
                <button class="quick-btn" onclick="sendQuickMessage('I feel overwhelmed')">😔 Feeling Overwhelmed</button>
            </div>
        </div>
    `;
    
    // Reset state
    sessionId = null;
    document.getElementById('emotional-state').textContent = '';
    
    // Initialize new session
    await initializeChat();
}

async function exportHistory() {
    if (!sessionId) {
        alert('No conversation to export');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/session/${sessionId}/history`);
        if (!response.ok) {
            throw new Error('Failed to get history');
        }
        
        const data = await response.json();
        
        // Create downloadable file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting history:', error);
        alert('Failed to export history');
    }
}

// Auto-resize textarea
document.getElementById('user-input').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Initialize on load
window.addEventListener('load', initializeChat);
