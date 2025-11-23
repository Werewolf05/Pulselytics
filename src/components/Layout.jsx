import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Home, BarChart3, TrendingUp, FileText, Settings, Menu, Search, Zap, Key, Brain } from 'lucide-react';
import { getClients, getScraperStatus } from '../services/api';
import DarkModeToggle from './DarkModeToggle';

export default function Layout({ 
  children, 
  selectedClient, 
  setSelectedClient, 
  dateRange, 
  setDateRange,
  selectedPlatform,
  setSelectedPlatform,
  searchQuery,
  setSearchQuery
}) {
  const location = useLocation();
  const [clients, setClients] = useState([]);
  const [scraperMode, setScraperMode] = useState('lightweight');

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'AI Predictions', href: '/predictive', icon: Brain },
    { name: 'Top Posts', href: '/top-posts', icon: TrendingUp },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'API Keys', href: '/api-keys', icon: Key },
  ];

  // Load clients on mount
  useEffect(() => {
    const loadClients = async () => {
      const data = await getClients();
      setClients(data);
    };
    loadClients();
  }, []);

  // Load scraper status
  useEffect(() => {
    const loadScraperStatus = async () => {
      try {
        const status = await getScraperStatus();
        setScraperMode(status.scraper_mode || 'lightweight');
      } catch (error) {
        console.error('Failed to load scraper status:', error);
      }
    };
    loadScraperStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-indigo-950 via-purple-950 to-indigo-950 text-white shadow-2xl">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-6 border-b border-purple-700/30">
            <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-xl shadow-lg">
              P
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Pulselytics</h1>
              <p className="text-xs text-purple-300">Social Analytics</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-lg scale-105'
                      : 'text-purple-200 hover:bg-purple-900/30 hover:text-white hover:scale-105'
                  }`}
                >
                  <Icon size={20} className={isActive ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'} />
                  <span className="font-medium">{item.name}</span>
                  {isActive && (
                    <div className="ml-auto w-2 h-2 rounded-full bg-white animate-pulse"></div>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-slate-700">
            <p className="text-xs text-slate-400"> 2025 Pulselytics</p>
            <p className="text-xs text-slate-500">Built for professionals</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-white/90 backdrop-blur-xl border-b border-purple-200/50 sticky top-0 z-10 shadow-lg">
          <div className="px-8 py-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 flex-1">
                {/* Client Selector */}
                <select
                  value={selectedClient}
                  onChange={(e) => setSelectedClient(e.target.value)}
                  className="px-4 py-2.5 border-2 border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent min-w-[200px] bg-white shadow-sm hover:border-purple-400 transition-all"
                >
                  <option value="">🌍 All Clients</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      📊 {client.name}
                    </option>
                  ))}
                </select>

                {/* Platform Filter */}
                <select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  className="px-4 py-2.5 border-2 border-purple-200 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-slate-700 dark:text-slate-200 shadow-sm hover:border-purple-400 transition-all"
                >
                  <option value="all">🌐 All Platforms</option>
                  <option value="instagram">📸 Instagram</option>
                  <option value="facebook">👍 Facebook</option>
                  <option value="youtube">🎥 YouTube</option>
                  <option value="twitter">🐦 Twitter/X</option>
                </select>

                {/* Date Range */}
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="px-4 py-2.5 border-2 border-purple-200 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-slate-700 dark:text-slate-200 shadow-sm hover:border-purple-400 transition-all"
                >
                  <option value="7days">📅 Last 7 Days</option>
                  <option value="30days">📅 Last 30 Days</option>
                  <option value="90days">📅 Last 90 Days</option>
                  <option value="all">📅 All Time</option>
                </select>

                {/* Search */}
                <div className="relative flex-1 max-w-md">
                  <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-400" />
                  <input
                    type="text"
                    placeholder="🔍 Search posts, hashtags..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border-2 border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white shadow-sm hover:border-purple-400 transition-all"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                {/* Dark Mode Toggle */}
                <DarkModeToggle />
                
                {/* Scraper Mode Badge */}
                {scraperMode === 'lightweight' && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-100 to-green-100 dark:from-emerald-900 dark:to-green-900 text-emerald-700 dark:text-emerald-300 rounded-xl text-sm font-medium shadow-sm border border-emerald-200 dark:border-emerald-700">
                    <Zap size={16} className="animate-pulse" />
                    <span>⚡ Fast Mode</span>
                  </div>
                )}
                
                {/* Export Button */}
                <button className="btn btn-secondary hover:scale-105 active:scale-95">
                  📥 Export
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
