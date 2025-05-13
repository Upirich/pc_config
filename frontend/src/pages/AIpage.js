import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuthContext from '../context/AuthContext';
import '../styles/ai.css';

const AIPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    // Загрузка истории сообщений при монтировании
    const loadHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/ai/history', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setMessages(response.data);
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);
      }
    };

    loadHistory();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    setIsLoading(true);
    const newMessage = {
      prompt: inputValue,
      response: null,
      timestamp: new Date().toISOString()
    };

    try {
      // Оптимистичное обновление UI
      setMessages(prev => [...prev, newMessage]);
      setInputValue('');

      const response = await axios.post('http://localhost:8000/ai', {
        prompt: inputValue
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      console.log(response.data)

      // Обновляем сообщение с ответом
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? { ...msg, response: response.data.answer } 
          : msg
      ));
    } catch (error) {
      console.error('Ошибка запроса к ИИ:', error);
      setMessages(prev => prev.filter(msg => msg.id !== newMessage.id));
      alert('Ошибка при обработке запроса');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    navigate('/auth');
    return null;
  }

  return (
    <div className="ai-assistant-container">
      <div className="sidebar">
        <h3>История запросов</h3>
        <div className="message-history">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`history-item ${selectedMessage?.id === message.id ? 'active' : ''}`}
              onClick={() => setSelectedMessage(message)}
            >
              {message.prompt.substring(0, 30)}...
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        {selectedMessage ? (
          <div className="message-detail">
            <div className="user-query">
              <h4>Ваш запрос:</h4>
              <p>{selectedMessage.query}</p>
            </div>
            <div className="ai-response">
              <h4>Ответ ИИ:</h4>
              {selectedMessage.response ? (
                <p>{selectedMessage.response}</p>
              ) : (
                <p className="loading-text">Запрос обрабатывается...</p>
              )}
            </div>
          </div>
        ) : (
          <div className="welcome-message">
            <h2>ИИ ассистент PCconfig</h2>
            <p>Задайте вопрос о сборке ПК, комплектующих или настройках</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Введите ваш запрос..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AIPage;