import React, { useState } from 'react';

const SearchBar = ({ initialQuery = '', onSearch }) => {
  const [query, setQuery] = useState(initialQuery);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch?.(query.trim());
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search processors, graphics cards, etc..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      <button type="submit" className="search-button">
        <i className="search-icon">🔍</i> Поиск
      </button>
    </form>
  );
};

export default SearchBar;