import { useState, useEffect } from 'react';
import { Plus, Trash2, RefreshCw, Zap, Globe, Save, AlertCircle } from 'lucide-react';
import { getClients, createClient, deleteClient, triggerScrape, getScraperStatus } from '../services/api';
import ProfileAutocomplete from '../components/ProfileAutocomplete';
import { useToast } from '../components/ToastContainer';

export default function Settings() {
  const { success, error, info } = useToast();
  const [clients, setClients] = useState([]);
  const [scraperStatus, setScraperStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [newClient, setNewClient] = useState({
    id: '',
    name: '',
    platforms: {
      instagram: '',
      youtube: '',
      facebook: '',
      twitter: ''
    }
  });

  // Load initial data
  useEffect(() => {
    loadClients();
    loadScraperStatus();
  }, []);

  const loadClients = async () => {
    setLoading(true);
    const data = await getClients();
    setClients(data);
    setLoading(false);
  };

  const loadScraperStatus = async () => {
    try {
      const status = await getScraperStatus();
      setScraperStatus(status);
    } catch (error) {
      console.error('Failed to load scraper status:', error);
    }
  };

  const handleAddClient = async (e) => {
    e.preventDefault();
    
    if (!newClient.id || !newClient.name) {
      error('Please provide client ID and name');
      return;
    }

    try {
      await createClient(newClient);
      await loadClients();
      setShowAddForm(false);
      setNewClient({
        id: '',
        name: '',
        platforms: { instagram: '', youtube: '', facebook: '', twitter: '' }
      });
      success(`Client "${newClient.name}" created successfully!`);
    } catch (err) {
      error('Failed to create client: ' + err.message);
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (!confirm(`Delete client ${clientId}? This cannot be undone.`)) {
      return;
    }

    try {
      await deleteClient(clientId);
      await loadClients();
      success(`Client "${clientId}" deleted successfully`);
    } catch (err) {
      error('Failed to delete client: ' + err.message);
    }
  };

  const handleScrape = async (clientId) => {
    setScraping(prev => ({ ...prev, [clientId]: true }));
    
    try {
      await triggerScrape(clientId, ['all']);
      info(`Scraping started for ${clientId}. This may take a few minutes...`);
    } catch (err) {
      error('Failed to trigger scrape: ' + err.message);
    } finally {
      setScraping(prev => ({ ...prev, [clientId]: false }));
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Settings</h2>
        <p className="text-slate-600 mt-2">Manage clients and configure scrapers</p>
      </div>

      {/* Scraper Status Card */}
      {scraperStatus && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-900">Scraper Configuration</h3>
            {scraperStatus.scraper_mode === 'lightweight' ? (
              <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                <Zap size={14} />
                <span>Lightweight Scraper</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                <Globe size={14} />
                <span>Playwright Scraper</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(scraperStatus.platforms || {}).map(([platform, info]) => (
              <div key={platform} className="border border-slate-200 rounded-lg p-4">
                <div className="text-sm font-medium text-slate-700 capitalize mb-1">{platform}</div>
                <div className="text-xs text-slate-500">Method: {info.method}</div>
                <div className="text-xs text-slate-500">Speed: {info.speed}</div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle size={16} className="text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium">Auto-scraping: Every {scraperStatus.interval_minutes || 360} minutes</p>
                <p className="text-blue-600 mt-1">Configure interval in backend/.env file</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clients Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-slate-900">Client Management</h3>
          <button onClick={() => setShowAddForm(!showAddForm)} className="btn btn-primary flex items-center gap-2">
            <Plus size={18} />
            Add Client
          </button>
        </div>

        {/* Add Client Form */}
        {showAddForm && (
          <form onSubmit={handleAddClient} className="mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h4 className="font-semibold text-slate-900 mb-4">New Client</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Client ID*</label>
                <input type="text" required placeholder="e.g., acme-corp" value={newClient.id}
                  onChange={(e) => setNewClient({ ...newClient, id: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Client Name*</label>
                <input type="text" required placeholder="e.g., ACME Corporation" value={newClient.name}
                  onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Instagram</label>
                <ProfileAutocomplete
                  platform="instagram"
                  value={newClient.platforms.instagram}
                  onChange={(val) => setNewClient({ ...newClient, platforms: { ...newClient.platforms, instagram: val } })}
                  placeholder="@username"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">YouTube</label>
                <ProfileAutocomplete
                  platform="youtube"
                  value={newClient.platforms.youtube}
                  onChange={(val) => setNewClient({ ...newClient, platforms: { ...newClient.platforms, youtube: val } })}
                  placeholder="@channel"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Facebook</label>
                <ProfileAutocomplete
                  platform="facebook"
                  value={newClient.platforms.facebook}
                  onChange={(val) => setNewClient({ ...newClient, platforms: { ...newClient.platforms, facebook: val } })}
                  placeholder="pagename"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Twitter/X</label>
                <ProfileAutocomplete
                  platform="twitter"
                  value={newClient.platforms.twitter}
                  onChange={(val) => setNewClient({ ...newClient, platforms: { ...newClient.platforms, twitter: val } })}
                  placeholder="@username"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button type="submit" className="btn btn-primary flex items-center gap-2">
                <Save size={16} />
                Save Client
              </button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn btn-secondary">Cancel</button>
            </div>
          </form>
        )}

        {/* Clients List */}
        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading clients...</div>
        ) : clients.length === 0 ? (
          <div className="text-center py-8 text-slate-400">No clients yet. Click "Add Client" to get started.</div>
        ) : (
          <div className="space-y-4">
            {clients.map((client) => (
              <div key={client.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-slate-900">{client.name}</h4>
                    <p className="text-sm text-slate-500">ID: {client.id}</p>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleScrape(client.id)} disabled={scraping[client.id]}
                      className="btn btn-primary btn-sm flex items-center gap-2">
                      <RefreshCw size={14} className={scraping[client.id] ? 'animate-spin' : ''} />
                      {scraping[client.id] ? 'Scraping...' : 'Scrape Now'}
                    </button>
                    
                    <button onClick={() => handleDeleteClient(client.id)}
                      className="btn btn-secondary btn-sm flex items-center gap-2 text-red-600 hover:bg-red-50">
                      <Trash2 size={14} />
                      Delete
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                  {Object.entries(client.platforms || {}).map(([platform, username]) => (
                    username && (
                      <div key={platform} className="flex items-center gap-2 text-slate-600">
                        <span className="capitalize font-medium">{platform}:</span>
                        <span className="text-slate-500">@{username}</span>
                      </div>
                    )
                  ))}
                </div>

                {client.last_updated && (
                  <div className="mt-2 text-xs text-slate-400">
                    Last updated: {new Date(client.last_updated).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
