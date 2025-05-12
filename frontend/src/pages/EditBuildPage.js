import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import AuthContext from '../context/AuthContext';
import '../styles/edit-build.css';

const componentTypes = {
  cpu: 'Процессор',
  gpu: 'Видеокарта',
  motherboard: 'Материнская плата',
  ram: 'Оперативная память',
  storage: 'Накопитель',
  psu: 'Блок питания',
  cpucool: 'Кулер',
  case: 'Корпус'
};

const EditBuildPage = () => {
  const [buildName, setBuildName] = useState('');
  const [selectedComponents, setSelectedComponents] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [activeComponent, setActiveComponent] = useState(null);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.build) {
      setBuildName(location.state.build.name);
      setSelectedComponents(location.state.build.components);
    }
  }, [location]);

  const handleSearch = async (componentType) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/parts/search`, {
        params: { type: componentType, q: searchQuery },
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const selectComponent = (component) => {
    setSelectedComponents(prev => ({
      ...prev,
      [activeComponent]: {
        name: component.part,
        price: component.price,
        art: component.art
      }
    }));
    setActiveComponent(null);
    setSearchQuery('');
  };

  const calculateTotal = () => {
    return Object.values(selectedComponents).reduce((sum, comp) => sum + (comp?.price || 0), 0);
  };

  const saveBuild = async () => {
    if (!buildName.trim()) {
      alert('Введите название сборки');
      return;
    }

    try {
      await axios.post('http://localhost:8000/api/builds', {
        name: buildName,
        components: selectedComponents
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } // Исправлено здесь
      });
      
      navigate('/builds');
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  if (!user) {
    navigate('/auth');
    return null;
  }

  return (
    <div className="edit-build-container">
      <div className="build-header">
        <input
          type="text"
          placeholder="Название сборки"
          value={buildName}
          onChange={(e) => setBuildName(e.target.value)}
          className="build-name-input"
        />
        <div className="total-price">
          Итоговая стоимость: {calculateTotal().toLocaleString()} ₽
        </div>
      </div>

      <div className="components-grid">
        {Object.entries(componentTypes).map(([key, label]) => (
          <div 
            key={key}
            className={`component-card ${activeComponent === key ? 'active' : ''}`}
          >
            <div className="component-header" onClick={() => setActiveComponent(key)}>
              <h4>{label}</h4>
              <div className="selected-component">
                {selectedComponents[key]?.name || 'Не выбрано'}
              </div>
            </div>

            {activeComponent === key && (
              <div className="search-section">
                <div className="search-bar">
                  <input
                    type="text"
                    placeholder={`Поиск ${label.toLowerCase()}...`}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch(key)}
                  />
                  <button onClick={() => handleSearch(key)}>Найти</button>
                </div>

                <div className="search-results">
                  {searchResults.map((item) => (
                    <div 
                      key={item.art} 
                      className="result-item"
                      onClick={() => selectComponent(item)}
                    >
                      <div className="part-name">{item.part}</div>
                      <div className="part-price">{item.price.toLocaleString()} ₽</div>
                      <div className="part-art">Артикул: {item.art}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="actions">
        <button onClick={saveBuild} className="save-btn">
          Сохранить сборку
        </button>
        <button onClick={() => navigate('/builds')} className="cancel-btn">
          Отмена
        </button>
      </div>
    </div>
  );
};

export default EditBuildPage;