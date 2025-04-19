import React from 'react';

const BuildCard = ({ build }) => {
  return (
    <div className="build-card">
      <h3>{build.name}</h3>
      <p className="build-description">{build.description}</p>
      <div className="build-details">
        <span className="build-price">${build.totalPrice.toFixed(2)}</span>
        <span className="build-rating">★ {build.rating}</span>
      </div>
      <div className="build-parts">
        <h4>Parts:</h4>
        <ul>
          {build.parts.map((part, index) => (
            <li key={index}>
              {part.name} - ${part.price.toFixed(2)}
            </li>
          ))}
        </ul>
      </div>
      <button className="edit-button">Edit Build</button>
    </div>
  );
};

export default BuildCard;