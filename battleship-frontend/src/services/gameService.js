import api from './api';

export const gameService = {
  // Obtener flotas disponibles
  async getAvailableFleets() {
    const response = await api.get('/player/available-fleets');
    return response.data;
  },

  // Crear nueva partida
  async createGame(baseFleetId) {
    const response = await api.post('/game/create', {
      base_fleet_id: baseFleetId
    });
    return response.data;
  },

  // Colocar barco
  async placeShip(gameId, shipTemplateId, startCoordinate, orientation) {
    const response = await api.post(`/game/${gameId}/place-ship`, {
      ship_template_id: shipTemplateId,
      start_coordinate: startCoordinate,
      orientation: orientation
    });
    return response.data;
  },

  // Obtener estado del tablero
  async getBoard(gameId) {
    const response = await api.get(`/game/${gameId}/board`);
    return response.data;
  },

  // Realizar disparo
  async shoot(gameId, coordinate) {
    const response = await api.post(`/game/${gameId}/shoot`, {
      coordinate: coordinate
    });
    return response.data;
  },

  // Obtener estadísticas
  async getStats(gameId) {
    const response = await api.get(`/game/${gameId}/stats`);
    return response.data;
  },

  // Obtener historial de disparos
  async getShotsHistory(gameId) {
    const response = await api.get(`/game/${gameId}/shots-history`);
    return response.data;
  },

  // Obtener mis juegos
  async getMyGames(status = null) {
    const params = status ? { status } : {};
    const response = await api.get('/player/my-games', { params });
    return response.data;
  },

  // Eliminar juego
  async deleteGame(gameId) {
    const response = await api.delete(`/game/${gameId}`);
    return response.data;
  }
};
