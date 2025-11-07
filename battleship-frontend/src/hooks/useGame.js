import { useState, useCallback } from 'react';
import { gameService } from '../services/gameService';

export const useGame = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [game, setGame] = useState(null);
  const [board, setBoard] = useState(null);
  const [stats, setStats] = useState(null);
  const [shots, setShots] = useState([]);

  // Crear nuevo juego
  const createGame = useCallback(async (baseFleetId, isMultiplayer = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await gameService.createGame(baseFleetId, isMultiplayer);
      setGame(data);
      return { success: true, data };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al crear juego';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Colocar barco
  const placeShip = useCallback(async (shipTemplateId, startCoordinate, orientation) => {
    if (!game?.id) {
      setError('No hay juego activo');
      return { success: false, error: 'No hay juego activo' };
    }

    setLoading(true);
    setError(null);

    try {
      const data = await gameService.placeShip(
        game.id,
        shipTemplateId,
        startCoordinate,
        orientation
      );
      
      // Actualizar estado del juego
      await refreshBoard();
      
      return { success: true, data };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al colocar barco';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, [game]);

  // Disparar
  const shoot = useCallback(async (coordinate) => {
    if (!game?.id) {
      setError('No hay juego activo');
      return { success: false, error: 'No hay juego activo' };
    }

    setLoading(true);
    setError(null);

    try {
      const data = await gameService.shoot(game.id, coordinate);
      
      // Actualizar disparos y stats
      await Promise.all([
        refreshBoard(),
        refreshStats()
      ]);
      
      return { success: true, data };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al disparar';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, [game]);

  // Refrescar tablero
  const refreshBoard = useCallback(async () => {
    if (!game?.id) return;

    try {
      const data = await gameService.getBoard(game.id);
      setBoard(data);
      
      // Actualizar también el estado del juego si cambió
      if (data.status && data.status !== game.status) {
        setGame(prev => ({ ...prev, status: data.status }));
      }
    } catch (err) {
      console.error('Error al refrescar tablero:', err);
    }
  }, [game]);

  // Refrescar estadísticas
  const refreshStats = useCallback(async () => {
    if (!game?.id) return;

    try {
      const data = await gameService.getStats(game.id);
      setStats(data);
    } catch (err) {
      console.error('Error al refrescar stats:', err);
    }
  }, [game]);

  // Cargar historial de disparos
  const loadShotsHistory = useCallback(async () => {
    if (!game?.id) return;

    try {
      const data = await gameService.getShotsHistory(game.id);
      setShots(data.shots || []);
    } catch (err) {
      console.error('Error al cargar historial:', err);
    }
  }, [game]);

  // Unirse a un juego
  const joinGame = useCallback(async (gameId) => {
    setLoading(true);
    setError(null);

    try {
      const data = await gameService.joinGame(gameId);
      
      // Actualizar estado del juego con los datos recibidos
      if (data.game) {
        setGame({
          id: data.game.id,
          status: data.game.status,
          board_size: data.game.board_size,
          is_multiplayer: data.game.is_multiplayer,
          player1_id: data.game.player1_id,
          player2_id: data.game.player2_id,
          ships_to_place: data.ships_to_place || []
        });
      }

      return { success: true, data };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al unirse a la partida';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Cargar juego existente
  const loadGame = useCallback(async (gameId) => {
    setLoading(true);
    setError(null);

    try {
      const [boardData, statsData] = await Promise.all([
        gameService.getBoard(gameId),
        gameService.getStats(gameId)
      ]);

      // Establecer el juego con el status correcto
      setGame({ 
        id: gameId, 
        status: boardData.status,
        board_size: boardData.board_size,
        is_multiplayer: boardData.is_multiplayer
      });
      setBoard(boardData);
      setStats(statsData);

      return { success: true };
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al cargar juego';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, []);

  // Resetear estado
  const resetGame = useCallback(() => {
    setGame(null);
    setBoard(null);
    setStats(null);
    setShots([]);
    setError(null);
  }, []);

  return {
    // Estado
    loading,
    error,
    game,
    board,
    stats,
    shots,
    
    // Acciones
    createGame,
    joinGame,
    placeShip,
    shoot,
    refreshBoard,
    refreshStats,
    loadShotsHistory,
    loadGame,
    resetGame
  };
};
