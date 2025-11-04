import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../hooks/useNotification';
import Notification from '../components/Layout/Notification';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { notification, showError, showSuccess, hideNotification } = useNotification();

  // Detectar si la ruta es /register
  useEffect(() => {
    setIsLogin(location.pathname === '/login');
  }, [location.pathname]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validaciones
    if (!username || !password) {
      showError('Por favor completa todos los campos');
      setLoading(false);
      return;
    }

    if (username.length < 3) {
      showError('El username debe tener al menos 3 caracteres');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      showError('La contraseña debe tener al menos 6 caracteres');
      setLoading(false);
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      showError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    try {
      let result;
      
      if (isLogin) {
        result = await login(username, password);
      } else {
        result = await register(username, password);
      }

      if (result.success) {
        showSuccess(isLogin ? '¡Bienvenido!' : '¡Registro exitoso!');
        setTimeout(() => {
          navigate('/game');
        }, 500);
      } else {
        showError(result.error);
      }
    } catch (error) {
      showError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setUsername('');
    setPassword('');
    setConfirmPassword('');
    navigate(isLogin ? '/register' : '/login');
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <Notification notification={notification} onClose={hideNotification} />

      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎮 Batalla Naval
          </h1>
          <p className="text-gray-400">
            {isLogin ? 'Inicia sesión para jugar' : 'Crea tu cuenta para comenzar'}
          </p>
        </div>

        {/* Card */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">
            {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Usuario
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-field w-full"
                placeholder="Ingresa tu usuario"
                disabled={loading}
                autoFocus
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field w-full"
                placeholder="Ingresa tu contraseña"
                disabled={loading}
              />
            </div>

            {/* Confirm Password (solo en registro) */}
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirmar Contraseña
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-field w-full"
                  placeholder="Confirma tu contraseña"
                  disabled={loading}
                />
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Procesando...
                </span>
              ) : (
                <span>{isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}</span>
              )}
            </button>
          </form>

          {/* Toggle Login/Register */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}
              <button
                onClick={toggleMode}
                className="ml-2 text-indigo-400 hover:text-indigo-300 font-medium"
                disabled={loading}
              >
                {isLogin ? 'Regístrate aquí' : 'Inicia sesión aquí'}
              </button>
            </p>
          </div>

          {/* Demo Credentials */}
          {isLogin && (
            <div className="mt-6 p-4 bg-gray-700 rounded border border-gray-600">
              <p className="text-xs text-gray-300 font-semibold mb-2">
                💡 Credenciales de prueba:
              </p>
              <div className="text-xs text-gray-400 space-y-1">
                <p><strong>Admin:</strong> admin / admin123</p>
                <p><strong>Player:</strong> Crea tu cuenta</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Batalla Naval v1.0</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
