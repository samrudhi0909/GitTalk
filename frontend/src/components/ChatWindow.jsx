import React, { useState } from 'react';
import axios from 'axios';

function ChatWindow({ repoLoaded }) {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/chat', {
        message: message,
      });
      if (response.status === 200) {
        setChatHistory([
          ...chatHistory,
          { question: message, answer: response.data.reply },
        ]);
        setMessage('');
      } else {
        alert('Failed to get a response.');
      }
    } catch (error) {
      alert('Error getting response from server.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Chat with Repository</h2>
      {!repoLoaded ? (
        <p>Please load a repository first.</p>
      ) : (
        <>
          <div className="chat-window">
            {chatHistory.map((chat, index) => (
              <div key={index} className={`chat-message ${chat.question ? 'user' : 'assistant'}`}>
                <p>
                  <strong>You:</strong> {chat.question}
                </p>
                <p>
                  <strong>Assistant:</strong> {chat.answer}
                </p>
              </div>
            ))}
          </div>
          <div className="chat-input">
            <img src="/path/to/chat-icon.svg" alt="Chat Icon" className="chat-icon" />
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask a question about the code..."
            />
            <button onClick={handleSendMessage} disabled={loading || !message}>
              <img src="/path/to/send-icon.svg" alt="Send Icon" className="send-icon" />
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default ChatWindow;