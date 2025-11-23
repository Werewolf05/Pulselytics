import { useState, useEffect } from 'react';
import { Download, FileText, Calendar, TrendingUp, Users, Hash, BarChart3, FileDown } from 'lucide-react';
import { getAnalytics, generatePDFReport } from '../services/api';
import { useToast } from '../components/ToastContainer';

export default function Reports({ selectedClient, dateRange, selectedPlatform, searchQuery }) {
  const { success, error } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');

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
        console.error('Error fetching report data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedClient, dateRange, selectedPlatform, searchQuery]);

  const handleGeneratePDF = async () => {
    if (!selectedClient) {
      error('Please select a client first');
      return;
    }

    setGeneratingPDF(true);
    try {
      const result = await generatePDFReport(selectedClient, dateRange);
      
      if (result.success) {
        success('PDF report generated successfully!');
        
        // Trigger download
        const downloadUrl = `http://127.0.0.1:5000${result.download_url}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = result.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        error(result.error || 'Failed to generate PDF report');
      }
    } catch (err) {
      console.error('PDF generation error:', err);
      error('Failed to generate PDF report. Make sure the backend is running.');
    } finally {
      setGeneratingPDF(false);
    }
  };

  const handleExport = (type) => {
    if (!data) return;

    const filename = `${selectedClient || 'all'}_report_${new Date().toISOString().split('T')[0]}`;
    
    if (type === 'csv') {
      exportToCSV(filename);
    } else if (type === 'json') {
      exportToJSON(filename);
    }
  };

  const exportToCSV = (filename) => {
    const headers = ['Metric', 'Value'];
    const rows = [
      ['Total Posts', data.total_posts],
      ['Total Engagement', data.total_engagement],
      ['Average Engagement', data.avg_engagement?.toFixed(2)],
      ['Platform Count', Object.keys(data.platforms || {}).length],
      ['Date Range', dateRange],
      ['Positive Sentiment %', ((data.sentiment?.positive / data.total_posts * 100) || 0).toFixed(1)],
      ['Neutral Sentiment %', ((data.sentiment?.neutral / data.total_posts * 100) || 0).toFixed(1)],
      ['Negative Sentiment %', ((data.sentiment?.negative / data.total_posts * 100) || 0).toFixed(1)]
    ];

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    downloadFile(csvContent, `${filename}.csv`, 'text/csv');
  };

  const exportToJSON = (filename) => {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, `${filename}.json`, 'application/json');
  };

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card">
        <h2 className="text-2xl font-bold text-slate-900">Reports</h2>
        <p className="text-slate-600 mt-4">No data available for reporting.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Reports & Analytics Summary</h2>
          <p className="text-slate-600 mt-1">Comprehensive performance overview</p>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={handleGeneratePDF}
            disabled={generatingPDF || !selectedClient}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FileDown size={20} />
            {generatingPDF ? 'Generating PDF...' : 'Generate PDF Report'}
          </button>
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="csv">CSV Format</option>
            <option value="json">JSON Format</option>
          </select>
          <button
            onClick={() => handleExport(exportFormat)}
            className="btn-secondary flex items-center gap-2"
          >
            <Download size={20} />
            Export Data
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center gap-3">
            <FileText size={32} className="opacity-80" />
            <div>
              <p className="text-sm opacity-90">Total Posts</p>
              <p className="text-3xl font-bold">{data.total_posts?.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center gap-3">
            <TrendingUp size={32} className="opacity-80" />
            <div>
              <p className="text-sm opacity-90">Total Engagement</p>
              <p className="text-3xl font-bold">{data.total_engagement?.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-pink-500 to-pink-600 text-white">
          <div className="flex items-center gap-3">
            <BarChart3 size={32} className="opacity-80" />
            <div>
              <p className="text-sm opacity-90">Avg Engagement</p>
              <p className="text-3xl font-bold">{data.avg_engagement?.toFixed(0)}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="flex items-center gap-3">
            <Hash size={32} className="opacity-80" />
            <div>
              <p className="text-sm opacity-90">Top Hashtags</p>
              <p className="text-3xl font-bold">{data.hashtags?.length || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Report Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Breakdown */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Users className="text-primary" size={20} />
            Platform Breakdown
          </h3>
          <div className="space-y-3">
            {data.platforms?.map((platform, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <span className="font-medium text-slate-700 capitalize">{platform.platform}</span>
                <span className="text-lg font-bold text-primary">{platform.posts} posts</span>
              </div>
            )) || <p className="text-slate-400">No platform data</p>}
          </div>
        </div>

        {/* Sentiment Summary */}
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp className="text-primary" size={20} />
            Sentiment Summary
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-green-700">Positive</span>
              <span className="text-lg font-bold text-green-600">
                {data.sentiment?.positive || 0} ({((data.sentiment?.positive / data.total_posts * 100) || 0).toFixed(1)}%)
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="font-medium text-slate-700">Neutral</span>
              <span className="text-lg font-bold text-slate-600">
                {data.sentiment?.neutral || 0} ({((data.sentiment?.neutral / data.total_posts * 100) || 0).toFixed(1)}%)
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <span className="font-medium text-red-700">Negative</span>
              <span className="text-lg font-bold text-red-600">
                {data.sentiment?.negative || 0} ({((data.sentiment?.negative / data.total_posts * 100) || 0).toFixed(1)}%)
              </span>
            </div>
          </div>
        </div>

        {/* Top Hashtags */}
        {data.hashtags && data.hashtags.length > 0 && (
          <div className="card lg:col-span-2">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Hash className="text-primary" size={20} />
              Top 10 Hashtags
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {data.hashtags.slice(0, 10).map((tag, index) => (
                <div key={index} className="p-3 bg-primary/10 rounded-lg text-center">
                  <p className="font-bold text-primary text-lg">#{tag.hashtag}</p>
                  <p className="text-sm text-slate-600">{tag.count} uses</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Report Metadata */}
        <div className="card lg:col-span-2 bg-slate-50">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="text-primary" size={20} />
            <h3 className="text-lg font-bold text-slate-900">Report Information</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-slate-600">Date Range</p>
              <p className="font-bold text-slate-900">{dateRange}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Client</p>
              <p className="font-bold text-slate-900">{selectedClient || 'All Clients'}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Generated</p>
              <p className="font-bold text-slate-900">{new Date().toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Time</p>
              <p className="font-bold text-slate-900">{new Date().toLocaleTimeString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
