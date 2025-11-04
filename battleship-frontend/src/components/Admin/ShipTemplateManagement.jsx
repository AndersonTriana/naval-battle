import { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import Loading from '../Layout/Loading';

const ShipTemplateManagement = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTemplate, setNewTemplate] = useState({ name: '', size: 2, description: '' });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await adminService.getAllShipTemplates();
      setTemplates(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar plantillas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    try {
      await adminService.createShipTemplate(newTemplate);
      setShowCreateModal(false);
      setNewTemplate({ name: '', size: 2, description: '' });
      loadTemplates();
    } catch (error) {
      console.error('Error al crear plantilla:', error);
      alert(error.response?.data?.detail || 'Error al crear plantilla');
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (window.confirm('¿Eliminar esta plantilla de barco?')) {
      try {
        await adminService.deleteShipTemplate(templateId);
        loadTemplates();
      } catch (error) {
        console.error('Error al eliminar plantilla:', error);
        alert(error.response?.data?.detail || 'Error al eliminar plantilla');
      }
    }
  };

  if (loading) {
    return <Loading message="Cargando plantillas..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Plantillas de Barcos</h2>
          <p className="text-gray-400 text-sm">Total: {templates.length} plantillas</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          ➕ Crear Plantilla
        </button>
      </div>

      {/* Grid de plantillas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div key={template.id} className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{template.name}</h3>
              </div>
              <button
                type="button"
                onClick={() => handleDeleteTemplate(template.id)}
                className="text-red-400 hover:text-red-300 cursor-pointer"
                title="Eliminar"
              >
                🗑️
              </button>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Tamaño:</span>
                <span className="text-white font-medium">{template.size} celdas</span>
              </div>
              {template.description && (
                <div className="text-sm">
                  <span className="text-gray-400">Descripción:</span>
                  <p className="text-white mt-1">{template.description}</p>
                </div>
              )}
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Creada:</span>
                <span className="text-white font-medium">
                  {new Date(template.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12 bg-gray-800 rounded-lg">
          <p className="text-gray-400">No hay plantillas de barcos creadas</p>
        </div>
      )}

      {/* Modal Crear Plantilla */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Crear Plantilla de Barco</h3>
            <form onSubmit={handleCreateTemplate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nombre del Barco
                </label>
                <input
                  type="text"
                  value={newTemplate.name}
                  onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                  className="input-field w-full"
                  placeholder="Ej: Portaaviones, Destructor"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tamaño (1-10 celdas)
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={newTemplate.size}
                  onChange={(e) => setNewTemplate({ ...newTemplate, size: parseInt(e.target.value) })}
                  className="input-field w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Descripción (opcional)
                </label>
                <textarea
                  value={newTemplate.description}
                  onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                  className="input-field w-full"
                  rows="3"
                  placeholder="Descripción del barco..."
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn-primary flex-1">
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
    </div>
  );
};

export default ShipTemplateManagement;
