import { useState, useEffect } from 'react';
import { ThumbsUp, MessageCircle, Share2, Eye, TrendingUp, Filter, ExternalLink, Download } from 'lucide-react';
import { getAnalytics } from '../services/api';
import { exportToCSV, exportToJSON, formatDataForExport } from '../utils/exportData';
import { useToast } from '../components/ToastContainer';

const platformIcons = {
  instagram: '📸',
  facebook: '📘',
  twitter: '🐦',
  youtube: '📺'
};

const platformColors = {
  instagram: 'bg-gradient-to-r from-purple-500 to-pink-500',
  facebook: 'bg-blue-600',
  twitter: 'bg-sky-500',
  youtube: 'bg-red-600'
};

export default function TopPosts({ selectedClient, dateRange, selectedPlatform = 'all', searchQuery = '' }) {
  const { success, error } = useToast();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('engagement');
  const [platformFilter, setPlatformFilter] = useState(selectedPlatform);

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      try {
        const result = await getAnalytics({
          client: selectedClient,
          range: dateRange,
          platform: platformFilter,
          search: searchQuery
        });
        setPosts(result.top_posts || []);
      } catch (err) {
        console.error('Error fetching top posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [selectedClient, dateRange, platformFilter, searchQuery]);

  useEffect(() => {
    setPlatformFilter(selectedPlatform);
  }, [selectedPlatform]);

  const getSortedPosts = () => {
    return [...posts].sort((a, b) => {
      switch (sortBy) {
        case 'engagement':
          return b.engagement - a.engagement;
        case 'likes':
          return b.likes - a.likes;
        case 'comments':
          return b.comments - a.comments;
        case 'shares':
          return (b.shares || 0) - (a.shares || 0);
        case 'date':
          return new Date(b.date) - new Date(a.date);
        default:
          return 0;
      }
    });
  };

  const handleExport = (format) => {
    try {
      const sortedData = getSortedPosts();
      const filename = `top-posts-${selectedClient || 'all'}-${dateRange}-${Date.now()}.${format}`;
      
      if (format === 'csv') {
        const csvData = formatDataForExport(sortedData, 'csv');
        exportToCSV(csvData, filename);
        success(`Exported ${sortedData.length} posts to CSV`);
      } else if (format === 'json') {
        exportToJSON(sortedData, filename);
        success(`Exported ${sortedData.length} posts to JSON`);
      }
    } catch (err) {
      error('Failed to export data: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const sortedPosts = getSortedPosts();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Top Posts</h2>
          <p className="text-slate-600 mt-1">Best performing content across platforms</p>
        </div>

        <div className="flex items-center gap-4">
          {/* Export dropdown */}
          <div className="relative group">
            <button className="btn btn-secondary flex items-center gap-2">
              <Download size={16} />
              Export
            </button>
            <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-xl border border-slate-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button 
                onClick={() => handleExport('csv')}
                className="w-full px-4 py-2 text-left hover:bg-slate-50 rounded-t-lg text-sm"
              >
                Export as CSV
              </button>
              <button 
                onClick={() => handleExport('json')}
                className="w-full px-4 py-2 text-left hover:bg-slate-50 rounded-b-lg text-sm"
              >
                Export as JSON
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Filter size={16} className="text-slate-600" />
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Platforms</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="twitter">Twitter</option>
              <option value="youtube">YouTube</option>
            </select>
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="engagement">Total Engagement</option>
            <option value="likes">Likes</option>
            <option value="comments">Comments</option>
            <option value="shares">Shares</option>
            <option value="date">Date Posted</option>
          </select>
        </div>
      </div>

      {sortedPosts.length === 0 ? (
        <div className="card">
          <p className="text-slate-600 text-center py-8">No posts found. Run scrapers to populate data.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sortedPosts.map((post, index) => (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              {/* Platform Badge */}
              <div className="flex items-center justify-between mb-4">
                <span className={`${platformColors[post.platform] || 'bg-slate-600'} text-white px-3 py-1 rounded-full text-sm flex items-center gap-2`}>
                  <span>{platformIcons[post.platform] || '📱'}</span>
                  {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                </span>
                <span className="text-slate-400 text-sm">
                  {new Date(post.date).toLocaleDateString()}
                </span>
              </div>

              {/* Post Content / Media */}
              <div className="mb-4">
                {post.thumbnail_url && (
                  <img
                    src={post.thumbnail_url}
                    alt="thumbnail"
                    className="w-full h-40 object-cover rounded-lg mb-3"
                    onError={(e) => {
                      const el = e.currentTarget;
                      const src = el.src;
                      // If maxresdefault fails, try hqdefault once
                      if (src.includes('maxresdefault.jpg') && !el.dataset.fallbackTried) {
                        el.dataset.fallbackTried = '1';
                        el.src = src.replace('maxresdefault.jpg', 'hqdefault.jpg');
                        return;
                      }
                      // Final placeholder
                      el.src = '/placeholder-video.svg';
                    }}
                  />
                )}
                <p className="text-slate-800 line-clamp-3 mb-2">
                  {post.content || post.caption || post.title || 'No content available'}
                </p>
                {post.username && (
                  <p className="text-sm text-slate-600">by @{post.username}</p>
                )}
              </div>

              {/* Engagement Metrics */}
              <div className="grid grid-cols-4 gap-4 mb-4 pb-4 border-b border-slate-200">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-slate-600 mb-1">
                    <ThumbsUp size={16} />
                  </div>
                  <p className="text-lg font-bold text-slate-900">{post.likes?.toLocaleString() || 0}</p>
                  <p className="text-xs text-slate-500">Likes</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-slate-600 mb-1">
                    <MessageCircle size={16} />
                  </div>
                  <p className="text-lg font-bold text-slate-900">{post.comments?.toLocaleString() || 0}</p>
                  <p className="text-xs text-slate-500">Comments</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-slate-600 mb-1">
                    <Share2 size={16} />
                  </div>
                  <p className="text-lg font-bold text-slate-900">{(post.shares || post.retweets || 0).toLocaleString()}</p>
                  <p className="text-xs text-slate-500">Shares</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-slate-600 mb-1">
                    <Eye size={16} />
                  </div>
                  <p className="text-lg font-bold text-slate-900">{(post.views || 0).toLocaleString()}</p>
                  <p className="text-xs text-slate-500">Views</p>
                </div>
              </div>

              {/* Total Engagement */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="text-primary" size={16} />
                  <span className="text-sm text-slate-600">Total Engagement:</span>
                  <span className="text-sm font-bold text-primary">{post.engagement?.toLocaleString() || 0}</span>
                </div>
                {post.url && (
                  <a 
                    href={post.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:text-primary/80 flex items-center gap-1 text-sm"
                  >
                    View Post <ExternalLink size={14} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
