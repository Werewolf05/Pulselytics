import { useState, useEffect } from 'react';
import { Heart, MessageCircle, Eye, FileText, TrendingUp, RefreshCw } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from 'recharts';
import KPICard from '../components/KPICard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { getAnalytics } from '../services/api';
import { useToast } from '../components/ToastContainer';
import ChartTooltip from '../components/ChartTooltip';

export default function Overview({ selectedClient, dateRange, selectedPlatform, searchQuery }) {
  const { success } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getAnalytics({
          client: selectedClient,
          range: dateRange,
          platform: selectedPlatform || 'all',
          search: searchQuery || ''
        });
        setData(result);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedClient, dateRange, selectedPlatform, searchQuery]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const result = await getAnalytics({
        client: selectedClient,
        range: dateRange,
        platform: selectedPlatform || 'all',
        search: searchQuery || ''
      });
      setData(result);
      success('Data refreshed successfully!');
    } catch (err) {
      console.error('Error refreshing:', err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Dashboard Overview</h2>
          <p className="text-slate-600 mt-1">Loading your analytics...</p>
        </div>
        
        {/* KPI Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <LoadingSkeleton key={i} type="card" />
          ))}
        </div>
        
        {/* Charts Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LoadingSkeleton type="card" />
          <LoadingSkeleton type="card" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-red-500 text-lg font-semibold mb-2">Error</div>
          <p className="text-slate-500">{error}</p>
          <p className="text-sm text-slate-400 mt-2">Make sure the backend server is running</p>
        </div>
      </div>
    );
  }

  if (!data || data.total_posts === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <FileText size={48} className="text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 text-lg font-medium">No data available</p>
          <p className="text-sm text-slate-400 mt-2">Run scrapers to populate data</p>
        </div>
      </div>
    );
  }

  // Colors for charts
  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];

  return (
    <div className="space-y-8">
      {/* Header with Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Dashboard Overview</h2>
          <p className="text-slate-600 mt-1">Real-time social media analytics</p>
        </div>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Posts"
          value={data.total_posts || 0}
          icon={FileText}
          trend="up"
        />
        <KPICard
          title="Avg Likes"
          value={(data.avg_likes || 0).toFixed(1)}
          icon={Heart}
          trend="up"
        />
        <KPICard
          title="Avg Comments"
          value={(data.avg_comments || 0).toFixed(1)}
          icon={MessageCircle}
        />
        <KPICard
          title="Avg Views"
          value={(data.avg_views || 0).toLocaleString()}
          icon={Eye}
          trend="up"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engagement Trend */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Engagement Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.trend || []}>
              <defs>
                <linearGradient id="ovColorEngagement" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '12px' }} />
              <YAxis stroke="#64748b" />
              <Tooltip content={<ChartTooltip />} />
              <Area 
                type="monotone" 
                dataKey="engagement" 
                stroke="#6366f1"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#ovColorEngagement)"
                name="Total Engagement"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Platform Distribution */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Platform Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.platforms || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="platform" stroke="#64748b" style={{ fontSize: '12px' }} />
              <YAxis stroke="#64748b" />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="posts" fill="#06b6d4" radius={[10, 10, 10, 10]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Hashtags */}
      {data.hashtags && data.hashtags.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Top Hashtags</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.hashtags.slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" stroke="#64748b" />
              <YAxis dataKey="hashtag" type="category" stroke="#64748b" width={120} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="count" fill="#8b5cf6" radius={[0, 12, 12, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Posts */}
      <div className="card">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Top Performing Posts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data.top_posts || []).slice(0, 6).map((post, idx) => (
            <div 
              key={idx} 
              className="border border-slate-200 rounded-lg p-4 hover:shadow-lg transition-shadow duration-200 cursor-pointer"
            >
              {/* Platform Badge */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-700 capitalize">
                  {post.platform}
                </span>
                <span className="text-xs text-slate-400">@{post.username}</span>
              </div>
              
              {/* Media */}
              {post.media_url && (
                <img 
                  src={post.media_url} 
                  alt="" 
                  className="w-full h-40 object-cover rounded-lg mb-3"
                  onError={(e) => {
                    const el = e.currentTarget;
                    const src = el?.src || '';
                    // First fallback: use hqdefault if maxresdefault is missing
                    if (src.includes('maxresdefault.jpg') && !el.dataset.fallbackTried) {
                      el.dataset.fallbackTried = '1';
                      el.src = src.replace('maxresdefault.jpg', 'hqdefault.jpg');
                      return;
                    }
                    // Final fallback: show placeholder image from /public
                    el.src = '/placeholder-video.svg';
                  }}
                />
              )}
              
              {/* Caption */}
              <p className="text-sm text-slate-700 line-clamp-2 mb-3">{post.caption}</p>
              
              {/* Metrics */}
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <Heart size={14} className="text-red-400" />
                  {(post.likes || 0).toLocaleString()}
                </span>
                <span className="flex items-center gap-1">
                  <MessageCircle size={14} className="text-blue-400" />
                  {(post.comments || 0).toLocaleString()}
                </span>
                {post.views && (
                  <span className="flex items-center gap-1">
                    <Eye size={14} className="text-green-400" />
                    {(post.views).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {(!data.top_posts || data.top_posts.length === 0) && (
          <div className="text-center py-8 text-slate-400">
            No posts to display
          </div>
        )}
      </div>
    </div>
  );
}
