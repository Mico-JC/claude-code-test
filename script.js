class MatrixTerminal {
    constructor() {
        this.canvas = document.getElementById('matrix-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.connectionStatus = document.getElementById('connection-status');

        // Matrix animation variables
        this.matrix = [];
        this.matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()';
        this.fontSize = 14;
        this.columns = 0;

        // N8N webhook URL - dynamic based on environment
        this.n8nWebhookUrl = this.getWebhookUrl();

        this.init();
    }

    getWebhookUrl() {
        // Check if we're running on localhost (development)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000/webhook';
        }
        // Production - use Vercel API endpoint
        return '/api/webhook';
    }

    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.startMatrixAnimation();
        this.focusInput();
    }

    setupCanvas() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);

        // Initialize matrix array
        this.matrix = [];
        for (let x = 0; x < this.columns; x++) {
            this.matrix[x] = Math.floor(Math.random() * this.canvas.height / this.fontSize);
        }
    }

    startMatrixAnimation() {
        const animate = () => {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

            this.ctx.fillStyle = '#00ff00';
            this.ctx.font = `${this.fontSize}px monospace`;

            for (let i = 0; i < this.matrix.length; i++) {
                const text = this.matrixChars[Math.floor(Math.random() * this.matrixChars.length)];
                this.ctx.fillText(text, i * this.fontSize, this.matrix[i] * this.fontSize);

                if (this.matrix[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
                    this.matrix[i] = 0;
                }
                this.matrix[i]++;
            }

            requestAnimationFrame(animate);
        };
        animate();
    }

    setupEventListeners() {
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.messageInput.value.trim()) {
                this.sendMessage(this.messageInput.value.trim());
                this.messageInput.value = '';
            }
        });

        this.messageInput.addEventListener('focus', () => {
            document.querySelector('.input-cursor').style.display = 'none';
        });

        this.messageInput.addEventListener('blur', () => {
            document.querySelector('.input-cursor').style.display = 'inline';
        });
    }

    focusInput() {
        this.messageInput.focus();
    }

    getCurrentTimestamp() {
        const now = new Date();
        return `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}]`;
    }

    addMessage(message, type = 'system') {
        const messageElement = document.createElement('div');
        messageElement.className = `${type}-message`;

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = this.getCurrentTimestamp();

        const text = document.createElement('span');
        text.className = 'text';
        text.textContent = message;

        messageElement.appendChild(timestamp);
        messageElement.appendChild(text);

        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();

        // Add glitch effect occasionally
        if (Math.random() > 0.8) {
            messageElement.classList.add('glitch');
            setTimeout(() => messageElement.classList.remove('glitch'), 300);
        }
    }

    showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'typing-indicator';
        typingElement.id = 'typing-indicator';

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = this.getCurrentTimestamp();

        const text = document.createElement('span');
        text.textContent = 'N8N Bot is typing';

        const dots = document.createElement('span');
        dots.className = 'typing-dots';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.className = 'typing-dot';
            dots.appendChild(dot);
        }

        typingElement.appendChild(timestamp);
        typingElement.appendChild(text);
        typingElement.appendChild(dots);

        this.chatMessages.appendChild(typingElement);
        this.scrollToBottom();

        return typingElement;
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async sendMessage(message) {
        // Add user message
        this.addMessage(message, 'user');

        // Show typing indicator
        const typingIndicator = this.showTypingIndicator();

        try {
            // Update connection status
            this.connectionStatus.textContent = 'SENDING...';
            this.connectionStatus.style.color = '#ffff00';

            // Send to N8N webhook
            const response = await this.sendToN8N(message);

            // Remove typing indicator
            this.removeTypingIndicator();

            // Add bot response - handle N8N formats: {"text": "response"} or [{"text": "response"}]
            if (response && response.text) {
                // Single object format: {"text": "response"}
                this.addMessage(response.text, 'bot');
            } else if (response && Array.isArray(response) && response.length > 0 && response[0].text) {
                // Array format: [{"text": "response"}]
                this.addMessage(response[0].text, 'bot');
            } else if (response && response.message) {
                this.addMessage(response.message, 'bot');
            } else if (response && typeof response === 'string') {
                this.addMessage(response, 'bot');
            } else {
                this.addMessage('Response received from N8N chatbot.', 'bot');
            }

            // Update connection status
            this.connectionStatus.textContent = 'CONNECTED';
            this.connectionStatus.style.color = '#00ff00';

        } catch (error) {
            console.error('Error sending message to N8N:', error);

            // Remove typing indicator
            this.removeTypingIndicator();

            // Add error message
            this.addMessage('ERROR: Connection to N8N chatbot failed. Check webhook URL.', 'system');

            // Update connection status
            this.connectionStatus.textContent = 'ERROR';
            this.connectionStatus.style.color = '#ff0000';

            // Simulate a demo response for now
            setTimeout(() => {
                this.addMessage('Demo mode: I received your message "' + message + '". Please configure your N8N webhook URL.', 'bot');
                this.connectionStatus.textContent = 'DEMO MODE';
                this.connectionStatus.style.color = '#ffff00';
            }, 1000);
        }

        this.focusInput();
    }

    async sendToN8N(message) {
        // Check if webhook URL is configured
        if (this.n8nWebhookUrl === 'YOUR_N8N_WEBHOOK_URL_HERE') {
            throw new Error('N8N webhook URL not configured');
        }

        const response = await fetch(this.n8nWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                timestamp: new Date().toISOString(),
                user: 'terminal_user'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    // Method to update N8N webhook URL
    setWebhookUrl(url) {
        this.n8nWebhookUrl = url;
        this.addMessage(`Webhook URL updated: ${url}`, 'system');
        this.connectionStatus.textContent = 'CONNECTED';
        this.connectionStatus.style.color = '#00ff00';
    }
}

// Initialize the terminal when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const terminal = new MatrixTerminal();

    // Make terminal instance globally available for debugging
    window.matrixTerminal = terminal;

    // Add some demo commands
    document.addEventListener('keydown', (e) => {
        // Ctrl + / to show help
        if (e.ctrlKey && e.key === '/') {
            terminal.addMessage('Available commands:', 'system');
            terminal.addMessage('- Type any message to chat with the N8N bot', 'system');
            terminal.addMessage('- Use matrixTerminal.setWebhookUrl("your-url") to configure webhook', 'system');
            terminal.addMessage('- Ctrl+/ to show this help', 'system');
        }

        // Escape to clear and focus input
        if (e.key === 'Escape') {
            terminal.messageInput.value = '';
            terminal.focusInput();
        }
    });
});