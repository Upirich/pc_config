import React from 'react';

const PartCard = ({ part }) => {
  return (
    <div className="part-card">
      <h3>{part.name}</h3>
      <div className="part-details">
        <span className="part-category">{part.category}</span>
        <span className="part-price">${part.price.toFixed(2)}</span>
      </div>
      <div className="part-rating">
        Rating: {Array.from({ length: 5 }).map((_, i) => (
          <span key={i}>{i < Math.floor(part.rating) ? '★' : '☆'}</span>
        ))}
      </div>
      <button className="add-to-build">Add to Build</button>
    </div>
  );
};

export default PartCard;