import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/ai.css';

const AIChat = () => {
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);
  const messagesEndRef = useRef(null);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setShowHistoryPanel(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isAuthenticated && isOpen) {
      fetchHistory();
    }
  }, [isAuthenticated, isOpen]);

  const formatHistoryItem = (historyItem) => ({
    messages: [
      { sender: 'user', text: historyItem.request_text },
      { sender: 'ai', text: historyItem.response_text }
    ],
    timestamp: historyItem.created_at
  });

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const { data } = await axios.get('http://localhost:8000/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(data.map(formatHistoryItem));
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const loadHistoryItem = (historyItem) => {
    setMessages(historyItem.messages);
    setShowHistoryPanel(false);
    scrollToBottom();
  };

  const handleSendMessage = async (endpoint) => {
    if (!input.trim()) return;

    const token = localStorage.getItem('token');
    const userMessage = { text: input, sender: 'user' };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const { data } = await axios.post(
        `http://localhost:8000/ai/${endpoint}`,
        { prompt: input },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const aiMessage = { text: data.response, sender: 'ai' };
      setMessages([...newMessages, aiMessage]);
      await fetchHistory();
    } catch (error) {
      setMessages([...newMessages, { 
        text: `Error: ${error.response?.data?.message || error.message}`, 
        sender: 'ai',
        isError: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="ai-chat-container">
        <div className="auth-message">
          Пользоваться ИИ-ассистентом возможно только после авторизации на сайте
          <br />
          <a href="/auth">Войти или Зарегистрироваться</a>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-chat-container">
      <button className="ai-chat-toggle" onClick={toggleChat}>
        AI
      </button>
      
      <div className={`ai-chat-window ${isOpen ? 'active' : ''}`}>
        {showHistoryPanel ? (
          <div className="history-panel">
            <div className="history-header">
              <h3>История запросов</h3>
              <button 
                className="close-history-btn"
                onClick={() => setShowHistoryPanel(false)}
              >
                ×
              </button>
            </div>
            
            <div className="history-grid">
              {history.length === 0 ? (
                <div className="empty-history">История запросов пуста</div>
              ) : (
                history.map((item, index) => (
                  <div 
                    key={index} 
                    className="history-card"
                    onClick={() => loadHistoryItem(item)}
                  >
                    <div className="history-preview">
                      {item.messages[0]?.text.slice(0, 100)}...
                    </div>
                    <div className="history-date">
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ) : (
          <>
            <div className="ai-chat-header">
              <div className="ai-chat-title">ИИ-ассистент</div>
              <div className="ai-chat-tools">
                <button 
                  className="tool-button" 
                  onClick={() => setShowHistoryPanel(true)}
                  title="История запросов"
                >
                  🕒
                </button>
                <button className="ai-chat-close" onClick={toggleChat}>
                  ×
                </button>
              </div>
            </div>
            
            <div className="ai-chat-messages">
              {messages.length === 0 && !isLoading && (
                <div className="message ai-message">
                  Задайте вопрос ИИ-ассистенту
                </div>
              )}
              
              {messages.map((message, index) => (
                <div 
                  key={index} 
                  className={`message ${message.sender}-message ${message.isError ? 'error' : ''}`}
                >
                  {message.text}
                </div>
              ))}
              
              {isLoading && (
                <div className="message ai-message">
                  ИИ думает...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="ai-chat-input-area">
              <textarea
                className="ai-chat-textarea"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Введите ваш запрос..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage('');
                  }
                }}
              />
              
              <div className="ai-chat-buttons">
                <button 
                  className="ai-chat-button secondary"
                  onClick={() => handleSendMessage('_cot')}
                  disabled={isLoading || !input.trim()}
                >
                  Chain-of-thought
                </button>
                <button 
                  className="ai-chat-button primary"
                  onClick={() => handleSendMessage('')}
                  disabled={isLoading || !input.trim()}
                >
                  Отправить
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AIChat;