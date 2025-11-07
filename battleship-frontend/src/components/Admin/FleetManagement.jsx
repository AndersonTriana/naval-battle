import { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import Loading from '../Layout/Loading';

const FleetManagement = () => {
  const [fleets, setFleets] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingFleet, setEditingFleet] = useState(null);
  const [newFleet, setNewFleet] = useState({ name: '', board_size: 10, ship_template_ids: [] });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [fleetsData, templatesData] = await Promise.all([
        adminService.getAllBaseFleets(),
        adminService.getAllShipTemplates()
      ]);
      setFleets(Array.isArray(fleetsData) ? fleetsData : []);
      setTemplates(Array.isArray(templatesData) ? templatesData : []);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFleets = async () => {
    try {
      const data = await adminService.getAllBaseFleets();
      setFleets(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar flotas:', error);
    }
  };

  const handleCreateFleet = async (e) => {
    e.preventDefault();
    
    if (newFleet.ship_template_ids.length === 0) {
      alert('Debes seleccionar al menos un barco para la flota');
      return;
    }
    
    try {
      await adminService.createBaseFleet(newFleet);
      setShowCreateModal(false);
      setNewFleet({ name: '', board_size: 10, ship_template_ids: [] });
      loadFleets();
    } catch (error) {
      console.error('Error al crear flota:', error);
      alert(error.response?.data?.detail || 'Error al crear flota');
    }
  };

  const addShipTemplate = (templateId) => {
    setNewFleet(prev => ({
      ...prev,
      ship_template_ids: [...prev.ship_template_ids, templateId]
    }));
  };

  const removeShipTemplate = (templateId) => {
    setNewFleet(prev => {
      const index = prev.ship_template_ids.indexOf(templateId);
      if (index > -1) {
        const newIds = [...prev.ship_template_ids];
        newIds.splice(index, 1);
        return { ...prev, ship_template_ids: newIds };
      }
      return prev;
    });
  };

  const getShipCount = (templateId, shipIds) => {
    return shipIds.filter(id => id === templateId).length;
  };

  const calculateFleetStats = (shipIds, boardSize) => {
    let totalCells = 0;
    shipIds.forEach(templateId => {
      const template = templates.find(t => t.id === templateId);
      if (template) {
        totalCells += template.size;
      }
    });
    
    const boardTotalCells = boardSize * boardSize;
    const maxAllowedCells = Math.floor(boardTotalCells * 0.8);
    const percentage = (totalCells / boardTotalCells * 100).toFixed(1);
    const isValid = totalCells <= maxAllowedCells;
    
    return {
      totalCells,
      boardTotalCells,
      maxAllowedCells,
      percentage,
      isValid
    };
  };

  const addShipTemplateEdit = (templateId) => {
    setEditingFleet(prev => ({
      ...prev,
      ship_template_ids: [...prev.ship_template_ids, templateId]
    }));
  };

  const removeShipTemplateEdit = (templateId) => {
    setEditingFleet(prev => {
      const index = prev.ship_template_ids.indexOf(templateId);
      if (index > -1) {
        const newIds = [...prev.ship_template_ids];
        newIds.splice(index, 1);
        return { ...prev, ship_template_ids: newIds };
      }
      return prev;
    });
  };

  const handleEditFleet = (fleet) => {
    setEditingFleet({
      id: fleet.id,
      name: fleet.name,
      board_size: fleet.board_size,
      ship_template_ids: fleet.ship_template_ids || []
    });
    setShowEditModal(true);
  };

  const handleUpdateFleet = async (e) => {
    e.preventDefault();
    try {
      await adminService.updateBaseFleet(editingFleet.id, {
        name: editingFleet.name,
        board_size: editingFleet.board_size,
        ship_template_ids: editingFleet.ship_template_ids
      });
      setShowEditModal(false);
      setEditingFleet(null);
      loadFleets();
    } catch (error) {
      console.error('Error al actualizar flota:', error);
      alert(error.response?.data?.detail || 'Error al actualizar flota');
    }
  };

  const handleDeleteFleet = async (fleetId) => {
    console.log('Intentando eliminar flota:', fleetId);
    if (window.confirm('¿Eliminar esta flota? Esta acción no se puede deshacer.')) {
      try {
        console.log('Confirmado, eliminando...');
        const result = await adminService.deleteBaseFleet(fleetId);
        console.log('Resultado de eliminación:', result);
        // Recargar la lista de flotas después de eliminar
        console.log('Recargando lista de flotas...');
        await loadFleets();
        console.log('Lista recargada');
      } catch (error) {
        console.error('Error al eliminar flota:', error);
        alert(error.response?.data?.detail || 'Error al eliminar flota');
      }
    }
  };

  if (loading) {
    return <Loading message="Cargando flotas..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Gestión de Flotas</h2>
          <p className="text-gray-400 text-sm">Total: {fleets.length} flotas base</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          ➕ Crear Flota
        </button>
      </div>

      {/* Grid de flotas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {fleets.map((fleet) => (
          <div key={fleet.id} className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{fleet.name}</h3>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleEditFleet(fleet)}
                  className="text-indigo-400 hover:text-indigo-300 cursor-pointer transition-colors"
                  title="Editar"
                >
                  ✏️
                </button>
                <button
                  type="button"
                  onClick={() => handleDeleteFleet(fleet.id)}
                  className="text-red-400 hover:text-red-300 cursor-pointer transition-colors"
                  title="Eliminar"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Tamaño tablero:</span>
                <span className="text-white font-medium">{fleet.board_size}x{fleet.board_size}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Barcos:</span>
                <span className="text-white font-medium">{fleet.ship_count || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Creada:</span>
                <span className="text-white font-medium">
                  {new Date(fleet.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            {fleet.ship_template_ids && fleet.ship_template_ids.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-700">
                <p className="text-xs text-gray-400 mb-2">Barcos incluidos:</p>
                <div className="space-y-1">
                  {fleet.ship_template_ids.map((templateId) => {
                    const template = templates.find(t => t.id === templateId);
                    return template ? (
                      <div key={templateId} className="text-xs text-gray-300 flex justify-between">
                        <span>{template.name}</span>
                        <span className="text-gray-500">Tamaño: {template.size}</span>
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {fleets.length === 0 && (
        <div className="text-center py-12 bg-gray-800 rounded-lg">
          <p className="text-gray-400">No hay flotas base creadas</p>
        </div>
      )}

      {/* Modal Crear Flota */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Crear Nueva Flota</h3>
            <form onSubmit={handleCreateFleet} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nombre de la Flota
                </label>
                <input
                  type="text"
                  value={newFleet.name}
                  onChange={(e) => setNewFleet({ ...newFleet, name: e.target.value })}
                  className="input-field w-full"
                  placeholder="Ej: Flota Estándar"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tamaño del Tablero (5-20)
                </label>
                <input
                  type="number"
                  min="5"
                  max="20"
                  value={newFleet.board_size}
                  onChange={(e) => setNewFleet({ ...newFleet, board_size: parseInt(e.target.value) })}
                  className="input-field w-full"
                  required
                />
                <p className="text-xs text-gray-400 mt-1">
                  Tablero cuadrado de {newFleet.board_size}x{newFleet.board_size} celdas
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Barcos de la Flota *
                </label>
                {templates.length === 0 ? (
                  <p className="text-sm text-gray-400">
                    No hay plantillas de barcos. Crea plantillas primero.
                  </p>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto bg-gray-700 rounded p-3">
                    {templates.map((template) => {
                      const count = getShipCount(template.id, newFleet.ship_template_ids);
                      return (
                        <div
                          key={template.id}
                          className="flex items-center gap-3 p-2 rounded bg-gray-600"
                        >
                          <div className="flex-1">
                            <span className="text-white font-medium">{template.name}</span>
                            <span className="text-gray-400 text-sm ml-2">
                              (Tamaño: {template.size})
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => removeShipTemplate(template.id)}
                              disabled={count === 0}
                              className="w-8 h-8 bg-red-600 hover:bg-red-700 disabled:bg-gray-500 disabled:cursor-not-allowed text-white rounded font-bold transition-colors"
                            >
                              −
                            </button>
                            <span className="text-white font-bold w-8 text-center">{count}</span>
                            <button
                              type="button"
                              onClick={() => addShipTemplate(template.id)}
                              className="w-8 h-8 bg-green-600 hover:bg-green-700 text-white rounded font-bold transition-colors"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <p className="text-xs text-gray-400 mt-1">
                  Seleccionados: {newFleet.ship_template_ids.length} barcos
                </p>
              </div>

              {/* Indicador de capacidad */}
              {newFleet.ship_template_ids.length > 0 && (() => {
                const stats = calculateFleetStats(newFleet.ship_template_ids, newFleet.board_size);
                return (
                  <div className={`p-3 rounded border ${
                    stats.isValid 
                      ? 'bg-green-900/30 border-green-700' 
                      : 'bg-red-900/30 border-red-700'
                  }`}>
                    <div className="flex justify-between items-center mb-2">
                      <span className={`text-sm font-medium ${
                        stats.isValid ? 'text-green-200' : 'text-red-200'
                      }`}>
                        {stats.isValid ? '✓ Capacidad válida' : '⚠️ Capacidad excedida'}
                      </span>
                      <span className={`text-lg font-bold ${
                        stats.isValid ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {stats.percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                      <div 
                        className={`h-2 rounded-full transition-all ${
                          stats.isValid ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(stats.percentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-300">
                      {stats.totalCells} / {stats.maxAllowedCells} celdas (máx 80% de {stats.boardTotalCells})
                    </p>
                  </div>
                );
              })()}

              <div className="flex gap-2">
                <button 
                  type="submit" 
                  className="btn-primary flex-1"
                  disabled={!calculateFleetStats(newFleet.ship_template_ids, newFleet.board_size).isValid}
                >
                  Crear
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Editar Flota */}
      {showEditModal && editingFleet && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Editar Flota</h3>
            <form onSubmit={handleUpdateFleet} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nombre de la Flota
                </label>
                <input
                  type="text"
                  value={editingFleet.name}
                  onChange={(e) => setEditingFleet({ ...editingFleet, name: e.target.value })}
                  className="input-field w-full"
                  placeholder="Ej: Flota Estándar"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tamaño del Tablero (5-20)
                </label>
                <input
                  type="number"
                  min="5"
                  max="20"
                  value={editingFleet.board_size}
                  onChange={(e) => setEditingFleet({ ...editingFleet, board_size: parseInt(e.target.value) })}
                  className="input-field w-full"
                  required
                />
                <p className="text-xs text-gray-400 mt-1">
                  Tablero cuadrado de {editingFleet.board_size}x{editingFleet.board_size} celdas
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Barcos de la Flota *
                </label>
                {templates.length === 0 ? (
                  <p className="text-sm text-gray-400">
                    No hay plantillas de barcos. Crea plantillas primero.
                  </p>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto bg-gray-700 rounded p-3">
                    {templates.map((template) => {
                      const count = getShipCount(template.id, editingFleet.ship_template_ids);
                      return (
                        <div
                          key={template.id}
                          className="flex items-center gap-3 p-2 rounded bg-gray-600"
                        >
                          <div className="flex-1">
                            <span className="text-white font-medium">{template.name}</span>
                            <span className="text-gray-400 text-sm ml-2">
                              (Tamaño: {template.size})
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => removeShipTemplateEdit(template.id)}
                              disabled={count === 0}
                              className="w-8 h-8 bg-red-600 hover:bg-red-700 disabled:bg-gray-500 disabled:cursor-not-allowed text-white rounded font-bold transition-colors"
                            >
                              −
                            </button>
                            <span className="text-white font-bold w-8 text-center">{count}</span>
                            <button
                              type="button"
                              onClick={() => addShipTemplateEdit(template.id)}
                              className="w-8 h-8 bg-green-600 hover:bg-green-700 text-white rounded font-bold transition-colors"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <p className="text-xs text-gray-400 mt-1">
                  Seleccionados: {editingFleet.ship_template_ids.length} barcos
                </p>
              </div>

              {/* Indicador de capacidad */}
              {editingFleet.ship_template_ids.length > 0 && (() => {
                const stats = calculateFleetStats(editingFleet.ship_template_ids, editingFleet.board_size);
                return (
                  <div className={`p-3 rounded border ${
                    stats.isValid 
                      ? 'bg-green-900/30 border-green-700' 
                      : 'bg-red-900/30 border-red-700'
                  }`}>
                    <div className="flex justify-between items-center mb-2">
                      <span className={`text-sm font-medium ${
                        stats.isValid ? 'text-green-200' : 'text-red-200'
                      }`}>
                        {stats.isValid ? '✓ Capacidad válida' : '⚠️ Capacidad excedida'}
                      </span>
                      <span className={`text-lg font-bold ${
                        stats.isValid ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {stats.percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                      <div 
                        className={`h-2 rounded-full transition-all ${
                          stats.isValid ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(stats.percentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-300">
                      {stats.totalCells} / {stats.maxAllowedCells} celdas (máx 80% de {stats.boardTotalCells})
                    </p>
                  </div>
                );
              })()}

              <div className="bg-yellow-900/30 border border-yellow-700 rounded p-3">
                <p className="text-xs text-yellow-200">
                  ⚠️ Cambiar el tamaño del tablero puede afectar juegos existentes
                </p>
              </div>

              <div className="flex gap-2">
                <button 
                  type="submit" 
                  className="btn-primary flex-1"
                  disabled={!calculateFleetStats(editingFleet.ship_template_ids, editingFleet.board_size).isValid}
                >
                  Actualizar
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingFleet(null);
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetManagement;
