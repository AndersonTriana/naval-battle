import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/Layout/ProtectedRoute';
import Layout from './components/Layout/Layout';
import LoginPage from './pages/LoginPage';
import GamePage from './pages/GamePage';
import MyGamesPage from './pages/MyGamesPage';
import AdminPage from './pages/AdminPage';
import TestGamePage from './pages/TestGamePage';

// Componente para redirigir según el rol
const HomeRedirect = () => {
  const { isAdmin } = useAuth();
  return <Navigate to={isAdmin ? '/admin' : '/game'} replace />;
};

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<LoginPage />} />

        {/* Rutas protegidas */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <HomeRedirect />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/game"
          element={
            <ProtectedRoute playerOnly>
              <Layout>
                <GamePage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/game/:gameId"
          element={
            <ProtectedRoute playerOnly>
              <Layout>
                <GamePage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/my-games"
          element={
            <ProtectedRoute playerOnly>
              <Layout>
                <MyGamesPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/test-game"
          element={
            <ProtectedRoute>
              <Layout>
                <TestGamePage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <Layout>
                <AdminPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App
