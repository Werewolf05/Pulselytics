const LoadingSkeleton = ({ type = 'card' }) => {
  if (type === 'card') {
    return (
      <div className="glass p-6 rounded-xl animate-pulse">
        <div className="h-4 bg-white/20 rounded w-1/3 mb-4"></div>
        <div className="h-8 bg-white/30 rounded w-2/3 mb-2"></div>
        <div className="h-3 bg-white/10 rounded w-1/2"></div>
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="glass rounded-xl overflow-hidden animate-pulse">
        <div className="h-12 bg-white/10 border-b border-white/10"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-white/5 border-b border-white/10"></div>
        ))}
      </div>
    );
  }

  if (type === 'stat') {
    return (
      <div className="animate-pulse">
        <div className="h-12 bg-gradient-to-r from-white/20 to-white/10 rounded-lg mb-2"></div>
        <div className="h-4 bg-white/10 rounded w-3/4"></div>
      </div>
    );
  }

  return (
    <div className="animate-pulse">
      <div className="h-4 bg-white/20 rounded w-full mb-2"></div>
      <div className="h-4 bg-white/20 rounded w-5/6"></div>
    </div>
  );
};

export default LoadingSkeleton;
