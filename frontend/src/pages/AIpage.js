import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuthContext from '../context/AuthContext';
import '../styles/ai.css';

const AIAssistantPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/history', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        // Преобразуем данные из бэкенда в нужный формат
        const formattedMessages = response.data.map(msg => ({
          id: msg._id,
          query: msg.request_text,
          response: msg.response_text,
          timestamp: msg.created_at
        }));
        setMessages(formattedMessages);
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);
      }
    };

    if (user) loadHistory();
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    setIsLoading(true);
    const tempId = Date.now(); // Временный ID для оптимистичного обновления

    try {
      // Оптимистичное обновление UI
      setMessages(prev => [...prev, {
        id: tempId,
        query: inputValue,
        response: null,
        timestamp: new Date().toISOString()
      }]);
      setInputValue('');

      // Отправка запроса к бэкенду
      const response = await axios.post('http://localhost:8000/ai', 
        { query: inputValue },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      // Обновляем сообщение с данными из бэкенда
      setMessages(prev => 
        prev.map(msg => 
          msg.id === tempId 
            ? { ...response.data, id: response.data._id } 
            : msg
        )
      );
    } catch (error) {
      console.error('Ошибка запроса к ИИ:', error);
      // Откатываем оптимистичное обновление
      setMessages(prev => prev.filter(msg => msg.id !== tempId));
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
              <div className="query-preview">
                {message?.query
                  ? `${message.query.substring(0, 30)}${message.query.length > 30 ? '...' : ''}`
                  : "Без текста..."}
              </div>
              <div className="message-date">
                {message?.timestamp 
                    ? new Date(message.timestamp).toLocaleDateString()
                    : 'Дата неизвестна'}
              </div>
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
              <div className="message-time">
                {new Date(selectedMessage.timestamp).toLocaleString()}
              </div>
            </div>
            <div className="ai-response">
              <h4>Ответ ИИ:</h4>
              {selectedMessage.response ? (
                <div className="response-content">
                  <p>{selectedMessage.response}</p>
                </div>
              ) : (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Обработка запроса...</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="welcome-message">
            <h2>ИИ ассистент PCconfig</h2>
            <p>Задайте вопрос о сборке ПК, комплектующих или настройках</p>
            <div className="example-questions">
              <p>Примеры запросов:</p>
              <ul>
                <li>"Подбери игровой ПК до 1000$"</li>
                <li>"Сравнение RTX 4060 и RX 7600"</li>
                <li>"Как настроить разгон RAM?"</li>
              </ul>
            </div>
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
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Отправка...
              </>
            ) : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AIAssistantPage;