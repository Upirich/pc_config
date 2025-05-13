import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import SearchPage from './pages/SearchPage';
import ProfilePage from './pages/ProfilePage';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import FavoritesPage from './pages/FavoritesPage';
import BuildsPage from './pages/BuildsPage';
import EditBuildPage from './pages/EditBuildPage';
import AIPage from './pages/AIpage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Header />
        <Routes>
          <Route path="/ai-assistant" element={
            <ProtectedRoute>
              <AIPage />
            </ProtectedRoute>
          }/>
          <Route path="/builds/edit" element={
            <ProtectedRoute>
              <EditBuildPage />
            </ProtectedRoute>
          }/>
          <Route path="/builds" element={
            <ProtectedRoute>
              <BuildsPage />
            </ProtectedRoute>
          }/>
          <Route path="/favorites" element={
            <ProtectedRoute>
              <FavoritesPage />
            </ProtectedRoute>
          }/>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }/>
          <Route path="/favorites" element={<div>Избранное</div>} />
          <Route path="/builds" element={<div>Мои Сборки</div>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;