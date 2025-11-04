const Cell = ({ coordinate, status, onClick, disabled = false, showShip = false, size = 'w-8 h-8', highlight = false }) => {
  // Estados posibles:
  // - 'empty': Celda vacía (agua)
  // - 'ship': Tiene barco (solo visible si showShip=true)
  // - 'hit': Barco impactado
  // - 'sunk': Barco hundido
  // - 'miss': Disparo al agua

  const getCellClasses = () => {
    const baseClasses = `${size} border border-gray-600 rounded transition-all flex items-center justify-center`;
    
    switch (status) {
      case 'ship':
        return `${baseClasses} ${showShip ? 'bg-blue-600' : 'bg-blue-900'}`;
      case 'hit':
        return `${baseClasses} bg-red-600`;
      case 'sunk':
        return `${baseClasses} bg-red-900`;
      case 'miss':
        return `${baseClasses} bg-gray-700`;
      default:
        return `${baseClasses} bg-blue-900 hover:bg-blue-800`;
    }
  };

  const getCellContent = () => {
    switch (status) {
      case 'hit':
        return <span className="text-white font-bold text-sm">💥</span>;
      case 'sunk':
        return <span className="text-white font-bold text-sm">☠️</span>;
      case 'miss':
        return <span className="text-blue-300 text-sm">💧</span>;
      case 'ship':
        return showShip ? <span className="text-white text-sm">🚢</span> : null;
      default:
        return null;
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || status === 'hit' || status === 'miss'}
      className={`${getCellClasses()} ${
        disabled || status === 'hit' || status === 'miss' ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-105'
      } ${highlight ? 'ring-4 ring-yellow-400 ring-opacity-75 animate-pulse' : ''}`}
      title={coordinate}
    >
      {getCellContent()}
    </button>
  );
};

export default Cell;
