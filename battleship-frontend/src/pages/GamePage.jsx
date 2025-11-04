import { useState, useEffect } from 'react';
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

const GamePage = () => {
  const {
    game,
    board,
    stats,
    loading,
    error,
    createGame,
    placeShip,
    shoot,
    refreshBoard,
    refreshStats,
    loadShotsHistory,
    resetGame
  } = useGame();

  const { notification, showError, showSuccess, hideNotification } = useNotification();
  const [gamePhase, setGamePhase] = useState('select'); // 'select' | 'placement' | 'playing' | 'finished'
  const [placedShips, setPlacedShips] = useState([]);
  const [lastShot, setLastShot] = useState(null);
  const [lastAiShot, setLastAiShot] = useState(null);

  // Verificar fase del juego cuando cambia el estado
  useEffect(() => {
    if (game) {
      if (game.status === 'placing_ships') {
        setGamePhase('placement');
      } else if (game.status === 'in_progress') {
        setGamePhase('playing');
      } else if (game.status === 'finished') {
        setGamePhase('finished');
      }
    }
    // También verificar si hay un ganador en board
    if (board && board.winner) {
      setGamePhase('finished');
    }
  }, [game, board]);

  // Cargar datos cuando el juego está activo
  useEffect(() => {
    if (gamePhase === 'playing') {
      refreshBoard();
      refreshStats();
      loadShotsHistory();
    }
  }, [gamePhase]);

  // Mostrar errores
  useEffect(() => {
    if (error) {
      showError(error);
    }
  }, [error]);

  // Handler: Seleccionar flota
  const handleFleetSelected = async (fleet) => {
    const result = await createGame(fleet.id);
    if (result.success) {
      setPlacedShips([]);
      setGamePhase('placement');
      showSuccess('¡Flota seleccionada! Coloca tus barcos');
    }
  };

  // Handler: Colocar barco
  const handlePlaceShip = async (shipTemplateId, startCoordinate, orientation) => {
    const result = await placeShip(shipTemplateId, startCoordinate, orientation);
    
    if (result.success) {
      // El backend devuelve: { ship: { name, coordinates }, ships_remaining_to_place }
      const newShip = {
        ship_template_id: shipTemplateId,
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
    setGamePhase('select');
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

      {/* FASE 1: Selección de Flota */}
      {gamePhase === 'select' && (
        <FleetSelector onFleetSelected={handleFleetSelected} />
      )}

      {/* FASE 2: Colocación de Barcos */}
      {gamePhase === 'placement' && game && (
        <ShipPlacementDragDrop
          shipsToPlace={game.ships_to_place || []}
          placedShips={placedShips}
          onPlaceShip={handlePlaceShip}
          boardSize={game.board_size}
          loading={loading}
        />
      )}

      {/* FASE 3: Juego Activo */}
      {gamePhase === 'playing' && board && (
        <div>
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
      {gamePhase === 'finished' && stats && (
        <div className="text-center">
          <div className="bg-gray-800 rounded-lg p-8 max-w-2xl mx-auto">
            <div className="text-6xl mb-4">
              {board?.winner === 'player' ? '🎉' : '💥'}
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-2">
              {board?.winner === 'player' ? '¡Victoria!' : 'Derrota'}
            </h2>
            
            <p className="text-gray-400 mb-6">
              {board?.winner === 'player' 
                ? '¡Has hundido toda la flota enemiga!' 
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
      )}

      {/* Resultado de disparo */}
      {lastShot && (
        <ShotResult
          result={lastShot}
          onClose={() => setLastShot(null)}
        />
      )}
      </div>
    </>
  );
};

export default GamePage;
