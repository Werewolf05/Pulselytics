import { useState } from 'react';
import { Lightbulb, Sparkles, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import { generateAIInsights, getContentRecommendations } from '../services/api';

const AIInsights = ({ clientId, dateRange = '30days' }) => {
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('insights');

  const loadInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateAIInsights(clientId, dateRange);
      if (data.success) {
        setInsights(data);
      } else {
        setError(data.error || 'Failed to generate insights');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getContentRecommendations(clientId);
      if (data.success) {
        setRecommendations(data);
      } else {
        setError(data.error || 'Failed to get recommendations');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (activeTab === 'insights') {
      loadInsights();
    } else {
      loadRecommendations();
    }
  };

  const renderInsights = () => {
    if (!insights) return null;

    return (
      <div className="space-y-6">
        {/* Key Insights */}
        {insights.key_insights && insights.key_insights.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 dark:text-gray-100">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              Key Insights
            </h3>
            <div className="space-y-2">
              {insights.key_insights.map((insight, idx) => (
                <div key={idx} className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trends */}
        {insights.trends && insights.trends.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 dark:text-gray-100">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Trends & Patterns
            </h3>
            <div className="space-y-2">
              {insights.trends.map((trend, idx) => (
                <div key={idx} className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300">{trend}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {insights.recommendations && insights.recommendations.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 dark:text-gray-100">
              <Sparkles className="w-5 h-5 text-purple-500" />
              Recommendations
            </h3>
            <div className="space-y-2">
              {insights.recommendations.map((rec, idx) => (
                <div key={idx} className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Warnings */}
        {insights.warnings && insights.warnings.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 dark:text-gray-100">
              <AlertCircle className="w-5 h-5 text-orange-500" />
              Areas of Concern
            </h3>
            <div className="space-y-2">
              {insights.warnings.map((warning, idx) => (
                <div key={idx} className="p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300">{warning}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Source indicator */}
        {insights.source && (
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-4 border-t border-gray-200 dark:border-gray-700">
            {insights.source === 'openai' ? (
              <span className="flex items-center justify-center gap-1">
                <Sparkles className="w-3 h-3" />
                Powered by AI
              </span>
            ) : (
              <span>Generated using analytics rules</span>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderRecommendations = () => {
    if (!recommendations) return null;

    return (
      <div className="space-y-6">
        <div className="prose dark:prose-invert max-w-none">
          <div className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
            {recommendations.recommendations}
          </div>
        </div>

        {/* Source indicator */}
        {recommendations.source && (
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-4 border-t border-gray-200 dark:border-gray-700">
            {recommendations.source === 'openai' ? (
              <span className="flex items-center justify-center gap-1">
                <Sparkles className="w-3 h-3" />
                Powered by AI
              </span>
            ) : (
              <span>General content recommendations</span>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-500" />
          AI-Powered Insights
        </h2>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => {
            setActiveTab('insights');
            if (!insights) loadInsights();
          }}
          className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'insights'
              ? 'border-purple-500 text-purple-600 dark:text-purple-400'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          Analytics Insights
        </button>
        <button
          onClick={() => {
            setActiveTab('recommendations');
            if (!recommendations) loadRecommendations();
          }}
          className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'recommendations'
              ? 'border-purple-500 text-purple-600 dark:text-purple-400'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          Content Strategy
        </button>
      </div>

      {/* Content */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
          <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <span>Generating insights...</span>
          </div>
        </div>
      )}

      {!loading && !error && (
        <div className="min-h-[200px]">
          {activeTab === 'insights' ? (
            insights ? renderInsights() : (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <Sparkles className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                <p>Click "Refresh" to generate AI insights</p>
              </div>
            )
          ) : (
            recommendations ? renderRecommendations() : (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <Lightbulb className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                <p>Click "Refresh" to get content recommendations</p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};

export default AIInsights;
