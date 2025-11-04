import { useEffect } from 'react';

const Notification = ({ notification, onClose }) => {
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(onClose, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification, onClose]);

  if (!notification) return null;

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
  }[notification.type];

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in">
      <div className={`${bgColor} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3`}>
        <span>{notification.message}</span>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 font-bold"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default Notification;
