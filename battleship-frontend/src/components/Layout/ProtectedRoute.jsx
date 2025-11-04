import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Loading from './Loading';

const ProtectedRoute = ({ children, adminOnly = false, playerOnly = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <Loading />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Solo admins pueden acceder
  if (adminOnly && !isAdmin) {
    return <Navigate to="/game" replace />;
  }

  // Solo players pueden acceder (admins no)
  if (playerOnly && isAdmin) {
    return <Navigate to="/admin" replace />;
  }

  return children;
};

export default ProtectedRoute;
