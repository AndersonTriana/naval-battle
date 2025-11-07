import { useState } from 'react';

const MultiplayerInfo = ({ game, isMyTurn }) => {
  const [copied, setCopied] = useState(false);

  const copyGameId = () => {
    navigator.clipboard.writeText(game.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getStatusInfo = () => {
    const statusMap = {
      'waiting_for_player2': {
        icon: '⏳',
        text: 'Esperando jugador 2',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20'
      },
      'both_players_setup': {
        icon: '🚢',
        text: 'Ambos jugadores colocando barcos',
        color: 'text-cyan-400',
        bgColor: 'bg-cyan-900/20'
      },
      'player1_setup': {
        icon: '🚢',
        text: 'Jugador 1 colocando barcos',
        color: 'text-blue-400',
        bgColor: 'bg-blue-900/20'
      },
      'player2_setup': {
        icon: '🚢',
        text: 'Jugador 2 colocando barcos',
        color: 'text-purple-400',
        bgColor: 'bg-purple-900/20'
      },
      'player1_turn': {
        icon: '🎯',
        text: 'Turno del Jugador 1',
        color: 'text-green-400',
        bgColor: 'bg-green-900/20'
      },
      'player2_turn': {
        icon: '🎯',
        text: 'Turno del Jugador 2',
        color: 'text-green-400',
        bgColor: 'bg-green-900/20'
      },
      'player1_won': {
        icon: '🏆',
        text: '¡Jugador 1 ganó!',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20'
      },
      'player2_won': {
        icon: '🏆',
        text: '¡Jugador 2 ganó!',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20'
      }
    };

    return statusMap[game.status] || {
      icon: '❓',
      text: game.status,
      color: 'text-gray-400',
      bgColor: 'bg-gray-900/20'
    };
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          👥 Partida Multijugador
        </h3>
        {isMyTurn !== undefined && (
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
            isMyTurn ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'
          }`}>
            {isMyTurn ? '✓ Tu turno' : '⏳ Esperando'}
          </div>
        )}
      </div>

      {/* Estado */}
      <div className={`${statusInfo.bgColor} rounded-lg p-4`}>
        <div className="flex items-center gap-3">
          <span className="text-3xl">{statusInfo.icon}</span>
          <div>
            <p className={`font-bold ${statusInfo.color}`}>
              {statusInfo.text}
            </p>
            {game.status === 'waiting_for_player2' && (
              <p className="text-sm text-gray-400 mt-1">
                Comparte el ID de la partida con tu oponente
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ID de la partida */}
      <div>
        <label className="block text-sm font-medium text-gray-400 mb-2">
          ID de la Partida
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={game.id}
            readOnly
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm font-mono"
          />
          <button
            onClick={copyGameId}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm font-bold"
          >
            {copied ? '✓ Copiado' : '📋 Copiar'}
          </button>
        </div>
      </div>

      {/* Jugadores */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-700 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Jugador 1</p>
          <p className="text-sm font-bold text-white truncate">
            🔵 {game.player1_username || game.player1_id?.substring(0, 8) + '...' || '—'}
          </p>
        </div>
        <div className="bg-gray-700 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Jugador 2</p>
          <p className="text-sm font-bold text-white truncate">
            {game.player2_id ? `🟣 ${game.player2_username || game.player2_id.substring(0, 8) + '...'}` : '⏳ Esperando...'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default MultiplayerInfo;
