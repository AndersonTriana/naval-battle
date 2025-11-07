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
      // No enviar filtro al backend, filtrar en frontend
      const data = await gameService.getMyGames();
      let filteredGames = data.games || [];
      
      // Filtrar en frontend según el filtro seleccionado
      if (filter === 'in_progress') {
        filteredGames = filteredGames.filter(g => 
          !['finished', 'player1_won', 'player2_won'].includes(g.status)
        );
      } else if (filter === 'finished') {
        filteredGames = filteredGames.filter(g => 
          ['finished', 'player1_won', 'player2_won'].includes(g.status)
        );
      }
      
      setGames(filteredGames);
    } catch (error) {
      console.error('Error al cargar juegos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueGame = async (gameId) => {
    // Navegar a la página del juego con el ID en la URL
    navigate(`/game/${gameId}`);
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
          <div className="text-6xl mb-4">🎮</div>
          <p className="text-gray-400 text-lg">No hay juegos en esta categoría</p>
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
  const isFinished = ['finished', 'player1_won', 'player2_won'].includes(game.status);
  const isWaitingForPlayer = game.status === 'waiting_for_player2';
  const isInProgress = !isFinished && !isWaitingForPlayer;
  const isMultiplayer = game.is_multiplayer || false;
  
  const statusColor = {
    setup: 'text-blue-400',
    placing_ships: 'text-blue-400',
    waiting_for_player2: 'text-yellow-400',
    both_players_setup: 'text-cyan-400',
    player1_setup: 'text-blue-400',
    player2_setup: 'text-purple-400',
    in_progress: 'text-green-400',
    player1_turn: 'text-green-400',
    player2_turn: 'text-green-400',
    finished: 'text-gray-400',
    player1_won: 'text-yellow-400',
    player2_won: 'text-yellow-400'
  }[game.status] || 'text-gray-400';

  const statusText = {
    setup: 'Colocando Barcos',
    placing_ships: 'Colocando Barcos',
    waiting_for_player2: '⏳ Esperando Jugador 2',
    both_players_setup: '🚢 Colocando Barcos',
    player1_setup: '🚢 Jugador 1 Setup',
    player2_setup: '🚢 Jugador 2 Setup',
    in_progress: 'En Progreso',
    player1_turn: '🎯 Turno J1',
    player2_turn: '🎯 Turno J2',
    finished: 'Finalizado',
    player1_won: '🏆 Ganó J1',
    player2_won: '🏆 Ganó J2'
  }[game.status] || game.status;

  return (
    <div className="bg-gray-800 rounded-lg p-4 flex justify-between items-center hover:bg-gray-750 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="text-white font-bold">
            Tablero {game.board_size}x{game.board_size}
          </h3>
          {isMultiplayer && (
            <span className="px-2 py-0.5 bg-purple-600 text-white text-xs font-bold rounded">
              👥 Multijugador
            </span>
          )}
        </div>
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
        {isWaitingForPlayer && (
          <button
            onClick={() => onContinue(game.id)}
            className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
          >
            ⏳ Ver Partida
          </button>
        )}
        {isInProgress && (
          <button
            onClick={() => onContinue(game.id)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
          >
            {game.status.includes('setup') ? '🚢 Colocar Barcos' : '⚔️ Continuar'}
          </button>
        )}
        {isFinished && (
          <button
            onClick={() => onContinue(game.id)}
            className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
          >
            👁️ Ver Resultado
          </button>
        )}
        <button
          onClick={() => onDelete(game.id)}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm"
        >
          🗑️ Eliminar
        </button>
      </div>
    </div>
  );
};

export default MyGamesPage;
