import { useState } from 'react';
import { generateShipCoordinates, areCoordinatesInBounds, coordinateToIndices } from '../../utils/coordinateUtils';

const ShipPlacementDragDrop = ({ 
  shipsToPlace, 
  placedShips = [], 
  onPlaceShip, 
  boardSize = 10,
  loading = false 
}) => {
  const [selectedShip, setSelectedShip] = useState(null);
  const [orientation, setOrientation] = useState('horizontal');
  const [draggedShip, setDraggedShip] = useState(null);
  const [hoverCell, setHoverCell] = useState(null);
  const [previewCoords, setPreviewCoords] = useState([]);

  // Filtrar barcos que aún no han sido colocados
  // Usar index para distinguir barcos del mismo tipo
  const remainingShips = shipsToPlace.filter(
    ship => !placedShips.some(placed => 
      placed.ship_index !== undefined 
        ? placed.ship_index === ship.index  // Comparar por index si existe
        : placed.ship_template_id === ship.id  // Fallback a id (legacy)
    )
  );

  // Generar el tablero
  const generateBoard = () => {
    const board = [];
    for (let row = 0; row < boardSize; row++) {
      for (let col = 0; col < boardSize; col++) {
        const letter = String.fromCharCode(65 + row); // A, B, C...
        const coordinate = `${letter}${col + 1}`;
        board.push({ row, col, coordinate });
      }
    }
    return board;
  };

  const board = generateBoard();

  // Manejar inicio de arrastre
  const handleDragStart = (e, ship) => {
    setDraggedShip(ship);
    setSelectedShip(ship);
    e.dataTransfer.effectAllowed = 'move';
  };

  // Manejar fin de arrastre
  const handleDragEnd = () => {
    setDraggedShip(null);
    setHoverCell(null);
    setPreviewCoords([]);
  };

  // Manejar hover sobre celda
  const handleDragOver = (e, cell) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    if (!draggedShip) return;

    setHoverCell(cell);
    
    try {
      const coords = generateShipCoordinates(cell.coordinate, draggedShip.size, orientation);
      
      if (areCoordinatesInBounds(coords, boardSize)) {
        // Verificar si alguna coordenada está ocupada
        const isOccupied = coords.some(coord => 
          placedShips.some(placed => 
            placed.coordinates?.includes(coord)
          )
        );
        
        if (!isOccupied) {
          setPreviewCoords(coords);
        } else {
          setPreviewCoords([]);
        }
      } else {
        setPreviewCoords([]);
      }
    } catch (error) {
      setPreviewCoords([]);
    }
  };

  // Manejar drop en celda
  const handleDrop = (e, cell) => {
    e.preventDefault();
    
    if (!draggedShip || previewCoords.length === 0) {
      return;
    }

    onPlaceShip(draggedShip.id, cell.coordinate, orientation, draggedShip.index);
    
    // Reset
    setDraggedShip(null);
    setSelectedShip(null);
    setHoverCell(null);
    setPreviewCoords([]);
  };

  // Verificar si una celda está ocupada
  const isCellOccupied = (coordinate) => {
    // Verificar en todas las formas posibles que el backend puede devolver las coordenadas
    return placedShips.some(ship => {
      if (ship.coordinates && Array.isArray(ship.coordinates)) {
        return ship.coordinates.includes(coordinate);
      }
      if (ship.ship_coordinates && Array.isArray(ship.ship_coordinates)) {
        return ship.ship_coordinates.includes(coordinate);
      }
      return false;
    });
  };

  // Verificar si una celda está en preview
  const isCellInPreview = (coordinate) => {
    return previewCoords.includes(coordinate);
  };

  // Obtener clase de celda
  const getCellClass = (cell) => {
    const baseClass = "w-full h-full flex items-center justify-center text-xs font-bold transition-all";
    
    const isOccupied = isCellOccupied(cell.coordinate);
    const isPreview = isCellInPreview(cell.coordinate);
    const isHover = hoverCell?.coordinate === cell.coordinate && draggedShip;
    
    if (isOccupied) {
      return `${baseClass} bg-blue-600 text-white shadow-lg`;
    }
    
    if (isPreview) {
      return `${baseClass} bg-green-500 text-white animate-pulse shadow-lg`;
    }
    
    if (isHover) {
      return `${baseClass} bg-gray-600 border-2 border-indigo-400`;
    }
    
    return `${baseClass} bg-gray-700 hover:bg-gray-600 cursor-pointer`;
  };

  // Obtener contenido de celda
  const getCellContent = (cell) => {
    if (isCellOccupied(cell.coordinate)) {
      return '🚢';
    }
    if (isCellInPreview(cell.coordinate)) {
      return '✓';
    }
    return '';
  };

  // Cambiar orientación con tecla R
  const handleKeyPress = (e) => {
    if (e.key === 'r' || e.key === 'R') {
      setOrientation(prev => prev === 'horizontal' ? 'vertical' : 'horizontal');
      setPreviewCoords([]);
    }
  };

  return (
    <div className="space-y-6" onKeyDown={handleKeyPress} tabIndex={0}>
      {/* Header */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-xl font-bold text-white mb-2">
          🚢 Colocar Barcos ({placedShips.length}/{shipsToPlace.length})
        </h3>
        <p className="text-sm text-gray-400">
          Arrastra los barcos al tablero o haz click para seleccionar
        </p>
      </div>

      {remainingShips.length === 0 ? (
        <div className="bg-gray-800 p-8 rounded-lg text-center">
          <div className="text-5xl mb-4">✅</div>
          <p className="text-green-400 font-bold text-lg">
            ¡Todos los barcos colocados!
          </p>
          <p className="text-gray-400 text-sm mt-2">
            El juego comenzará automáticamente
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panel izquierdo: Barcos disponibles */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 p-4 rounded-lg space-y-4">
              <div>
                <h4 className="text-lg font-bold text-white mb-3">Barcos Disponibles</h4>
                <div className="space-y-2">
                  {remainingShips.map((ship, idx) => {
                    // Contar cuántos barcos del mismo tipo hay en total y cuál es este
                    const sameTypeShips = shipsToPlace.filter(s => s.id === ship.id);
                    const shipNumber = sameTypeShips.findIndex(s => s.index === ship.index) + 1;
                    const displayName = sameTypeShips.length > 1 
                      ? `${ship.name} #${shipNumber}` 
                      : ship.name;
                    
                    return (
                      <div
                        key={ship.index !== undefined ? `ship-${ship.index}` : `ship-${ship.id}-${idx}`}
                        draggable={!loading}
                        onDragStart={(e) => handleDragStart(e, ship)}
                        onDragEnd={handleDragEnd}
                        onClick={() => setSelectedShip(ship)}
                        className={`p-3 rounded cursor-move transition-all ${
                          selectedShip?.index === ship.index
                            ? 'bg-indigo-600 text-white shadow-lg scale-105'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        } ${draggedShip?.index === ship.index ? 'opacity-50' : ''}`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{displayName}</span>
                          <span className="text-sm">
                            {'■'.repeat(ship.size)} ({ship.size})
                          </span>
                        </div>
                        {ship.description && (
                          <p className="text-xs text-gray-400 mt-1">{ship.description}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Control de orientación */}
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Orientación</h4>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setOrientation('horizontal')}
                    className={`py-2 px-3 rounded text-sm transition-all ${
                      orientation === 'horizontal'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    ➡️ Horizontal
                  </button>
                  <button
                    type="button"
                    onClick={() => setOrientation('vertical')}
                    className={`py-2 px-3 rounded text-sm transition-all ${
                      orientation === 'vertical'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    ⬇️ Vertical
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  💡 Presiona <kbd className="px-1 bg-gray-700 rounded">R</kbd> para rotar
                </p>
              </div>

              {/* Barcos colocados */}
              {placedShips.length > 0 && (
                <div className="pt-4 border-t border-gray-700">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Colocados</h4>
                  <div className="space-y-1">
                    {placedShips.map((ship, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between text-xs bg-gray-700 p-2 rounded"
                      >
                        <span className="text-green-400">✓ {ship.name || 'Barco'}</span>
                        <span className="text-gray-400">
                          {ship.coordinates?.[0]}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Panel derecho: Tablero */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-bold text-white mb-3">Tablero de Juego</h4>
              
              {/* Tablero */}
              <div className="inline-block bg-gray-900 p-4 rounded-lg">
                {/* Encabezado de columnas */}
                <div className="grid gap-1 mb-1" style={{ gridTemplateColumns: `40px repeat(${boardSize}, 40px)` }}>
                  <div></div>
                  {Array.from({ length: boardSize }, (_, i) => (
                    <div key={i} className="w-10 h-8 flex items-center justify-center text-gray-400 text-sm font-bold">
                      {i + 1}
                    </div>
                  ))}
                </div>

                {/* Filas del tablero */}
                {Array.from({ length: boardSize }, (_, rowIndex) => (
                  <div key={rowIndex} className="grid gap-1 mb-1" style={{ gridTemplateColumns: `40px repeat(${boardSize}, 40px)` }}>
                    {/* Etiqueta de fila */}
                    <div className="w-10 h-10 flex items-center justify-center text-gray-400 text-sm font-bold">
                      {String.fromCharCode(65 + rowIndex)}
                    </div>
                    
                    {/* Celdas */}
                    {Array.from({ length: boardSize }, (_, colIndex) => {
                      const cell = board.find(c => c.row === rowIndex && c.col === colIndex);
                      return (
                        <div
                          key={colIndex}
                          onDragOver={(e) => handleDragOver(e, cell)}
                          onDrop={(e) => handleDrop(e, cell)}
                          className="w-10 h-10 border border-gray-600 rounded"
                        >
                          <div className={getCellClass(cell)}>
                            {getCellContent(cell)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

              {/* Leyenda */}
              <div className="mt-4 flex gap-4 text-xs text-gray-400">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-gray-700 rounded"></div>
                  <span>Vacío</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span>Preview</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-600 rounded"></div>
                  <span>Ocupado</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShipPlacementDragDrop;
