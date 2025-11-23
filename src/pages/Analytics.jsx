import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { TrendingUp, Hash, Calendar, Image, Video, FileText, Download, RefreshCw, Clock, Target, Award, Zap, Users, ThumbsUp, Eye, MessageCircle } from 'lucide-react';
import { getAnalytics, getMLModelStatus } from '../services/api';
import { exportToCSV, exportToJSON } from '../utils/exportData';
import { useToast } from '../components/ToastContainer';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ChartTooltip from '../components/ChartTooltip';
import AIInsights from '../components/AIInsights';

export default function Analytics({ selectedClient, dateRange, selectedPlatform, searchQuery }) {
  const { success, error } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState('overview'); // overview, engagement, content, timing, insights
  const [mlStatus, setMlStatus] = useState(null);
  const [mlLoading, setMlLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
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
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedClient, dateRange, selectedPlatform, searchQuery]);

  useEffect(() => {
    const fetchStatus = async () => {
      setMlLoading(true);
      try {
        const status = await getMLModelStatus();
        setMlStatus(status);
      } catch (err) {
        console.warn('Failed to fetch ML status', err);
      } finally {
        setMlLoading(false);
      }
    };
    fetchStatus();
  }, []);

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
      success('Analytics refreshed successfully!');
    } catch (err) {
      error('Failed to refresh analytics');
    } finally {
      setRefreshing(false);
    }
  };

  const handleExport = (format) => {
    try {
      const exportData = {
        summary: {
          total_posts: data.total_posts,
          avg_likes: data.avg_likes,
          avg_comments: data.avg_comments,
          avg_views: data.avg_views,
          engagement_rate: calculateEngagementRate(),
        },
        platforms: data.platforms || [],
        top_posts: data.top_posts || [],
        hashtags: data.hashtags || [],
        trend: data.trend || [],
      };

      const filename = `analytics-${selectedClient || 'all'}-${dateRange}-${Date.now()}.${format}`;
      
      if (format === 'csv') {
        // Export top posts as CSV
        exportToCSV(data.top_posts || [], filename);
        success(`Exported ${(data.top_posts || []).length} posts to CSV`);
      } else if (format === 'json') {
        exportToJSON(exportData, filename);
        success('Exported complete analytics to JSON');
      }
    } catch (err) {
      error('Failed to export: ' + err.message);
    }
  };

  // Calculate advanced metrics
  const calculateEngagementRate = () => {
    if (!data || !data.total_posts) return 0;
    const totalEngagement = (data.avg_likes || 0) + (data.avg_comments || 0);
    const avgViews = data.avg_views || 1;
    return ((totalEngagement / avgViews) * 100).toFixed(2);
  };

  const calculateGrowthRate = () => {
    if (!data || !data.trend || data.trend.length < 2) return 0;
    const recent = data.trend.slice(-7);
    const older = data.trend.slice(0, 7);
    
    const recentAvg = recent.reduce((sum, d) => sum + (d.engagement || 0), 0) / recent.length;
    const olderAvg = older.reduce((sum, d) => sum + (d.engagement || 0), 0) / older.length;
    
    if (olderAvg === 0) return 0;
    return (((recentAvg - olderAvg) / olderAvg) * 100).toFixed(1);
  };

  const getBestPostingTimes = () => {
    if (!data || !data.top_posts) return [];
    
    const timeDistribution = {};
    data.top_posts.forEach(post => {
      // Backend returns upload_date; also support 'date' defensively
      const ts = post.upload_date || post.date;
      if (ts) {
        const hour = new Date(ts).getHours();
        const engagement = Number(post.engagement || 0);
        timeDistribution[hour] = (timeDistribution[hour] || 0) + engagement;
      }
    });

    return Object.entries(timeDistribution)
      .map(([hour, engagement]) => ({
        hour: `${hour}:00`,
        engagement,
        label: `${hour}:00 - ${parseInt(hour) + 1}:00`
      }))
      .sort((a, b) => b.engagement - a.engagement)
      .slice(0, 8);
  };

  const getContentPerformance = () => {
    if (!data || !data.top_posts) return [];
    
    const performance = {
      'High Engagement': 0,
      'Medium Engagement': 0,
      'Low Engagement': 0,
    };

    const avgEngagement = data.avg_likes + data.avg_comments;
    
    data.top_posts.forEach(post => {
      if (post.engagement > avgEngagement * 1.5) {
        performance['High Engagement']++;
      } else if (post.engagement > avgEngagement * 0.5) {
        performance['Medium Engagement']++;
      } else {
        performance['Low Engagement']++;
      }
    });

    return Object.entries(performance).map(([name, value]) => ({ name, value }));
  };

  const getPlatformComparison = () => {
    if (!data || !data.platforms) return [];
    
    return data.platforms.map(platform => ({
      platform: platform.platform,
      'Avg Engagement': platform.avg_engagement || 0,
      'Total Posts': platform.posts || 0,
      'Engagement Rate': ((platform.avg_engagement || 0) / (platform.avg_views || 1) * 100).toFixed(1),
    }));
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Advanced Analytics</h2>
          <p className="text-slate-600 mt-1">Loading comprehensive insights...</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <LoadingSkeleton key={i} type="card" />
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LoadingSkeleton type="card" />
          <LoadingSkeleton type="card" />
        </div>
      </div>
    );
  }

  if (!data || data.total_posts === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Advanced Analytics</h2>
          <p className="text-slate-600 mt-2">Comprehensive insights across all platforms</p>
        </div>
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">No Data Available</h3>
          <p className="text-slate-600">Run scrapers from the Settings page to populate analytics.</p>
        </div>
      </div>
    );
  }

  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];
  const engagementRate = calculateEngagementRate();
  const growthRate = calculateGrowthRate();
  const bestTimes = getBestPostingTimes();
  const contentPerformance = getContentPerformance();
  const platformComparison = getPlatformComparison();

  // Prepare sentiment data for pie chart
  const sentimentData = [
    { name: 'Positive', value: data.sentiment?.positive || 0, color: '#10b981' },
    { name: 'Neutral', value: data.sentiment?.neutral || 0, color: '#8b5cf6' },
    { name: 'Negative', value: data.sentiment?.negative || 0, color: '#ef4444' }
  ].filter(item => item.value > 0);

  // Prepare content type data
  const contentTypeData = Object.entries(data.content_types || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  return (
    <div className="space-y-8">
      {/* Header with Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Advanced Analytics</h2>
          <p className="text-slate-600 mt-2">Comprehensive insights and performance metrics</p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* AI Status quick glance */}
          <div className="hidden md:flex items-center gap-3 px-3 py-2 rounded-lg border border-purple-200 bg-purple-50">
            <span className="text-xs font-semibold text-purple-700">AI Status</span>
            <span className={`text-xs px-2 py-1 rounded-full ${mlStatus?.predictor?.loaded ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'}`} title={`Predictor v${mlStatus?.predictor?.version || '—'}`}>Predictor {mlStatus?.predictor?.loaded ? 'Ready' : 'Idle'}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${mlStatus?.anomaly_detector?.loaded ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'}`} title={`Anomaly v${mlStatus?.anomaly_detector?.version || '—'}`}>Anomaly {mlStatus?.anomaly_detector?.loaded ? 'Ready' : 'Idle'}</span>
          </div>
          {/* Export Dropdown */}
          <div className="relative group">
            <button className="btn btn-secondary flex items-center gap-2">
              <Download size={16} />
              Export
            </button>
            <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-xl border border-purple-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button 
                onClick={() => handleExport('csv')}
                className="w-full px-4 py-2 text-left hover:bg-purple-50 rounded-t-lg text-sm"
              >
                Export as CSV
              </button>
              <button 
                onClick={() => handleExport('json')}
                className="w-full px-4 py-2 text-left hover:bg-purple-50 rounded-b-lg text-sm"
              >
                Export as JSON
              </button>
            </div>
          </div>

          {/* Refresh Button */}
          <button 
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex gap-2 border-b border-purple-200">
        <button
          onClick={() => setViewMode('overview')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            viewMode === 'overview'
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-slate-600 hover:text-purple-600'
          }`}
        >
          📊 Overview
        </button>
        <button
          onClick={() => setViewMode('engagement')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            viewMode === 'engagement'
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-slate-600 hover:text-purple-600'
          }`}
        >
          💬 Engagement
        </button>
        <button
          onClick={() => setViewMode('content')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            viewMode === 'content'
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-slate-600 hover:text-purple-600'
          }`}
        >
          📝 Content
        </button>
        <button
          onClick={() => setViewMode('timing')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            viewMode === 'timing'
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-slate-600 hover:text-purple-600'
          }`}
        >
          ⏰ Timing
        </button>
        <button
          onClick={() => setViewMode('insights')}
          className={`px-4 py-2 font-medium transition-colors border-b-2 ${
            viewMode === 'insights'
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-slate-600 hover:text-purple-600'
          }`}
        >
          ✨ AI Insights
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-indigo-50 to-indigo-100 border-indigo-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-indigo-600 mb-1" title="(Likes + Comments) / Views × 100">Engagement Rate</p>
              <h3 className="text-3xl font-bold text-indigo-900">{engagementRate}%</h3>
              <p className="text-xs text-indigo-600 mt-1">Likes + Comments / Views</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg shadow-lg">
              <Target className="text-white" size={24} />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-emerald-600 mb-1" title="Average engagement of last 7 days vs previous 7 days">Growth Rate</p>
              <h3 className="text-3xl font-bold text-emerald-900">{growthRate}%</h3>
              <p className="text-xs text-emerald-600 mt-1">Last 7 days vs previous</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-emerald-500 to-green-500 rounded-lg shadow-lg">
              <TrendingUp className="text-white" size={24} />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-fuchsia-100 border-purple-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 mb-1">Total Posts</p>
              <h3 className="text-3xl font-bold text-purple-900">{data.total_posts}</h3>
              <p className="text-xs text-purple-600 mt-1">Across all platforms</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg shadow-lg">
              <FileText className="text-white" size={24} />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-amber-50 to-orange-100 border-amber-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-amber-600 mb-1" title="Hour with highest historical engagement">Best Time</p>
              <h3 className="text-3xl font-bold text-amber-900">
                {bestTimes[0]?.hour || 'N/A'}
              </h3>
              <p className="text-xs text-amber-600 mt-1">Peak engagement hour</p>
            </div>
            <div className="p-3 bg-gradient-to-br from-amber-500 to-orange-500 rounded-lg shadow-lg">
              <Clock className="text-white" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* AI Intelligence Status Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-1">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Award className="text-primary" size={20} />
              <h3 className="text-lg font-bold text-slate-900">AI Intelligence Status</h3>
            </div>
            <button
              onClick={async () => { setMlLoading(true); try { const s = await getMLModelStatus(); setMlStatus(s);} finally { setMlLoading(false);} }}
              className="text-sm text-purple-600 hover:underline"
              disabled={mlLoading}
            >{mlLoading ? 'Refreshing…' : 'Refresh'}</button>
          </div>
          {mlStatus ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Predictor</span>
                <span className={`text-xs px-2 py-1 rounded-full ${mlStatus?.predictor?.loaded ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{mlStatus?.predictor?.loaded ? 'Ready' : 'Idle'}</span>
              </div>
              <div className="text-xs text-slate-500">v{mlStatus?.predictor?.version || '—'} • trained: {mlStatus?.predictor?.trained_on || '—'} • samples: {mlStatus?.predictor?.samples_trained || '—'}</div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Anomaly Detector</span>
                <span className={`text-xs px-2 py-1 rounded-full ${mlStatus?.anomaly_detector?.loaded ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{mlStatus?.anomaly_detector?.loaded ? 'Ready' : 'Idle'}</span>
              </div>
              <div className="text-xs text-slate-500">v{mlStatus?.anomaly_detector?.version || '—'} • trained: {mlStatus?.anomaly_detector?.trained_on || '—'} • samples: {mlStatus?.anomaly_detector?.samples_trained || '—'}</div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">{mlLoading ? 'Loading status…' : 'Status unavailable'}</p>
          )}
        </div>
      </div>

      {/* Overview Tab */}
      {viewMode === 'overview' && (
        <>
          {/* Sentiment Analysis & Content Type */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Sentiment Analysis</h3>
              </div>
              {sentimentData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      cornerRadius={8}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<ChartTooltip />} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-slate-400 text-center py-8">No sentiment data available</p>
              )}
            </div>

            {/* Content Type Distribution */}
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Image className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Content Type Distribution</h3>
              </div>
              {contentTypeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={contentTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      cornerRadius={8}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {contentTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<ChartTooltip />} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-slate-400 text-center py-8">No content type data available</p>
              )}
            </div>
          </div>

          {/* Platform Performance Comparison */}
          {platformComparison.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Award className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Platform Performance Comparison</h3>
              </div>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={platformComparison}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="platform" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend />
                  <Bar dataKey="Avg Engagement" fill="#06b6d4" radius={[10, 10, 10, 10]} />
                  <Bar dataKey="Total Posts" fill="#8b5cf6" radius={[10, 10, 10, 10]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {/* Engagement Tab */}
      {viewMode === 'engagement' && (
        <>
          {/* Engagement Over Time */}
          {data.trend && data.trend.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Engagement Trend</h3>
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={data.trend}>
                  <defs>
                    <linearGradient id="colorEngagement" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="#3b82f6"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorEngagement)"
                    name="Total Engagement"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Content Performance Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Target className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Content Performance</h3>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={contentPerformance}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    cornerRadius={8}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {contentPerformance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Top Performing Metrics */}
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Award className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Top Performing Metrics</h3>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-transparent rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500 rounded-lg">
                      <ThumbsUp className="text-white" size={20} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600">Avg Likes</p>
                      <p className="text-2xl font-bold text-slate-900">{(data.avg_likes || 0).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-transparent rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-500 rounded-lg">
                      <MessageCircle className="text-white" size={20} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600">Avg Comments</p>
                      <p className="text-2xl font-bold text-slate-900">{(data.avg_comments || 0).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-transparent rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-500 rounded-lg">
                      <Eye className="text-white" size={20} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600">Avg Views</p>
                      <p className="text-2xl font-bold text-slate-900">{(data.avg_views || 0).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Content Tab */}
      {viewMode === 'content' && (
        <>
          {/* Top Hashtags */}
          {data.hashtags && data.hashtags.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Hash className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Top Hashtags</h3>
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={data.hashtags.slice(0, 15)} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis dataKey="hashtag" type="category" stroke="#64748b" width={150} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[0, 12, 12, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Content Type Deep Dive */}
          {contentTypeData.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Video className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Content Type Performance</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {contentTypeData.map((type, index) => (
                  <div 
                    key={type.name}
                    className="p-4 rounded-xl border-2 transition-all hover:shadow-lg"
                    style={{ borderColor: COLORS[index % COLORS.length] + '40' }}
                  >
                    <div 
                      className="w-12 h-12 rounded-lg flex items-center justify-center mb-3"
                      style={{ backgroundColor: COLORS[index % COLORS.length] + '20' }}
                    >
                      <span className="text-2xl">{type.name === 'Video' ? '🎬' : type.name === 'Image' ? '🖼️' : type.name === 'Text' ? '📝' : '📄'}</span>
                    </div>
                    <p className="text-sm font-medium text-slate-600">{type.name}</p>
                    <p className="text-2xl font-bold text-slate-900">{type.value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Timing Tab */}
      {viewMode === 'timing' && (
        <>
          {/* Best Posting Times */}
          {bestTimes.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Best Posting Times</h3>
                <span className="text-sm text-slate-500">(by engagement)</span>
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={bestTimes}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="label" stroke="#64748b" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#64748b" />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="engagement" fill="#f59e0b" radius={[10, 10, 10, 10]} name="Engagement Score" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <p className="text-sm text-orange-800">
                  <strong>💡 Tip:</strong> Schedule your posts during peak hours ({bestTimes[0]?.label} - {bestTimes[2]?.label}) for maximum engagement.
                </p>
              </div>
            </div>
          )}

          {/* Posting Pattern Calendar */}
          {data.trend && data.trend.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="text-primary" size={20} />
                <h3 className="text-lg font-bold text-slate-900">Posting Activity Pattern</h3>
              </div>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={data.trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="posts" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    name="Posts Published"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    name="Total Engagement"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* AI Insights Section in Overview */}
          {viewMode === 'overview' && data && (
            <div className="mt-8">
              <AIInsights clientId={selectedClient} dateRange={dateRange} />
            </div>
          )}
        </>
      )}

      {/* AI Insights Tab */}
      {viewMode === 'insights' && !loading && (
        <div className="mt-6">
          <AIInsights clientId={selectedClient} dateRange={dateRange} />
        </div>
      )}
    </div>
  );
}
