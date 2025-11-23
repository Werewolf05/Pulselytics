export default function KPICard({ title, value, change, icon: Icon }) {
  const isPositive = change >= 0;

  return (
    <div className="card hover:shadow-2xl transition-all duration-300">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mt-2">{value}</p>
          {change !== undefined && (
            <p className={`text-sm mt-2 font-medium ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
              {isPositive ? '↑' : '↓'} {Math.abs(change)}%
            </p>
          )}
        </div>
        {Icon && (
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center shadow-sm">
            <Icon className="text-purple-600" size={24} />
          </div>
        )}
      </div>
    </div>
  );
}
