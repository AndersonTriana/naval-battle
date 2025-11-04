import api from './api';

export const adminService = {
  // ========== PLANTILLAS DE BARCOS ==========

  // Obtener todas las plantillas de barcos
  async getAllShipTemplates() {
    const response = await api.get('/admin/ship-templates');
    return response.data;
  },

  // Obtener plantilla por ID
  async getShipTemplate(templateId) {
    const response = await api.get(`/admin/ship-templates/${templateId}`);
    return response.data;
  },

  // Crear plantilla de barco
  async createShipTemplate(templateData) {
    const response = await api.post('/admin/ship-templates', templateData);
    return response.data;
  },

  // Actualizar plantilla de barco
  async updateShipTemplate(templateId, templateData) {
    const response = await api.put(`/admin/ship-templates/${templateId}`, templateData);
    return response.data;
  },

  // Eliminar plantilla de barco
  async deleteShipTemplate(templateId) {
    const response = await api.delete(`/admin/ship-templates/${templateId}`);
    return response.data;
  },

  // ========== FLOTAS BASE ==========

  // Obtener todas las flotas base
  async getAllBaseFleets() {
    const response = await api.get('/admin/base-fleets');
    return response.data;
  },

  // Crear flota base
  async createBaseFleet(fleetData) {
    const response = await api.post('/admin/base-fleets', fleetData);
    return response.data;
  },

  // Actualizar flota base
  async updateBaseFleet(fleetId, fleetData) {
    const response = await api.put(`/admin/base-fleets/${fleetId}`, fleetData);
    return response.data;
  },

  // Eliminar flota base
  async deleteBaseFleet(fleetId) {
    // DELETE devuelve 204 No Content, no hay data en la respuesta
    await api.delete(`/admin/base-fleets/${fleetId}`);
    return { success: true };
  },

  // Agregar barco a flota
  async addShipToFleet(fleetId, shipData) {
    const response = await api.post(`/admin/base-fleets/${fleetId}/ships`, shipData);
    return response.data;
  },

  // Eliminar barco de flota
  async removeShipFromFleet(fleetId, shipTemplateId) {
    const response = await api.delete(`/admin/base-fleets/${fleetId}/ships/${shipTemplateId}`);
    return response.data;
  }
};
