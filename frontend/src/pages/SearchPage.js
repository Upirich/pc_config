import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PartCard from '../components/PartCard';
import FilterPanel from '../components/FilterPanel';
import SearchBar from '../components/SearchBar';

const SearchPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [allResults, setAllResults] = useState([]); // Все результаты
  const [filteredResults, setFilteredResults] = useState([]); // Отфильтрованные результаты
  const [filters, setFilters] = useState({
    category: '',
    priceMin: '',
    priceMax: '',
    sortBy: 'name'
  });

  // Функция для выполнения поиска
  const performSearch = (query) => {
    setSearchQuery(query);
    fetchResults(query);
  };

  // При первом открытии страницы
  useEffect(() => {
    if (location.state?.searchQuery) {
      performSearch(location.state.searchQuery);
    }
  }, [location]);

  // При изменении фильтров или результатов
  useEffect(() => {
    applyFilters();
  }, [filters, allResults]);

  // Моковая функция поиска
  const fetchResults = async (query) => {
    const mockParts = [
      { id: 1, name: 'Intel Core i9-13900K', category: 'CPU', price: 589.99, rating: 4.8 },
      { id: 2, name: 'AMD Ryzen 9 7950X', category: 'CPU', price: 699.99, rating: 4.9 },
      { id: 3, name: 'NVIDIA RTX 4090', category: 'GPU', price: 1599.99, rating: 4.7 },
      { id: 4, name: 'AMD RX 7900 XTX', category: 'GPU', price: 999.99, rating: 4.6 },
      { id: 5, name: 'Corsair Vengeance 32GB DDR5', category: 'RAM', price: 129.99, rating: 4.5 },
      { id: 6, name: 'Samsung 980 Pro 1TB', category: 'Storage', price: 99.99, rating: 4.8 },
    ];
    
    const filtered = mockParts.filter(part => 
      part.name.toLowerCase().includes(query.toLowerCase()) ||
      part.category.toLowerCase().includes(query.toLowerCase())
    );
    
    setAllResults(filtered);
  };

  // Применение фильтров
  const applyFilters = () => {
    let results = [...allResults];
    
    // Фильтрация по категории
    if (filters.category) {
      results = results.filter(part => part.category === filters.category);
    }
    
    // Фильтрация по цене
    if (filters.priceMin) {
      results = results.filter(part => part.price >= Number(filters.priceMin));
    }
    
    if (filters.priceMax) {
      results = results.filter(part => part.price <= Number(filters.priceMax));
    }
    
    // Сортировка
    results = sortResults(results, filters.sortBy);
    
    setFilteredResults(results);
  };

  // Функция сортировки
  const sortResults = (results, sortBy) => {
    switch (sortBy) {
      case 'price-asc':
        return [...results].sort((a, b) => a.price - b.price);
      case 'price-desc':
        return [...results].sort((a, b) => b.price - a.price);
      case 'rating':
        return [...results].sort((a, b) => b.rating - a.rating);
      default: // name
        return [...results].sort((a, b) => a.name.localeCompare(b.name));
    }
  };

  return (
    <div className="page">
      <h1>Search Results {searchQuery && `for "${searchQuery}"`}</h1>
      
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
          filteredResults.map(part => <PartCard key={part.id} part={part} />)
        ) : (
          <p className="no-results">
            {allResults.length === 0 
              ? "No parts found. Try another search." 
              : "No parts match your filters. Try adjusting them."}
          </p>
        )}
      </div>
    </div>
  );
};

export default SearchPage;