import { useState } from 'react';
import AvailableGamesList from './AvailableGamesList';

const JoinGameModal = ({ onJoin, onCancel, loading }) => {
  const [gameId, setGameId] = useState('');
  const [showManualInput, setShowManualInput] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (gameId.trim()) {
      onJoin(gameId.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-gray-800 rounded-xl p-8 max-w-3xl w-full shadow-2xl my-8">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-bold text-white">
            🎮 Unirse a Partida Multijugador
          </h2>
          <button
            onClick={onCancel}
            disabled={loading}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        {!showManualInput ? (
          <>
            {/* Lista de partidas disponibles */}
            <AvailableGamesList
              onJoinGame={onJoin}
              onShowManualJoin={() => setShowManualInput(true)}
            />
          </>
        ) : (
          <>
            {/* Input manual de ID */}
            <div className="space-y-4">
              <button
                onClick={() => setShowManualInput(false)}
                className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-2"
              >
                ← Volver a la lista
              </button>

              <p className="text-gray-400">
                Ingresa el ID de la partida a la que quieres unirte
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    ID de la Partida
                  </label>
                  <input
                    type="text"
                    value={gameId}
                    onChange={(e) => setGameId(e.target.value)}
                    placeholder="Ej: game-abc123..."
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    disabled={loading}
                    autoFocus
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={!gameId.trim() || loading}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-colors"
                  >
                    {loading ? 'Uniéndose...' : 'Unirse'}
                  </button>
                  <button
                    type="button"
                    onClick={onCancel}
                    disabled={loading}
                    className="flex-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </form>

              <div className="p-4 bg-gray-700 rounded-lg">
                <p className="text-xs text-gray-400">
                  💡 <strong>Tip:</strong> El jugador 1 debe compartir el ID de la partida contigo
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default JoinGameModal;
