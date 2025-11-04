import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gameService } from '../services/gameService';
import { useGame } from '../hooks/useGame';
import Loading from '../components/Layout/Loading';

const MyGamesPage = () => {
  const navigate = useNavigate();
  const { loadGame } = useGame();
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all' | 'in_progress' | 'finished'

  useEffect(() => {
    loadGames();
  }, [filter]);

  const loadGames = async () => {
    setLoading(true);
    try {
      const statusParam = filter === 'all' ? null : filter;
      const data = await gameService.getMyGames(statusParam);
      setGames(data.games || []);
    } catch (error) {
      console.error('Error al cargar juegos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueGame = async (gameId) => {
    const result = await loadGame(gameId);
    if (result.success) {
      navigate('/game');
    }
  };

  const handleDeleteGame = async (gameId) => {
    if (window.confirm('¿Eliminar este juego?')) {
      try {
        await gameService.deleteGame(gameId);
        loadGames();
      } catch (error) {
        console.error('Error al eliminar:', error);
      }
    }
  };

  if (loading) {
    return <Loading message="Cargando juegos..." />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">
        📋 Mis Juegos
      </h1>

      {/* Filtros */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Todos
        </button>
        <button
          onClick={() => setFilter('in_progress')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'in_progress' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          En Progreso
        </button>
        <button
          onClick={() => setFilter('finished')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'finished' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Finalizados
        </button>
      </div>

      {/* Lista de juegos */}
      {games.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 rounded-lg">
          <p className="text-gray-400 text-lg mb-4">No hay juegos</p>
          <button
            onClick={() => navigate('/game')}
            className="btn-primary"
          >
            Comenzar Nuevo Juego
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {games.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              onContinue={handleContinueGame}
              onDelete={handleDeleteGame}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const GameCard = ({ game, onContinue, onDelete }) => {
  const isFinished = game.status === 'finished';
  const isInProgress = game.status === 'in_progress' || game.status === 'placing_ships';
  
  const statusColor = {
    placing_ships: 'text-blue-400',
    in_progress: 'text-yellow-400',
    finished: 'text-gray-400'
  }[game.status] || 'text-gray-400';

  const statusText = {
    placing_ships: 'Colocando Barcos',
    in_progress: 'En Progreso',
    finished: 'Finalizado'
  }[game.status] || game.status;

  return (
    <div className="bg-gray-800 rounded-lg p-4 flex justify-between items-center hover:bg-gray-750 transition-colors">
      <div className="flex-1">
        <h3 className="text-white font-bold mb-1">
          Tablero {game.board_size}x{game.board_size}
        </h3>
        <p className={`text-sm font-medium ${statusColor}`}>
          {statusText}
        </p>
        <div className="flex gap-4 mt-2 text-xs text-gray-400">
          <span>📊 {game.total_shots} disparos</span>
          <span>🎯 {game.hits} aciertos</span>
          <span>⚓ {game.ships_remaining}/{game.ships_total} barcos</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {new Date(game.created_at).toLocaleString()}
        </p>
      </div>

      <div className="flex gap-2">
        {isInProgress && (
          <button
            onClick={() => onContinue(game.id)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
          >
            Continuar
          </button>
        )}
        <button
          onClick={() => onDelete(game.id)}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
        >
          Eliminar
        </button>
      </div>
    </div>
  );
};

export default MyGamesPage;
