import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useGame } from '../hooks/useGame';
import FleetSelector from '../components/Game/FleetSelector';
import ShipPlacementDragDrop from '../components/Game/ShipPlacementDragDrop';
import Board from '../components/Game/Board';
import GameStats from '../components/Game/GameStats';
import GameControls from '../components/Game/GameControls';
import ShotResult from '../components/Game/ShotResult';
import Loading from '../components/Layout/Loading';
import { useNotification } from '../hooks/useNotification';
import Notification from '../components/Layout/Notification';
import GameModeSelector from '../components/Game/GameModeSelector';
import JoinGameModal from '../components/Game/JoinGameModal';
import MultiplayerInfo from '../components/Game/MultiplayerInfo';
import { gameService } from '../services/gameService';

const GamePage = () => {
  const { gameId } = useParams();
  const {
    game,
    board,
    stats,
    loading,
    error,
    createGame,
    joinGame,
    placeShip,
    shoot,
    refreshBoard,
    refreshStats,
    loadShotsHistory,
    loadGame,
    resetGame
  } = useGame();

  const { notification, showError, showSuccess, showInfo, hideNotification } = useNotification();
  const [gamePhase, setGamePhase] = useState('mode'); // 'mode' | 'select' | 'join' | 'placement' | 'playing' | 'finished'
  const [placedShips, setPlacedShips] = useState([]);
  const [lastShot, setLastShot] = useState(null);
  const [lastAiShot, setLastAiShot] = useState(null);
  const [isMultiplayer, setIsMultiplayer] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [previousTurnPlayerId, setPreviousTurnPlayerId] = useState(null);

  // Cargar juego existente si hay gameId en la URL
  useEffect(() => {
    if (gameId) {
      const loadExistingGame = async () => {
        const result = await loadGame(gameId);
        if (result.success) {
          // El juego se cargó correctamente
          // El useEffect de abajo manejará la fase
        } else {
          showError('No se pudo cargar la partida');
        }
      };
      loadExistingGame();
    }
  }, [gameId, loadGame, showError]);

  // Verificar fase del juego cuando cambia el estado
  useEffect(() => {
    if (game) {
      // Detectar si es multijugador
      if (game.is_multiplayer !== undefined) {
        setIsMultiplayer(game.is_multiplayer);
      }

      // Mapear estados del backend a fases del frontend
      const statusToPhase = {
        'setup': 'placement',
        'placing_ships': 'placement',
        'waiting_for_player2': 'placement',
        'both_players_setup': 'placement',
        'player1_setup': 'placement',
        'player2_setup': 'placement',
        'in_progress': 'playing',
        'player1_turn': 'playing',
        'player2_turn': 'playing',
        'finished': 'finished',
        'player1_won': 'finished',
        'player2_won': 'finished'
      };

      const newPhase = statusToPhase[game.status];
      if (newPhase && newPhase !== gamePhase) {
        // Si cambia de placement a playing, notificar
        if (gamePhase === 'placement' && newPhase === 'playing' && isMultiplayer) {
          showSuccess('¡Ambos jugadores listos! Comienza la batalla ⚔️');
        }
        setGamePhase(newPhase);
      }
      
      // Detectar cambios de turno en multijugador
      if (isMultiplayer && gamePhase === 'playing' && game.current_turn_player_id) {
        if (previousTurnPlayerId && previousTurnPlayerId !== game.current_turn_player_id) {
          // El turno cambió
          const user = JSON.parse(localStorage.getItem('user') || '{}');
          const isMyTurn = game.current_turn_player_id === user.id;
          
          if (isMyTurn) {
            showSuccess('¡Es tu turno! 🎯');
          } else {
            showInfo('Turno del oponente ⏳');
          }
        }
        setPreviousTurnPlayerId(game.current_turn_player_id);
      }
    }
    // También verificar si hay un ganador en board
    if (board && board.winner) {
      setGamePhase('finished');
    }
  }, [game, board, gamePhase, isMultiplayer, showSuccess, showInfo, previousTurnPlayerId]);

  // Cargar datos cuando el juego está activo
  useEffect(() => {
    if (gamePhase === 'playing') {
      refreshBoard();
      refreshStats();
      loadShotsHistory();
    }
  }, [gamePhase]);

  // Polling en multijugador para sincronización en tiempo real
  useEffect(() => {
    if (isMultiplayer && game?.id && (gamePhase === 'placement' || gamePhase === 'playing')) {
      // Durante colocación: detectar cuando el otro jugador termina
      // Durante juego: detectar disparos del oponente y cambios de turno
      const pollInterval = gamePhase === 'placement' ? 3000 : 2000; // Más frecuente durante el juego
      
      const interval = setInterval(async () => {
        await refreshBoard();
        if (gamePhase === 'playing') {
          await refreshStats();
        }
      }, pollInterval);

      return () => clearInterval(interval);
    }
  }, [gamePhase, isMultiplayer, game?.id, refreshBoard, refreshStats]);

  // Mostrar errores
  useEffect(() => {
    if (error) {
      showError(error);
    }
  }, [error]);

  // Handler: Seleccionar modo de juego
  const handleModeSelected = (multiplayer) => {
    setIsMultiplayer(multiplayer);
    if (multiplayer) {
      // Mostrar opciones: crear o unirse
      setGamePhase('select');
    } else {
      // Modo vs IA: ir directo a selección de flota
      setGamePhase('select');
    }
  };

  // Handler: Seleccionar flota
  const handleFleetSelected = async (fleet) => {
    const result = await createGame(fleet.id, isMultiplayer);
    if (result.success) {
      setPlacedShips([]);
      setGamePhase('placement');
      if (isMultiplayer) {
        showSuccess('¡Partida multijugador creada! Comparte el ID con tu oponente');
      } else {
        showSuccess('¡Flota seleccionada! Coloca tus barcos');
      }
    }
  };

  // Handler: Unirse a partida
  const handleJoinGame = async (gameId) => {
    const result = await joinGame(gameId);
    
    if (result.success) {
      showSuccess(result.data?.message || '¡Te has unido a la partida!');
      setShowJoinModal(false);
      setIsMultiplayer(true);
      setPlacedShips([]);
      setGamePhase('placement');
    } else {
      showError(result.error || 'Error al unirse a la partida');
    }
  };

  // Handler: Colocar barco
  const handlePlaceShip = async (shipTemplateId, startCoordinate, orientation, shipIndex) => {
    const result = await placeShip(shipTemplateId, startCoordinate, orientation);
    
    if (result.success) {
      // El backend devuelve: { ship: { name, coordinates }, ships_remaining_to_place }
      const newShip = {
        ship_template_id: shipTemplateId,
        ship_index: shipIndex,  // Guardar el index para distinguir barcos del mismo tipo
        coordinates: result.data?.ship?.coordinates || [],
        name: result.data?.ship?.name || 'Barco'
      };
      
      setPlacedShips(prev => [...prev, newShip]);
      
      showSuccess(`${newShip.name} colocado correctamente`);

      // Verificar si todos los barcos fueron colocados
      if (result.data?.ships_remaining_to_place === 0) {
        showSuccess('¡Todos los barcos colocados! Inicializando juego...');
        
        // Recargar el tablero para obtener los barcos de la IA
        await refreshBoard();
        await refreshStats();
        
        // Pequeña pausa para asegurar que los datos se cargaron
        setTimeout(() => {
          setGamePhase('playing');
          showSuccess('¡Comienza el juego! Es tu turno');
        }, 500);
      }
    } else {
      showError(result.error || 'Error al colocar barco');
    }
  };

  // Handler: Realizar disparo
  const handleShoot = async (coordinate) => {
    const result = await shoot(coordinate);
    
    if (result.success) {
      // Mostrar resultado del disparo
      setLastShot(result.data);
      
      // Guardar último disparo de la IA
      if (result.data.ai_shot) {
        setLastAiShot(result.data.ai_shot.coordinate);
        // Limpiar después de 3 segundos
        setTimeout(() => setLastAiShot(null), 3000);
      }
      
      // Verificar si el juego terminó
      if (result.data.game_won) {
        setGamePhase('finished');
      }
    }
  };

  // Handler: Nuevo juego
  const handleNewGame = () => {
    resetGame();
    setPlacedShips([]);
    setLastShot(null);
    setIsMultiplayer(false);
    setGamePhase('mode');
  };

  // Renderizar según fase
  if (loading && !game) {
    return <Loading message="Cargando juego..." />;
  }

  return (
    <>
      <Notification notification={notification} onClose={hideNotification} />
      
      <div className="space-y-6">
        {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            ⚓ Batalla Naval
          </h1>
          {game && (
            <p className="text-gray-400">
              Juego ID: {game.id} • Estado: {game.status}
            </p>
          )}
        </div>
        
        {game && (
          <button
            onClick={handleNewGame}
            className="btn-secondary"
          >
            🔄 Nuevo Juego
          </button>
        )}
      </div>

      {/* FASE 0: Selección de Modo */}
      {gamePhase === 'mode' && (
        <div className="space-y-6">
          <GameModeSelector onModeSelected={handleModeSelected} />
        </div>
      )}

      {/* FASE 1: Selección de Flota o Unirse */}
      {gamePhase === 'select' && (
        <div className="space-y-6">
          {isMultiplayer && (
            <div className="flex justify-center mb-6">
              <button
                onClick={() => setShowJoinModal(true)}
                className="btn-primary"
              >
                🔍 O Unirse a una Partida Existente
              </button>
            </div>
          )}
          <FleetSelector onFleetSelected={handleFleetSelected} />
        </div>
      )}

      {/* FASE 2: Colocación de Barcos */}
      {gamePhase === 'placement' && game && (
        <div className="space-y-6">
          {/* Info multijugador */}
          {isMultiplayer && (
            <MultiplayerInfo game={game} />
          )}
          
          <ShipPlacementDragDrop
            shipsToPlace={game.ships_to_place || []}
            placedShips={placedShips}
            onPlaceShip={handlePlaceShip}
            boardSize={game.board_size}
            loading={loading}
          />
        </div>
      )}

      {/* FASE 3: Juego Activo */}
      {gamePhase === 'playing' && board && (
        <div>
          {/* Info multijugador */}
          {isMultiplayer && (
            <div className="mb-6">
              <MultiplayerInfo 
                game={game} 
                isMyTurn={board.is_my_turn}
              />
            </div>
          )}

          {/* Controles superiores */}
          {stats && (
            <div className="mb-6">
              <GameControls
                gameId={game.id}
                stats={stats}
                onRefresh={() => {
                  refreshBoard();
                  refreshStats();
                }}
              />
            </div>
          )}

          {/* Tableros */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Tablero del jugador */}
            <Board
              size={board.board_size}
              ships={board.player_ships || []}
              shots={board.enemy_shots || []}
              showShips={true}
              title="🛡️ Tu Flota"
              disabled={true}
              onCellClick={() => {}}
              highlightCoordinate={lastAiShot}
            />

            {/* Tablero enemigo */}
            <Board
              size={board.board_size}
              ships={[]}
              shots={board.player_shots || []}
              showShips={false}
              title="🎯 Tablero Enemigo"
              disabled={loading}
              onCellClick={handleShoot}
            />
          </div>

          {/* Estadísticas */}
          {stats && (
            <div className="mb-6">
              <GameStats stats={stats} />
            </div>
          )}
        </div>
      )}

      {/* FASE 4: Juego Terminado */}
      {gamePhase === 'finished' && stats && (() => {
        // Determinar si el jugador actual ganó
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const isWinner = isMultiplayer 
          ? board?.winner === user.id 
          : board?.winner === 'player';
        
        return (
          <div className="text-center">
            <div className="bg-gray-800 rounded-lg p-8 max-w-2xl mx-auto">
              <div className="text-6xl mb-4">
                {isWinner ? '🎉' : '💥'}
              </div>
              
              <h2 className="text-3xl font-bold text-white mb-2">
                {isWinner ? '¡Victoria!' : 'Derrota'}
              </h2>
              
              <p className="text-gray-400 mb-6">
                {isWinner
                  ? '¡Has hundido toda la flota enemiga!' 
                  : isMultiplayer 
                    ? 'Tu oponente ha destruido tu flota'
                    : 'La IA ha destruido tu flota'}
              </p>

            {/* Resumen de estadísticas */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-700 p-4 rounded">
                <p className="text-gray-400 text-sm">Disparos totales</p>
                <p className="text-2xl font-bold text-white">
                  {stats.total_shots}
                </p>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <p className="text-gray-400 text-sm">Precisión</p>
                <p className="text-2xl font-bold text-white">
                  {stats.accuracy}%
                </p>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <p className="text-gray-400 text-sm">Barcos hundidos</p>
                <p className="text-2xl font-bold text-green-400">
                  {stats.enemy_ships_sunk || 0}
                </p>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <p className="text-gray-400 text-sm">Barcos perdidos</p>
                <p className="text-2xl font-bold text-red-400">
                  {stats.ships_sunk || 0}
                </p>
              </div>
            </div>

            <button
              onClick={handleNewGame}
              className="btn-primary px-8 py-3 text-lg"
            >
              🎮 Jugar de Nuevo
            </button>
          </div>
        </div>
        );
      })()}

      {/* Resultado de disparo */}
      {lastShot && (
        <ShotResult
          result={lastShot}
          onClose={() => setLastShot(null)}
        />
      )}

      {/* Modal para unirse a partida */}
      {showJoinModal && (
        <JoinGameModal
          onJoin={handleJoinGame}
          onCancel={() => setShowJoinModal(false)}
          loading={loading}
        />
      )}
      </div>
    </>
  );
};

export default GamePage;
