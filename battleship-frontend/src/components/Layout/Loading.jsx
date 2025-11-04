const Loading = ({ message = 'Cargando...' }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
      <p className="mt-4 text-gray-400">{message}</p>
    </div>
  );
};

export default Loading;
