import { useEffect, useState } from 'react';

const ShotResult = ({ result, onClose }) => {
  const [visible, setVisible] = useState(true);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    // Iniciar animación
    setAnimating(true);
    
    // Duración más corta: 1.5 segundos
    const timer = setTimeout(() => {
      setAnimating(false);
      setTimeout(() => {
        setVisible(false);
        onClose?.();
      }, 300); // Tiempo para fade out
    }, 1500);

    return () => clearTimeout(timer);
  }, [result, onClose]);

  if (!result || !visible) return null;

  const getResultConfig = () => {
    switch (result.result) {
      case 'water':
        return {
          emoji: '💧',
          title: '¡Agua!',
          message: `${result.coordinate}`,
          color: 'from-blue-500 to-blue-600',
          textColor: 'text-blue-100',
          shadow: 'shadow-blue-500/50'
        };
      case 'hit':
        return {
          emoji: '💥',
          title: '¡Impacto!',
          message: `${result.ship_hit || 'Barco'} en ${result.coordinate}`,
          color: 'from-orange-500 to-red-500',
          textColor: 'text-orange-100',
          shadow: 'shadow-orange-500/50'
        };
      case 'sunk':
        return {
          emoji: '☠️',
          title: '¡HUNDIDO!',
          message: `${result.ship_hit} destruido`,
          color: 'from-red-600 to-red-800',
          textColor: 'text-red-100',
          shadow: 'shadow-red-500/50'
        };
      default:
        return null;
    }
  };

  const config = getResultConfig();
  if (!config) return null;

  return (
    <div className={`fixed inset-0 flex items-center justify-center z-50 pointer-events-none transition-opacity duration-300 ${animating ? 'opacity-100' : 'opacity-0'}`}>
      <div className={`bg-gradient-to-br ${config.color} text-white px-8 py-6 rounded-2xl shadow-2xl ${config.shadow} text-center transform transition-all duration-300 ${
        animating ? 'scale-100 translate-y-0' : 'scale-75 -translate-y-4'
      }`}>
        <div className="text-5xl mb-2 animate-pulse">{config.emoji}</div>
        <h3 className="text-2xl font-bold mb-1">{config.title}</h3>
        <p className={`text-sm ${config.textColor}`}>{config.message}</p>
      </div>
    </div>
  );
};

export default ShotResult;
