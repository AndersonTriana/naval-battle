import { indicesToCoordinate, coordinateToIndices } from '../../utils/coordinateUtils';
import Cell from './Cell';

const Board = ({
  size = 10,
  ships = [],
  shots = [],
  onCellClick = null,
  showShips = true,
  title = 'Tablero',
  disabled = false,
  highlightCoordinate = null
}) => {
  // Crear matriz del tablero con estado de cada celda
  const getBoardMatrix = () => {
    const matrix = Array(size).fill(null).map(() =>
      Array(size).fill({ status: 'empty' })
    );

    // Marcar celdas con barcos
    if (showShips) {
      ships.forEach(ship => {
        ship.coordinates?.forEach(coord => {
          const [row, col] = coordinateToIndices(coord);
          if (row >= 0 && row < size && col >= 0 && col < size) {
            matrix[row][col] = { 
              status: ship.segments?.find(s => s.coordinate === coord)?.is_hit ? 'hit' : 'ship',
              shipName: ship.name 
            };
          }
        });
      });
    }

    // Marcar disparos
    shots.forEach(shot => {
      const [row, col] = coordinateToIndices(shot.coordinate);
      if (row >= 0 && row < size && col >= 0 && col < size) {
        let status;
        if (shot.result === 'water') {
          status = 'miss';
        } else if (shot.result === 'sunk') {
          status = 'sunk';
        } else {
          status = 'hit';
        }
        
        matrix[row][col] = { 
          status: status,
          result: shot.result
        };
      }
    });

    return matrix;
  };

  const handleCellClick = (row, col) => {
    if (!onCellClick || disabled) return;
    const coordinate = indicesToCoordinate(row, col);
    onCellClick(coordinate);
  };

  const matrix = getBoardMatrix();

  // Generar letras de columnas (A, B, C, ...)
  const columnLabels = Array.from({ length: size }, (_, i) =>
    String.fromCharCode(65 + i)
  );

  // Calcular tamaño de celda basado en el tamaño del tablero
  const getCellSize = () => {
    if (size <= 10) return 'w-8 h-8'; // 32px para tableros pequeños
    if (size <= 15) return 'w-6 h-6'; // 24px para tableros medianos
    return 'w-5 h-5'; // 20px para tableros grandes
  };

  const cellSize = getCellSize();
  const cellSizeRem = size <= 10 ? '2rem' : size <= 15 ? '1.5rem' : '1.25rem';

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      {/* Título */}
      <h3 className="text-lg font-bold text-white mb-3">{title}</h3>

      <div className="inline-block bg-gray-900 p-3 rounded">
        {/* Encabezado de columnas (números) */}
        <div className="flex gap-0.5 mb-0.5" style={{ marginLeft: '1.5rem' }}>
          {Array.from({ length: size }, (_, i) => (
            <div
              key={i}
              className={`${cellSize} flex items-center justify-center text-gray-400 font-mono text-xs`}
            >
              {i + 1}
            </div>
          ))}
        </div>

        {/* Filas del tablero */}
        {matrix.map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-0.5 mb-0.5">
            {/* Etiqueta de fila (letra) */}
            <div className="w-6 flex items-center justify-center text-gray-400 font-mono text-xs">
              {columnLabels[rowIndex]}
            </div>
            
            {/* Celdas */}
            {row.map((cell, colIndex) => {
              const coordinate = indicesToCoordinate(rowIndex, colIndex);
              const isHighlighted = highlightCoordinate === coordinate;
              return (
                <Cell
                  key={coordinate}
                  coordinate={coordinate}
                  status={cell.status}
                  onClick={() => handleCellClick(rowIndex, colIndex)}
                  disabled={disabled}
                  showShip={showShips}
                  size={cellSize}
                  highlight={isHighlighted}
                />
              );
            })}
          </div>
        ))}
      </div>

      {/* Leyenda */}
      <div className="mt-3 flex gap-4 text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <div className="w-5 h-5 bg-blue-900 border border-gray-600 rounded"></div>
          <span>Agua</span>
        </div>
        {showShips && (
          <div className="flex items-center gap-1">
            <div className="w-5 h-5 bg-blue-600 border border-gray-600 rounded flex items-center justify-center">
              <span className="text-xs">🚢</span>
            </div>
            <span>Barco</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <div className="w-5 h-5 bg-red-600 border border-gray-600 rounded flex items-center justify-center">
            <span className="text-xs">💥</span>
          </div>
          <span>Impacto</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-5 h-5 bg-red-900 border border-gray-600 rounded flex items-center justify-center">
            <span className="text-xs">☠️</span>
          </div>
          <span>Hundido</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-5 h-5 bg-gray-700 border border-gray-600 rounded flex items-center justify-center">
            <span className="text-xs">💧</span>
          </div>
          <span>Agua (fallo)</span>
        </div>
      </div>
    </div>
  );
};

export default Board;
