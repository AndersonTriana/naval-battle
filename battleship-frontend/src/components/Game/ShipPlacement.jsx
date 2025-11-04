import { useState } from 'react';
import { generateShipCoordinates, areCoordinatesInBounds } from '../../utils/coordinateUtils';

const ShipPlacement = ({ 
  shipsToPlace, 
  placedShips = [], 
  onPlaceShip, 
  boardSize = 10,
  loading = false 
}) => {
  const [selectedShip, setSelectedShip] = useState(null);
  const [startCoordinate, setStartCoordinate] = useState('');
  const [orientation, setOrientation] = useState('horizontal');
  const [preview, setPreview] = useState([]);
  const [error, setError] = useState('');

  const handleShipSelect = (ship) => {
    setSelectedShip(ship);
    setStartCoordinate('');
    setPreview([]);
    setError('');
  };

  const handleCoordinateChange = (value) => {
    const coord = value.toUpperCase();
    setStartCoordinate(coord);
    setError('');

    if (selectedShip && coord.length >= 2) {
      updatePreview(coord, orientation);
    } else {
      setPreview([]);
    }
  };

  const handleOrientationChange = (newOrientation) => {
    setOrientation(newOrientation);
    if (selectedShip && startCoordinate) {
      updatePreview(startCoordinate, newOrientation);
    }
  };

  const updatePreview = (coord, orient) => {
    try {
      const coordinates = generateShipCoordinates(coord, selectedShip.size, orient);
      
      if (!areCoordinatesInBounds(coordinates, boardSize)) {
        setError('El barco se sale del tablero');
        setPreview([]);
        return;
      }

      setPreview(coordinates);
    } catch (err) {
      setPreview([]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!selectedShip) {
      setError('Selecciona un barco');
      return;
    }

    if (!startCoordinate) {
      setError('Ingresa una coordenada');
      return;
    }

    if (preview.length === 0) {
      setError('Posición inválida');
      return;
    }

    onPlaceShip(selectedShip.id, startCoordinate, orientation);
    
    // Reset después de colocar
    setSelectedShip(null);
    setStartCoordinate('');
    setPreview([]);
  };

  const remainingShips = shipsToPlace.filter(
    ship => !placedShips.some(placed => placed.ship_template_id === ship.id)
  );

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h3 className="text-xl font-bold text-white mb-4">
        🚢 Colocar Barcos ({placedShips.length}/{shipsToPlace.length})
      </h3>

      {remainingShips.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-5xl mb-4">✅</div>
          <p className="text-green-400 font-bold text-lg">
            ¡Todos los barcos colocados!
          </p>
          <p className="text-gray-400 text-sm mt-2">
            El juego comenzará automáticamente
          </p>
        </div>
      ) : (
        <>
          {/* Lista de barcos disponibles */}
          <div className="mb-6">
            <p className="text-sm text-gray-400 mb-3">Barcos disponibles:</p>
            <div className="space-y-2">
              {remainingShips.map((ship) => (
                <button
                  key={ship.id}
                  onClick={() => handleShipSelect(ship)}
                  disabled={loading}
                  className={`w-full text-left p-3 rounded transition-all ${
                    selectedShip?.id === ship.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{ship.name}</span>
                    <span className="text-sm">
                      {'■'.repeat(ship.size)} ({ship.size})
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Formulario de colocación */}
          {selectedShip && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Coordenada inicial
                </label>
                <input
                  type="text"
                  value={startCoordinate}
                  onChange={(e) => handleCoordinateChange(e.target.value)}
                  className="input-field w-full uppercase"
                  placeholder="Ej: A1"
                  maxLength={3}
                  disabled={loading}
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Orientación
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleOrientationChange('horizontal')}
                    disabled={loading}
                    className={`py-2 px-4 rounded transition-all ${
                      orientation === 'horizontal'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    ➡️ Horizontal
                  </button>
                  <button
                    type="button"
                    onClick={() => handleOrientationChange('vertical')}
                    disabled={loading}
                    className={`py-2 px-4 rounded transition-all ${
                      orientation === 'vertical'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    ⬇️ Vertical
                  </button>
                </div>
              </div>

              {/* Preview */}
              {preview.length > 0 && (
                <div className="bg-gray-700 p-3 rounded">
                  <p className="text-sm text-gray-300 mb-2">Vista previa:</p>
                  <p className="text-indigo-400 font-mono text-sm">
                    {preview.join(', ')}
                  </p>
                </div>
              )}

              {/* Error */}
              {error && (
                <p className="text-red-400 text-sm">{error}</p>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading || preview.length === 0}
                className="btn-primary w-full disabled:opacity-50"
              >
                {loading ? 'Colocando...' : `Colocar ${selectedShip.name}`}
              </button>
            </form>
          )}

          {/* Barcos ya colocados */}
          {placedShips.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-700">
              <p className="text-sm text-gray-400 mb-3">Barcos colocados:</p>
              <div className="space-y-2">
                {placedShips.map((ship, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-sm bg-gray-700 p-2 rounded"
                  >
                    <span className="text-green-400">✓ {ship.name || 'Barco'}</span>
                    <span className="text-gray-400 text-xs">
                      {ship.coordinates?.[0]} - {ship.coordinates?.[ship.coordinates.length - 1]}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ShipPlacement;
