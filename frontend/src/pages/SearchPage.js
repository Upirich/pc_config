import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PartCard from '../components/PartCard';
import FilterPanel from '../components/FilterPanel';
import SearchBar from '../components/SearchBar';

const SearchPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [allResults, setAllResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    priceMin: '',
    priceMax: '',
    sortBy: 'name'
  });

  const performSearch = (query) => {
    setSearchQuery(query);
    fetchResults(query);
  };

  useEffect(() => {
    if (location.state?.searchQuery) {
      performSearch(location.state.searchQuery);
    }
  }, [location]);

  useEffect(() => {
    applyFilters();
  }, [filters, allResults]);

  const fetchResults = async (query) => {
    try {
      const response = await fetch(
        `http://localhost:8000/search_components?query=${encodeURIComponent(query)}`
      );
      
      if (!response.ok) {
        throw new Error('Ошибка при загрузке данных');
      }
      
      const data = await response.json();
      
      // Преобразование данных бэкенда под структуру фронтенда
      const transformedData = data.map(item => ({
        id: item.id,
        name: item.name.toString(),
        category: item.type,
        price: parseFloat(item.price),
        description: item.description
      }));
      
      setAllResults(transformedData);
    } catch (error) {
      console.error('Ошибка:', error);
      setAllResults([]);
    }
  };

  const applyFilters = () => {
    let results = [...allResults];

    if (filters.category) {
      results = results.filter(part => part.category === filters.category);
    }

    if (filters.priceMin) {
      results = results.filter(part => part.price >= Number(filters.priceMin));
    }
    
    if (filters.priceMax) {
      results = results.filter(part => part.price <= Number(filters.priceMax));
    }

    results = sortResults(results, filters.sortBy);
    
    setFilteredResults(results);
  };

  const sortResults = (results, sortBy) => {
    switch (sortBy) {
      case 'price-asc':
        return [...results].sort((a, b) => a.price - b.price);
      case 'price-desc':
        return [...results].sort((a, b) => b.price - a.price);
      default:
        return [...results].sort((a, b) => a.name.localeCompare(b.name));
    }
  };

  return (
    <div className="page">
      <h1>Результаты поиска {searchQuery && `для "${searchQuery}"`}</h1>
      
      <div className="search-page-bar">
        <SearchBar 
          initialQuery={searchQuery}
          onSearch={(query) => {
            performSearch(query);
            navigate('/search', { state: { searchQuery: query }, replace: true });
          }} 
        />
      </div>
      
      <FilterPanel 
        filters={filters}
        onFilterChange={setFilters}
        availableCategories={[...new Set(allResults.map(part => part.category))]}
      />
      
      <div className="parts-grid">
        {filteredResults.length > 0 ? (
          filteredResults.map(part => (
            <PartCard 
              key={part.id} 
              part={{
                ...part,
                // Добавляем совместимость с прежней структурой данных
                price: part.price
              }}
            />
          ))
        ) : (
          <p className="no-results">
            {allResults.length === 0 
              ? "Компоненты не найдены" 
              : "Нет компонентов, соответствующих фильтрам"}
          </p>
        )}
      </div>
    </div>
  );
};

export default SearchPage;