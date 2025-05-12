import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuthContext from '../context/AuthContext';
import '../styles/builds.css';

const BuildsPage = () => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBuilds = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/builds', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        const sortedBuilds = response.data.sort((a, b) => 
          a.name.localeCompare(b.name)
        );
        setBuilds(sortedBuilds);
      } catch (error) {
        console.error('Ошибка загрузки сборок:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBuilds();
  }, []);

  const handleDeleteBuild = async (buildId) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту сборку?')) return;

    try {
      await axios.delete(`http://localhost:8000/api/builds/${buildId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setBuilds(prev => prev.filter(build => build.id !== buildId));
    } catch (error) {
      console.error('Ошибка удаления:', error);
      alert('Не удалось удалить сборку');
    }
  };

  const renderComponent = (component, art) => {
    return component ? (
      <div className="component-item">
        <span className="component-name">{component}</span>
        <span className="component-art">Артикул: {art}</span>
      </div>
    ) : <div className="component-empty">Пусто</div>;
  };

  if (!user) {
    navigate('/auth');
    return null;
  }

  if (loading) {
    return <div className="loading">Загрузка сборок...</div>;
  }

  return (
    <div className="builds-container">
      <div className="builds-header">
        <h1>Мои сборки</h1>
        <div className="builds-actions">
          <button 
            className="create-build-btn"
            onClick={() => navigate('/builds/edit')}
          >
            + Создать сборку
          </button>
          <button 
            className="back-btn"
            onClick={() => navigate('/profile')}
          >
            ← Назад в профиль
          </button>
        </div>
      </div>

      <div className="builds-list">
        {builds.map((build) => (
          <div key={build.id} className="build-card">
            <div className="build-header">
              <h3>{build.name}</h3>
              <div className="build-actions">
                <button
                  className="delete-btn"
                  onClick={() => handleDeleteBuild(build.id)}
                  title="Удалить сборку"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="components-list">
              <div className="components-column">
                {renderComponent(build.cpu, build.artcpu)}
                {renderComponent(build.gpu, build.artgpu)}
                {renderComponent(build.motherboard, build.artmotherboard)}
                {renderComponent(build.ram, build.artram)}
              </div>
              <div className="components-column">
                {renderComponent(build.storage, build.artstorage)}
                {renderComponent(build.psu, build.artpsu)}
                {renderComponent(build.cpucool, build.artcpucool)}
                {renderComponent(build.case, build.artcase)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BuildsPage;