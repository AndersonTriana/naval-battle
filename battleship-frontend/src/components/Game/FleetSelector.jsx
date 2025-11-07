import { useState, useEffect } from 'react';
import { gameService } from '../../services/gameService';
import Loading from '../Layout/Loading';

const FleetSelector = ({ onFleetSelected }) => {
  const [fleets, setFleets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFleet, setSelectedFleet] = useState(null);

  useEffect(() => {
    loadFleets();
  }, []);

  const loadFleets = async () => {
    try {
      const data = await gameService.getAvailableFleets();
      // El backend devuelve un array directamente, no un objeto con propiedad 'fleets'
      setFleets(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar flotas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (fleet) => {
    setSelectedFleet(fleet);
  };

  const handleConfirm = () => {
    if (selectedFleet) {
      onFleetSelected(selectedFleet);
    }
  };

  if (loading) {
    return <Loading message="Cargando flotas disponibles..." />;
  }

  if (fleets.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 text-lg">
          No hay flotas disponibles. Contacta al administrador.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">
          Selecciona tu Flota
        </h2>
        <p className="text-gray-400">
          Elige una configuración de barcos para comenzar
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {fleets.map((fleet) => (
          <div
            key={fleet.id}
            onClick={() => handleSelect(fleet)}
            className={`bg-gray-800 rounded-lg p-6 cursor-pointer transition-all border-2 ${
              selectedFleet?.id === fleet.id
                ? 'border-indigo-500 shadow-lg shadow-indigo-500/50'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <h3 className="text-xl font-bold text-white mb-2">
              {fleet.name}
            </h3>
            <p className="text-gray-400 text-sm mb-4">
              Tablero: {fleet.board_size}x{fleet.board_size}
            </p>
            
            <div className="space-y-2">
              <p className="text-sm text-gray-300 font-medium mb-2">
                {fleet.ship_count} barcos:
              </p>
              {fleet.ships && fleet.ships.length > 0 ? (
                <div className="space-y-1">
                  {fleet.ships.map((ship, index) => (
                    <div key={`${ship.id}-${index}`} className="flex items-center gap-2 text-sm text-gray-400">
                      <span className="text-indigo-400">⚓</span>
                      <span>{ship.name}</span>
                      <span className="text-xs text-gray-500">({ship.size} casillas)</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">Detalles no disponibles</p>
              )}
            </div>

            {selectedFleet?.id === fleet.id && (
              <div className="mt-4 flex items-center gap-2 text-indigo-400">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Seleccionada</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedFleet && (
        <div className="mt-8 text-center">
          <button
            onClick={handleConfirm}
            className="btn-primary px-8 py-3 text-lg"
          >
            Comenzar Juego con {selectedFleet.name}
          </button>
        </div>
      )}
    </div>
  );
};

export default FleetSelector;
