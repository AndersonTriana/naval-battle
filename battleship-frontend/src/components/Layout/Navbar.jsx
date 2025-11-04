import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-white">
              🎮 Batalla Naval
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {!isAdmin && (
              <>
                <Link
                  to="/game"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Jugar
                </Link>

                <Link
                  to="/my-games"
                  className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Mis Juegos
                </Link>
              </>
            )}

            {isAdmin && (
              <Link
                to="/admin"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Admin Panel
              </Link>
            )}
            
            <div className="flex items-center gap-3">
              <span className="text-gray-400 text-sm">
                {user?.username}
                {isAdmin && <span className="ml-2 text-xs bg-indigo-600 px-2 py-1 rounded">Admin</span>}
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm"
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
