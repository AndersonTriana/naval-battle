import { useState } from 'react';

const GameModeSelector = ({ onModeSelected }) => {
  const [selectedMode, setSelectedMode] = useState(null);

  const modes = [
    {
      id: 'vs-ai',
      title: '🤖 Vs IA',
      description: 'Juega contra la inteligencia artificial',
      color: 'from-blue-600 to-blue-800',
      isMultiplayer: false
    },
    {
      id: 'multiplayer',
      title: '👥 Multijugador',
      description: 'Juega contra otro jugador humano',
      color: 'from-purple-600 to-purple-800',
      isMultiplayer: true
    }
  ];

  const handleSelect = (mode) => {
    setSelectedMode(mode.id);
    onModeSelected(mode.isMultiplayer);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          Selecciona el Modo de Juego
        </h2>
        <p className="text-gray-400">
          Elige cómo quieres jugar
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {modes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => handleSelect(mode)}
            className={`
              relative overflow-hidden rounded-xl p-8 
              bg-gradient-to-br ${mode.color}
              hover:scale-105 transform transition-all duration-200
              ${selectedMode === mode.id ? 'ring-4 ring-white' : ''}
            `}
          >
            <div className="text-center">
              <div className="text-6xl mb-4">
                {mode.id === 'vs-ai' ? '🤖' : '👥'}
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                {mode.title}
              </h3>
              <p className="text-gray-200 text-sm">
                {mode.description}
              </p>
            </div>

            {/* Decoración */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-5 rounded-full -mr-16 -mt-16" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white opacity-5 rounded-full -ml-12 -mb-12" />
          </button>
        ))}
      </div>
    </div>
  );
};

export default GameModeSelector;
