import { useState } from 'react';
import { useGame } from '../hooks/useGame';
import FleetSelector from '../components/Game/FleetSelector';
import ShipPlacement from '../components/Game/ShipPlacement';
import Board from '../components/Game/Board';

const TestGamePage = () => {
  const { game, createGame, placeShip, loading } = useGame();
  const [step, setStep] = useState('select'); // 'select' | 'place' | 'play'

  const handleFleetSelected = async (fleet) => {
    const result = await createGame(fleet.id);
    if (result.success) {
      setStep('place');
    }
  };

  const handlePlaceShip = async (shipId, coord, orientation) => {
    const result = await placeShip(shipId, coord, orientation);
    if (result.success) {
      console.log('Barco colocado:', result.data);
      
      // Verificar si todos los barcos están colocados
      if (result.data.ships_remaining_to_place === 0) {
        setStep('play');
      }
    }
  };

  return (
    <div>
      {step === 'select' && (
        <FleetSelector onFleetSelected={handleFleetSelected} />
      )}

      {step === 'place' && game && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Board
            size={game.board_size}
            ships={[]}
            shots={[]}
            showShips={true}
            title="Coloca tus barcos"
            disabled={true}
          />
          <ShipPlacement
            shipsToPlace={game.ships_to_place || []}
            placedShips={[]}
            onPlaceShip={handlePlaceShip}
            boardSize={game.board_size}
            loading={loading}
          />
        </div>
      )}

      {step === 'play' && (
        <div className="text-center text-white">
          <h2 className="text-2xl font-bold">¡Juego listo!</h2>
          <p>Integración completa en la siguiente parte</p>
        </div>
      )}
    </div>
  );
};

export default TestGamePage;
