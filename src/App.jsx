import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ToastProvider } from './components/ToastContainer';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Analytics from './pages/Analytics';
import TopPosts from './pages/TopPosts';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import APIKeys from './pages/APIKeys';
import PredictiveAnalytics from './pages/PredictiveAnalytics';

function App() {
  const [selectedClient, setSelectedClient] = useState('');
  // Default to 'all' so users immediately see historical data on first load
  const [dateRange, setDateRange] = useState('all');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <ToastProvider>
      <Router>
        <Layout 
          selectedClient={selectedClient}
          setSelectedClient={setSelectedClient}
          dateRange={dateRange}
          setDateRange={setDateRange}
          selectedPlatform={selectedPlatform}
          setSelectedPlatform={setSelectedPlatform}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        >
          <Routes>
            <Route 
              path="/" 
              element={
                <Overview 
                  selectedClient={selectedClient} 
                  dateRange={dateRange} 
                  selectedPlatform={selectedPlatform}
                  searchQuery={searchQuery}
                />
              } 
            />
            <Route 
              path="/analytics" 
              element={
                <Analytics 
                  selectedClient={selectedClient} 
                  dateRange={dateRange} 
                  selectedPlatform={selectedPlatform}
                  searchQuery={searchQuery}
                />
              } 
            />
            <Route 
              path="/top-posts" 
              element={
                <TopPosts 
                  selectedClient={selectedClient} 
                  dateRange={dateRange} 
                  selectedPlatform={selectedPlatform}
                  searchQuery={searchQuery}
                />
              } 
            />
            <Route 
              path="/reports" 
              element={
                <Reports 
                  selectedClient={selectedClient} 
                  dateRange={dateRange} 
                  selectedPlatform={selectedPlatform}
                  searchQuery={searchQuery}
                />
              } 
            />
            <Route 
              path="/settings" 
              element={
                <Settings 
                  selectedClient={selectedClient}
                />
              } 
            />
            <Route path="/api-keys" element={<APIKeys />} />
            <Route 
              path="/predictive" 
              element={
                <PredictiveAnalytics 
                  selectedClient={selectedClient}
                />
              } 
            />
          </Routes>
        </Layout>
      </Router>
    </ToastProvider>
  );
}

export default App;
