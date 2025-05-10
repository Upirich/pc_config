import { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const { data } = await axios.get('http://localhost:8000/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(data);
    } catch (err) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const register = async (formData) => {
    const { data } = await axios.post('http://localhost:8000/register', formData);
    localStorage.setItem('token', data.access_token);
    checkAuth();
  };

  const login = async (formData) => {
    const { data } = await axios.post('http://localhost:8000/login', formData);
    localStorage.setItem('token', data.access_token);
    await checkAuth();
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;