import { useState } from 'react';
import { isValidCoordinate } from '../../utils/coordinateUtils';

const ShootControl = ({ onShoot, disabled = false, boardSize = 10 }) => {
  const [coordinate, setCoordinate] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    const coord = coordinate.toUpperCase().trim();

    // Validación
    if (!coord) {
      setError('Ingresa una coordenada');
      return;
    }

    if (!isValidCoordinate(coord, boardSize)) {
      setError(`Coordenada inválida. Usa formato A1-${String.fromCharCode(64 + boardSize)}${boardSize}`);
      return;
    }

    // Disparar
    onShoot(coord);
    setCoordinate('');
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h3 className="text-xl font-bold text-white mb-4">🎯 Disparar</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Coordenada (ej: A1, B5, J10)
          </label>
          <input
            type="text"
            value={coordinate}
            onChange={(e) => setCoordinate(e.target.value)}
            className="input-field w-full uppercase"
            placeholder="A1"
            disabled={disabled}
            maxLength={3}
            autoComplete="off"
          />
          {error && (
            <p className="mt-2 text-sm text-red-400">{error}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={disabled}
          className="btn-primary w-full disabled:opacity-50"
        >
          {disabled ? 'Disparando...' : 'Disparar'}
        </button>
      </form>

      {/* Quick buttons (opcional) */}
      <div className="mt-4">
        <p className="text-xs text-gray-400 mb-2">Acceso rápido:</p>
        <div className="grid grid-cols-5 gap-1">
          {['A1', 'B2', 'C3', 'D4', 'E5'].map((coord) => (
            <button
              key={coord}
              onClick={() => setCoordinate(coord)}
              className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs py-1 px-2 rounded"
              disabled={disabled}
            >
              {coord}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ShootControl;
