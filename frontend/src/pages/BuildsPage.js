import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
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
        const response = await fetch('http://localhost:8000/builds', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) throw new Error('Ошибка загрузки сборок');
        
        let data = await response.json();
        data = data.sort((a, b) => a.name.localeCompare(b.name));
        setBuilds(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBuilds();
  }, []);

  if (!user) {
    navigate('/auth');
    return null;
  }

  const renderComponent = (component, art) => {
    return component ? (
      <div className="component-item">
        <span className="component-name">{component}</span>
        <span className="component-art">Артикул: {art}</span>
      </div>
    ) : <div className="component-empty">Пусто</div>;
  };

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

      {loading ? (
        <div className="loading">Загрузка сборок...</div>
      ) : (
        <div className="builds-list">
          {builds.map((build) => (
            <div key={build.id} className="build-card">
              <div className="build-header">
                <h3>{build.name}</h3>
                <button 
                  className="build-menu-btn"
                  onClick={() => console.log('Меню сборки...')}
                >
                  ⋮
                </button>
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
      )}
    </div>
  );
};

export default BuildsPage;