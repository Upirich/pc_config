import React from 'react';
import { Link } from 'react-router-dom';

const ProfilePage = () => {
  return (
    <div className="page">
      <h1>Your Profile</h1>
      <div className="profile-content">
        <div className="profile-section">
          <h2>Your PC Builds</h2>
          <Link to="/" className="button">View Popular Builds</Link>
        </div>
        <div className="profile-section">
          <h2>Search Components</h2>
          <Link to="/search" className="button">Go to Search</Link>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;