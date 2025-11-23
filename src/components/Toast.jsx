import { useEffect } from 'react';
import { X, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

const Toast = ({ message, type = 'info', onClose, duration = 4000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />
  };

  const colors = {
    success: 'bg-green-500/90',
    error: 'bg-red-500/90',
    warning: 'bg-yellow-500/90',
    info: 'bg-blue-500/90'
  };

  return (
    <div className={`${colors[type]} backdrop-blur-lg text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 min-w-[300px] max-w-md animate-slideIn`}>
      {icons[type]}
      <p className="flex-1 font-medium">{message}</p>
      <button 
        onClick={onClose}
        className="hover:bg-white/20 rounded p-1 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};

export default Toast;
