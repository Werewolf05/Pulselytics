import { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, Clock, Zap, Target } from 'lucide-react';
import { getClients, detectAnomalies } from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';

export default function PredictiveAnalytics() {
  const [loading, setLoading] = useState(false);
  const [selectedClient, setSelectedClient] = useState('');
  const [clients, setClients] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [optimalTime, setOptimalTime] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [postCaption, setPostCaption] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const data = await getClients();
      setClients(data);
      if (data.length > 0) {
        setSelectedClient(data[0].id);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const trainModels = async () => {
    if (!selectedClient) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ml/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
      });
      const data = await response.json();
      
      if (data.success) {
        setTrainingStatus(data);
        alert('✅ Analysis complete! Your data has been processed and insights are ready.');
      } else {
        alert(`⚠️ Analysis failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Error training models:', error);
      alert('⚠️ Failed to analyze data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const refreshModelStatus = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/ml/models/status');
      const data = await res.json();
      if (data.success) setModelStatus(data);
    } catch (e) {
      console.error('Error fetching model status', e);
    }
  };

  const predictEngagement = async () => {
    if (!postCaption) {
      alert('Please enter a caption to predict');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ml/predict/engagement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          caption: postCaption,
          platform: platform
        })
      });
      const data = await response.json();
      
      if (data.success) {
        setPrediction(data.prediction);
      }
    } catch (error) {
      console.error('Error predicting:', error);
    } finally {
      setLoading(false);
    }
  };

  const detectAnomaliesHandler = async () => {
    if (!selectedClient) return;
    setLoading(true);
    try {
      const result = await detectAnomalies(selectedClient);
      if (result.success) {
        setAnomalies(result);
      } else {
        alert(result.error || 'Failed to detect anomalies');
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getOptimalTime = async () => {
    if (!selectedClient) return;

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:5000/api/ml/optimal-time?client_id=${selectedClient}&platform=${platform}`
      );
      const data = await response.json();
      
      if (data.success) {
        setOptimalTime(data.optimal_time);
      }
    } catch (error) {
      console.error('Error getting optimal time:', error);
    } finally {
      setLoading(false);
    }
  };

  const forecastTrends = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/ml/forecast?days=7');
      const data = await response.json();
      
      if (data.success) {
        setForecast(data.forecast);
      }
    } catch (error) {
      console.error('Error forecasting:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Brain className="w-8 h-8 text-purple-600" />
          AI-Powered Insights
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Get intelligent predictions, detect unusual patterns, and optimize your content strategy
        </p>
      </div>

      {/* Model Status */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            AI Intelligence Status
          </h2>
          <button
            onClick={refreshModelStatus}
            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Refresh Status
          </button>
        </div>
        {modelStatus ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="p-3 rounded border border-gray-200 dark:border-gray-700">
              <p className="font-medium text-gray-900 dark:text-white">📊 Performance Predictor</p>
              <p className="mt-1 text-gray-600 dark:text-gray-400">
                Status: {modelStatus.predictor?.loaded ? '✅ Active' : '⏸️ Inactive'} • v{modelStatus.predictor?.version || '—'}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                Posts Analyzed: {modelStatus.predictor?.samples_trained ?? '—'} • Insights: {modelStatus.predictor?.features_used ?? '—'}
              </p>
            </div>
            <div className="p-3 rounded border border-gray-200 dark:border-gray-700">
              <p className="font-medium text-gray-900 dark:text-white">🔍 Pattern Detection</p>
              <p className="mt-1 text-gray-600 dark:text-gray-400">
                Status: {modelStatus.anomaly_detector?.loaded ? '✅ Active' : '⏸️ Inactive'} • v{modelStatus.anomaly_detector?.version || '—'}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                Posts Analyzed: {modelStatus.anomaly_detector?.samples_trained ?? '—'}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-600 dark:text-gray-400">Click Refresh Status to check intelligence availability.</p>
        )}
      </div>

      {/* Client Selection & Training */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Target className="w-5 h-5" />
            Setup & Data Analysis
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Client
            </label>
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Platform
            </label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="instagram">Instagram</option>
              <option value="youtube">YouTube</option>
              <option value="facebook">Facebook</option>
              <option value="twitter">Twitter</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={trainModels}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Brain className="w-4 h-4" />
            Analyze & Learn from Data
          </button>
          {trainingStatus && trainingStatus.models && (
            <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md space-y-1">
              {(() => {
                const predictor = trainingStatus.models?.predictor;
                const detector = trainingStatus.models?.anomaly_detector;
                return (
                  <>
                    {predictor && predictor.status === 'success' && (
                      <p className="text-sm text-green-800 dark:text-green-300">
                        ✅ Analysis complete using {predictor.samples_trained} posts • Accuracy Score: {predictor.r2_score_likes}
                      </p>
                    )}
                    {detector && detector.status === 'success' && (
                      <p className="text-sm text-green-800 dark:text-green-300">
                        🔍 Pattern detection ready using {detector.samples_trained} posts
                      </p>
                    )}
                    {!predictor && !detector && (
                      <p className="text-sm text-yellow-800 dark:text-yellow-300">
                        ⚠️ Analysis started but results not available yet.
                      </p>
                    )}
                  </>
                );
              })()}
            </div>
          )}
        </div>
      </div>

      {/* Engagement Prediction */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-yellow-500" />
          Test Your Content
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Post Caption
            </label>
            <textarea
              value={postCaption}
              onChange={(e) => setPostCaption(e.target.value)}
              placeholder="Enter your post caption to predict its performance..."
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 h-24"
            />
          </div>

          <button
            onClick={predictEngagement}
            disabled={loading || !postCaption}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Get Performance Forecast
          </button>

          {prediction && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Likes</p>
                  <p className="text-2xl font-bold text-blue-600">{prediction.predicted_likes.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Comments</p>
                  <p className="text-2xl font-bold text-green-600">{prediction.predicted_comments.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Views</p>
                  <p className="text-2xl font-bold text-purple-600">{prediction.predicted_views.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Virality Score</p>
                  <p className="text-2xl font-bold text-orange-600">{prediction.virality_score}/100</p>
                </div>
              </div>
              <div className="p-3 bg-white dark:bg-gray-700 rounded-md">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {prediction.recommendation}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Confidence: {prediction.confidence}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Anomaly Detection */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Unusual Activity Detection
          </h2>
          <button
            onClick={detectAnomaliesHandler}
            disabled={loading}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 text-sm"
          >
            Find Unusual Patterns
          </button>
        </div>

        {anomalies && (
          <div className="space-y-4">
            {/* Trend Analysis */}
            {anomalies.trend_analysis && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Trend Analysis</h3>
                <p className="text-sm mb-2">{anomalies.trend_analysis.alert}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {anomalies.trend_analysis.recommendation}
                </p>
              </div>
            )}

            {/* Engagement Drop */}
            {anomalies.engagement_drop && anomalies.engagement_drop.drop_detected && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">⚠️ Engagement Drop Detected</h3>
                <p className="text-sm">{anomalies.engagement_drop.alert_message}</p>
              </div>
            )}

            {/* Anomalies List */}
            {anomalies.anomalies && anomalies.anomalies.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Unusual Posts Found ({anomalies.total_anomalies_found})
                </h3>
                <div className="space-y-2">
                  {anomalies.anomalies.slice(0, 5).map((anomaly, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-gray-50 dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {anomaly.alert_message}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {anomaly.platform} • {anomaly.type} • {anomaly.date}
                          </p>
                          {/* Derived Parameters Display */}
                          {anomaly.metric_values && (
                            <div className="mt-2 flex gap-3 text-xs">
                              {anomaly.metric_values.responsiveness_index !== undefined && (
                                <span className="text-blue-600 dark:text-blue-400">
                                  👥 Responsiveness: {anomaly.metric_values.responsiveness_index.toFixed(1)}
                                </span>
                              )}
                              {anomaly.metric_values.peak_performance !== undefined && (
                                <span className="text-purple-600 dark:text-purple-400">
                                  🏆 Peak: {anomaly.metric_values.peak_performance.toFixed(0)}%
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          anomaly.severity === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' :
                          anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-300'
                        }`}>
                          {anomaly.severity}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Optimal Posting Time */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-green-500" />
            Best Time to Post
          </h2>
          <button
            onClick={getOptimalTime}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 text-sm"
          >
            Find Best Time
          </button>
        </div>

        {optimalTime && (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {optimalTime.recommendation}
              </p>
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Best Hours</p>
                  <div className="flex flex-wrap gap-2">
                    {optimalTime.best_hours && optimalTime.best_hours.map((hour, idx) => (
                      <span key={idx} className="px-2 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 rounded text-sm">
                        {hour}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Best Days</p>
                  <div className="flex flex-wrap gap-2">
                    {optimalTime.best_days && optimalTime.best_days.map((day, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 rounded text-sm">
                        {day}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {loading && <LoadingSkeleton />}
    </div>
  );
}
