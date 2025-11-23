import { useState, useEffect } from 'react';
import { Key, ExternalLink, Check, X, AlertCircle, Info, DollarSign } from 'lucide-react';
import { getApiKeys, saveApiKey, validateApiKey, deleteApiKey } from '../services/api';
import { useToast } from '../components/ToastContainer';

export default function APIKeys() {
  const { success, error, info } = useToast();
  const [apiKeys, setApiKeys] = useState({
    youtube: '',
    facebook: '',
    instagram: '',
    twitter: ''
  });
  
  const [savedKeys, setSavedKeys] = useState({
    youtube: false,
    facebook: false,
    instagram: false,
    twitter: false
  });
  
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [saving, setSaving] = useState({});
  const [loading, setLoading] = useState(true);

  // Load saved keys from backend on mount
  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    setLoading(true);
    try {
      const keys = await getApiKeys();
      
      // Update savedKeys state based on which keys exist
      const newSavedKeys = {};
      Object.keys(keys).forEach(platform => {
        newSavedKeys[platform] = keys[platform]?.is_active || false;
      });
      setSavedKeys(newSavedKeys);
      
      console.log('Loaded API keys:', keys);
    } catch (error) {
      console.error('Error loading API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKey = async (platform) => {
    if (!apiKeys[platform]) {
      error('Please enter an API key');
      return;
    }
    
    setSaving({ ...saving, [platform]: true });
    
    try {
      await saveApiKey(platform, apiKeys[platform]);
      setSavedKeys({ ...savedKeys, [platform]: true });
      success(`${platform.charAt(0).toUpperCase() + platform.slice(1)} API key saved securely!`);
      
      // Clear the input field for security
      setApiKeys({ ...apiKeys, [platform]: '' });
    } catch (err) {
      error(`Failed to save API key: ${err.message}`);
    } finally {
      setSaving({ ...saving, [platform]: false });
    }
  };

  const handleTestKey = async (platform) => {
    if (!apiKeys[platform]) {
      error('Please enter an API key to test');
      return;
    }
    
    setTesting({ ...testing, [platform]: true });
    setTestResults({ ...testResults, [platform]: null });
    
    try {
      const result = await validateApiKey(platform, apiKeys[platform]);
      
      if (result.valid) {
        setTestResults({ ...testResults, [platform]: 'success' });
        success(`${platform.charAt(0).toUpperCase() + platform.slice(1)} API key is valid!`);
      } else {
        setTestResults({ ...testResults, [platform]: 'error' });
        error(`Validation failed: ${result.message}`);
      }
    } catch (err) {
      setTestResults({ ...testResults, [platform]: 'error' });
      error(`Test failed: ${err.message}`);
    } finally {
      setTesting({ ...testing, [platform]: false });
    }
  };

  const handleDeleteKey = async (platform) => {
    if (!confirm(`Delete ${platform} API key from database?`)) return;
    
    try {
      await deleteApiKey(platform);
      setApiKeys({ ...apiKeys, [platform]: '' });
      setSavedKeys({ ...savedKeys, [platform]: false });
      setTestResults({ ...testResults, [platform]: null });
      alert(`${platform.charAt(0).toUpperCase() + platform.slice(1)} API key deleted successfully`);
    } catch (error) {
      alert(`Failed to delete API key: ${error.message}`);
    }
  };

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube Data API v3',
      icon: '🎥',
      cost: 'FREE',
      quota: '10,000 requests/day',
      setupUrl: 'https://console.cloud.google.com/',
      docsUrl: 'https://developers.google.com/youtube/v3',
      instructions: [
        'Go to Google Cloud Console',
        'Create a new project',
        'Enable "YouTube Data API v3"',
        'Create credentials → API Key',
        'Copy your API key'
      ],
      limitations: 'None for public data'
    },
    {
      id: 'facebook',
      name: 'Facebook Graph API',
      icon: '👍',
      cost: 'FREE',
      quota: 'Rate limited',
      setupUrl: 'https://developers.facebook.com/tools/explorer/',
      docsUrl: 'https://developers.facebook.com/docs/graph-api',
      instructions: [
        'Go to Facebook Developers',
        'Create an app or use existing',
        'Go to Graph API Explorer',
        'Generate Access Token',
        'Grant permissions: pages_read_engagement'
      ],
      limitations: 'Some data requires page ownership'
    },
    {
      id: 'instagram',
      name: 'Instagram Graph API',
      icon: '📸',
      cost: 'FREE (Limited)',
      quota: 'Rate limited',
      setupUrl: 'https://developers.facebook.com/',
      docsUrl: 'https://developers.facebook.com/docs/instagram-api',
      instructions: [
        'Convert Instagram to Business account',
        'Connect to Facebook Page',
        'Create Facebook App',
        'Add Instagram Graph API',
        'Generate Access Token'
      ],
      limitations: 'Only works for business accounts you own'
    },
    {
      id: 'twitter',
      name: 'Twitter/X API',
      icon: '🐦',
      cost: 'PAID ($100/mo)',
      quota: 'Tier based',
      setupUrl: 'https://developer.x.com/',
      docsUrl: 'https://developer.x.com/en/docs',
      upgradeUrl: 'https://developer.x.com/en/portal/products',
      instructions: [
        'No free tier available',
        'Basic tier: $100/month',
        'Includes: Read/Write access',
        'Alternative: Use web scraping (limited)'
      ],
      limitations: 'No free option - requires paid subscription'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900">API Configuration</h2>
        <p className="text-slate-600 mt-2">Connect your social media API keys for reliable data access</p>
      </div>

      {/* Info Banner */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <Info size={20} className="text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-2">Why Use Official APIs?</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>✅ More reliable than web scraping</li>
              <li>✅ No rate limit issues</li>
              <li>✅ Access to complete data (likes, comments, views)</li>
              <li>✅ Faster data retrieval</li>
              <li>✅ YouTube & Facebook are 100% FREE</li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Key Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {platforms.map((platform) => (
          <div key={platform.id} className="card border-2 hover:border-primary transition-colors">
            {/* Platform Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{platform.icon}</span>
                <div>
                  <h3 className="font-bold text-slate-900">{platform.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-1 rounded font-medium ${
                      platform.cost === 'FREE' 
                        ? 'bg-green-100 text-green-700' 
                        : platform.cost.includes('FREE')
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {platform.cost}
                    </span>
                    <span className="text-xs text-slate-500">{platform.quota}</span>
                  </div>
                </div>
              </div>
              
              {savedKeys[platform.id] && testResults[platform.id] === 'success' && (
                <Check size={24} className="text-green-600" />
              )}
            </div>

            {/* API Key Input */}
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  API Key / Access Token
                </label>
                <input
                  type="password"
                  value={apiKeys[platform.id]}
                  onChange={(e) => setApiKeys({ ...apiKeys, [platform.id]: e.target.value })}
                  placeholder={platform.id === 'twitter' ? 'Requires paid subscription' : 'Enter your API key...'}
                  disabled={platform.id === 'twitter' && !apiKeys[platform.id]}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-slate-100 disabled:cursor-not-allowed"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleSaveKey(platform.id)}
                  disabled={!apiKeys[platform.id] || platform.id === 'twitter'}
                  className="btn btn-primary btn-sm flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Key size={14} />
                  Save Key
                </button>
                
                <button
                  onClick={() => handleTestKey(platform.id)}
                  disabled={!apiKeys[platform.id] || testing[platform.id]}
                  className="btn btn-secondary btn-sm flex-1 disabled:opacity-50"
                >
                  {testing[platform.id] ? 'Testing...' : 'Test Connection'}
                </button>
                
                {savedKeys[platform.id] && (
                  <button
                    onClick={() => handleDeleteKey(platform.id)}
                    className="btn btn-secondary btn-sm text-red-600 hover:bg-red-50"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* Test Result */}
              {testResults[platform.id] && (
                <div className={`p-3 rounded-lg flex items-center gap-2 text-sm ${
                  testResults[platform.id] === 'success'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                }`}>
                  {testResults[platform.id] === 'success' ? (
                    <>
                      <Check size={16} />
                      <span>Connection successful! Key is valid.</span>
                    </>
                  ) : (
                    <>
                      <X size={16} />
                      <span>Connection failed. Please check your API key.</span>
                    </>
                  )}
                </div>
              )}

              {/* Get API Key / Upgrade */}
              <div className="pt-3 border-t border-slate-200">
                <p className="text-xs text-slate-600 mb-2">
                  <strong>Setup Instructions:</strong>
                </p>
                <ol className="text-xs text-slate-600 space-y-1 mb-3">
                  {platform.instructions.map((step, idx) => (
                    <li key={idx}>{idx + 1}. {step}</li>
                  ))}
                </ol>
                
                <div className="flex gap-2">
                  {platform.id === 'twitter' ? (
                    <a
                      href={platform.upgradeUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm flex-1 flex items-center justify-center gap-2"
                    >
                      <DollarSign size={14} />
                      Upgrade to Paid API
                      <ExternalLink size={12} />
                    </a>
                  ) : (
                    <a
                      href={platform.setupUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm flex-1 flex items-center justify-center gap-2"
                    >
                      Get Free API Key
                      <ExternalLink size={12} />
                    </a>
                  )}
                  
                  <a
                    href={platform.docsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary btn-sm flex items-center gap-1"
                  >
                    Docs
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>

              {/* Limitations */}
              {platform.limitations && (
                <div className="flex items-start gap-2 p-2 bg-slate-50 rounded text-xs text-slate-600">
                  <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
                  <span>{platform.limitations}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="card bg-slate-50">
        <h3 className="font-semibold text-slate-900 mb-3">Quick Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium text-slate-700 mb-2">✅ Free APIs (Recommended):</p>
            <ul className="text-slate-600 space-y-1">
              <li>• YouTube: Best option, 10k requests/day</li>
              <li>• Facebook: Good for public pages</li>
            </ul>
          </div>
          <div>
            <p className="font-medium text-slate-700 mb-2">⚠️ Limited / Paid:</p>
            <ul className="text-slate-600 space-y-1">
              <li>• Instagram: Only your business account</li>
              <li>• Twitter: $100/month minimum</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
