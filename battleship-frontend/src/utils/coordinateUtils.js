/**
 * Convierte coordenada de string a índices de array
 * Ejemplo: "A1" -> [0, 0], "B3" -> [1, 2]
 */
export const coordinateToIndices = (coordinate) => {
  const letter = coordinate[0].toUpperCase();
  const number = parseInt(coordinate.slice(1));
  
  const row = letter.charCodeAt(0) - 'A'.charCodeAt(0);
  const col = number - 1;
  
  return [row, col];
};

/**
 * Convierte índices de array a coordenada string
 * Ejemplo: [0, 0] -> "A1", [1, 2] -> "B3"
 */
export const indicesToCoordinate = (row, col) => {
  const letter = String.fromCharCode('A'.charCodeAt(0) + row);
  const number = col + 1;
  
  return `${letter}${number}`;
};

/**
 * Valida formato de coordenada
 * Ejemplo: "A1" -> true, "Z99" -> false (depende del boardSize)
 */
export const isValidCoordinate = (coordinate, boardSize = 10) => {
  const regex = /^[A-Z]\d+$/;
  if (!regex.test(coordinate)) return false;
  
  const [row, col] = coordinateToIndices(coordinate);
  
  return row >= 0 && row < boardSize && col >= 0 && col < boardSize;
};

/**
 * Genera array de coordenadas para un barco
 * Ejemplo: ("A1", 3, "horizontal") -> ["A1", "A2", "A3"]
 */
export const generateShipCoordinates = (start, size, orientation) => {
  const [startRow, startCol] = coordinateToIndices(start);
  const coordinates = [];
  
  for (let i = 0; i < size; i++) {
    if (orientation === 'horizontal') {
      coordinates.push(indicesToCoordinate(startRow, startCol + i));
    } else {
      coordinates.push(indicesToCoordinate(startRow + i, startCol));
    }
  }
  
  return coordinates;
};

/**
 * Verifica si las coordenadas están dentro del tablero
 */
export const areCoordinatesInBounds = (coordinates, boardSize = 10) => {
  return coordinates.every(coord => isValidCoordinate(coord, boardSize));
};
