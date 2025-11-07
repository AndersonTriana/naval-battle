import { useState, useEffect } from 'react';
import { gameService } from '../../services/gameService';

const AvailableGamesList = ({ onJoinGame, onShowManualJoin }) => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAvailableGames();
    // Recargar cada 10 segundos
    const interval = setInterval(loadAvailableGames, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAvailableGames = async () => {
    try {
      setError(null);
      const data = await gameService.getAvailableGames(8);
      setGames(data.games || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar partidas');
    } finally {
      setLoading(false);
    }
  };

  const getTimeAgo = (isoDate) => {
    const now = new Date();
    const created = new Date(isoDate);
    const diffMs = now - created;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Hace menos de 1 min';
    if (diffMins === 1) return 'Hace 1 minuto';
    if (diffMins < 60) return `Hace ${diffMins} minutos`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return 'Hace 1 hora';
    return `Hace ${diffHours} horas`;
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400">Buscando partidas disponibles...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold text-white">
            🎮 Partidas Disponibles
          </h3>
          <p className="text-gray-400 text-sm mt-1">
            {games.length > 0 
              ? `${games.length} partida${games.length !== 1 ? 's' : ''} esperando jugador`
              : 'No hay partidas disponibles'}
          </p>
        </div>
        
        <button
          onClick={onShowManualJoin}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm"
        >
          📝 Unirse por ID
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <p className="text-red-400 text-sm">⚠️ {error}</p>
        </div>
      )}

      {/* Lista de partidas */}
      {games.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h4 className="text-xl font-bold text-white mb-2">
            No hay partidas disponibles
          </h4>
          <p className="text-gray-400">
            Sé el primero en crear una partida multijugador o únete usando un ID
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {games.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              onJoin={() => onJoinGame(game.id)}
              timeAgo={getTimeAgo(game.created_at)}
            />
          ))}
        </div>
      )}

      {/* Botón de refrescar */}
      <div className="text-center">
        <button
          onClick={loadAvailableGames}
          disabled={loading}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-gray-300 rounded-lg transition-colors text-sm"
        >
          🔄 Actualizar lista
        </button>
      </div>
    </div>
  );
};

const GameCard = ({ game, onJoin, timeAgo }) => {
  return (
    <div className="bg-gray-800 hover:bg-gray-750 rounded-lg p-4 flex items-center justify-between transition-all border border-gray-700 hover:border-purple-500">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg flex items-center justify-center text-2xl">
            🎯
          </div>
          <div>
            <h4 className="text-white font-bold">
              {game.base_fleet_name}
            </h4>
            <p className="text-sm text-gray-400">
              Tablero {game.board_size}x{game.board_size} • {game.ship_count} barcos
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-xs text-gray-400 ml-15">
          <span className="flex items-center gap-1">
            👤 Jugador: {game.player1_username || game.player1_id.substring(0, 8) + '...'}
          </span>
          <span className="flex items-center gap-1">
            ⏰ {timeAgo}
          </span>
        </div>
      </div>

      <button
        onClick={onJoin}
        className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-colors ml-4"
      >
        Unirse →
      </button>
    </div>
  );
};

export default AvailableGamesList;
