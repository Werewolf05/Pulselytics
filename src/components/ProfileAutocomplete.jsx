import { useState, useEffect, useRef } from 'react';
import { Search, CheckCircle } from 'lucide-react';
import { getProfileSuggestions } from '../services/api';

export default function ProfileAutocomplete({ platform, value, onChange, placeholder }) {
  const [query, setQuery] = useState(value || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions when query changes
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!platform || query.length < 1) {
        setSuggestions([]);
        return;
      }

      setLoading(true);
      const results = await getProfileSuggestions(platform, query);
      setSuggestions(results);
      setLoading(false);
      setShowDropdown(true);
    };

    const timer = setTimeout(fetchSuggestions, 300); // Debounce
    return () => clearTimeout(timer);
  }, [query, platform]);

  const handleSelect = (suggestion) => {
    setQuery(suggestion.username);
    onChange(suggestion.username);
    setShowDropdown(false);
  };

  const handleInputChange = (e) => {
    const val = e.target.value.replace('@', ''); // Remove @ if typed
    setQuery(val);
    onChange(val);
  };

  const handleFocus = async () => {
    if (!query && platform) {
      setLoading(true);
      const results = await getProfileSuggestions(platform, '');
      setSuggestions(results);
      setLoading(false);
      setShowDropdown(true);
    } else if (suggestions.length > 0) {
      setShowDropdown(true);
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          className="w-full px-3 py-2 pl-9 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      </div>

      {showDropdown && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleSelect(suggestion)}
              className="w-full px-4 py-3 text-left hover:bg-slate-50 flex items-center justify-between border-b border-slate-100 last:border-b-0"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-900">@{suggestion.username}</span>
                  {suggestion.verified && (
                    <CheckCircle size={14} className="text-blue-500" />
                  )}
                </div>
                <div className="text-sm text-slate-500">{suggestion.name}</div>
              </div>
              <div className="text-xs text-slate-400 px-2 py-1 bg-slate-100 rounded">
                {suggestion.category}
              </div>
            </button>
          ))}
        </div>
      )}

      {showDropdown && loading && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg p-4 text-center text-slate-500">
          Loading suggestions...
        </div>
      )}

      {showDropdown && !loading && suggestions.length === 0 && query.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg p-4 text-center text-slate-500">
          No suggestions found. You can still enter the username manually.
        </div>
      )}
    </div>
  );
}
