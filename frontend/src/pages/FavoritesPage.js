import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import '../styles/favorites.css';

const FavoritesPage = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const response = await fetch(`http://localhost:8000/components`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) throw new Error('Ошибка загрузки');
        
        let data = await response.json();
        data = data.sort((a, b) => a.part.localeCompare(b.part));
        setFavorites(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);

  if (!user) {
    navigate('/auth');
    return null;
  }

  if (loading) {
    return <div className="loading">Загрузка избранного...</div>;
  }

  return (
    <div className="favorites-container">
      <h1>Избранные комплектующие</h1>
      <button 
        onClick={() => navigate('/profile')}
        className="back-button"
      >
        ← Назад в профиль
      </button>
      
      <div className="parts-grid">
        {favorites.map((item) => (
          <div key={item.art} className="part-card">
            <h3>{item.part}</h3>
            <div className="part-details">
              <p>Тип: <span>{item.type}</span></p>
              <p>Цена: <span>{item.price} ₽</span></p>
              <p>Артикул: <span>{item.art}</span></p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FavoritesPage;