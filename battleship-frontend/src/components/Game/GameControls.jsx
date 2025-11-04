const GameControls = ({ gameId, stats, onRefresh }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-center">
        <div className="flex gap-6">
          {stats && (
            <>
              <div className="text-center">
                <p className="text-xs text-gray-400">Disparos</p>
                <p className="text-xl font-bold text-white">{stats.total_shots}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-400">Aciertos</p>
                <p className="text-xl font-bold text-green-400">{stats.hits}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-400">Fallos</p>
                <p className="text-xl font-bold text-red-400">{stats.misses}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-400">Precisión</p>
                <p className="text-xl font-bold text-indigo-400">{stats.accuracy}%</p>
              </div>
            </>
          )}
        </div>

        <button
          onClick={onRefresh}
          className="btn-secondary text-sm"
          title="Actualizar"
        >
          🔄 Actualizar
        </button>
      </div>
    </div>
  );
};

export default GameControls;
