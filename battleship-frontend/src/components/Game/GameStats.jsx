const GameStats = ({ stats, shipsInfo = [] }) => {
  if (!stats) return null;

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">📊 Estadísticas</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total de Disparos"
          value={stats.total_shots || 0}
          icon="🎯"
        />
        <StatCard
          label="Aciertos"
          value={stats.hits || 0}
          icon="✅"
          className="text-green-400"
        />
        <StatCard
          label="Fallos"
          value={stats.misses || 0}
          icon="❌"
          className="text-red-400"
        />
        <StatCard
          label="Precisión"
          value={`${stats.accuracy || 0}%`}
          icon="📈"
          className="text-indigo-400"
        />
        <StatCard
          label="Barcos Hundidos"
          value={stats.enemy_ships_sunk || 0}
          icon="⚓"
          className="text-green-400"
          tooltip="Barcos enemigos que has hundido"
        />
        <StatCard
          label="Barcos Perdidos"
          value={stats.ships_sunk || 0}
          icon="💥"
          className="text-red-400"
          tooltip="Tus barcos hundidos por la IA"
        />
        <StatCard
          label="Tiempo de Juego"
          value={formatDuration(stats.game_duration_seconds)}
          icon="⏱️"
        />
        <StatCard
          label="Racha Actual"
          value={stats.current_streak || 0}
          icon="🔥"
          className="text-orange-400"
        />
      </div>

      {/* Lista de barcos */}
      {shipsInfo && shipsInfo.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-700">
          <p className="text-gray-400 text-sm mb-3">Estado de la flota:</p>
          <div className="space-y-2">
            {shipsInfo.map((ship, index) => (
              <div
                key={index}
                className="flex items-center justify-between text-sm bg-gray-700 p-2 rounded"
              >
                <span className={ship.is_sunk ? 'text-red-400 line-through' : 'text-gray-300'}>
                  {ship.name}
                </span>
                <span className="text-xs text-gray-500">
                  {ship.is_sunk ? '💀 Hundido' : '⛵ Activo'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ label, value, icon, className = '' }) => (
  <div className="bg-gray-700 p-4 rounded text-center">
    <div className="text-2xl mb-1">{icon}</div>
    <p className="text-xs text-gray-400 mb-1">{label}</p>
    <p className={`text-2xl font-bold ${className || 'text-white'}`}>
      {value}
    </p>
  </div>
);

export default GameStats;
