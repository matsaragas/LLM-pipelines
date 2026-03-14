import React, { useState } from 'react';
import axios from 'axios';
import { FaSearch, FaFilter, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [theme, setTheme] = useState('');
  const [country, setCountry] = useState('');
  const [isStructured, setIsStructured] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const endpoint = isStructured ? `${API_URL}/query/structured` : `${API_URL}/query`;
      const payload = {
        query_str: query,
        theme: theme || null,
        country: country || null
      };

      const response = await axios.post(endpoint, payload);
      setResult({ type: isStructured ? 'structured' : 'standard', data: response.data });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred while fetching results. Ensure the backend is running and data is ingested.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Llama Intelligence</h1>
        <p>AI-Powered News Contextualization & Fact-Checking</p>
      </header>

      <main>
        <div className="glass-panel search-form">
          <form onSubmit={handleSearch}>
            <div className="search-input-group">
              <input 
                type="text" 
                className="search-input" 
                placeholder="Ask a question about the news..." 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Searching...' : <><FaSearch /> Search</>}
              </button>
            </div>

            <div className="filters-group" style={{marginTop: '20px'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-secondary)'}}>
                <FaFilter /> Filters:
              </div>
              <select 
                className="filter-select" 
                value={theme} 
                onChange={(e) => setTheme(e.target.value)}
              >
                <option value="">All Themes</option>
                <option value="Politics">Politics</option>
                <option value="Business">Business</option>
                <option value="Technology">Technology</option>
                <option value="Sport">Sport</option>
              </select>
              
              <select 
                className="filter-select" 
                value={country} 
                onChange={(e) => setCountry(e.target.value)}
              >
                <option value="">All Regions</option>
                <option value="UK">UK</option>
                <option value="US">US</option>
                <option value="EU">EU</option>
              </select>

              <label className="toggle-group" style={{marginLeft: 'auto'}}>
                <input 
                  type="checkbox" 
                  checked={isStructured} 
                  onChange={(e) => setIsStructured(e.target.checked)}
                />
                Use Structured Analysis (Fact Check)
              </label>
            </div>
          </form>
        </div>

        {error && (
          <div className="error-message" style={{marginTop: '20px'}}>
            <FaExclamationTriangle style={{marginRight: '10px'}}/> {error}
          </div>
        )}

        {loading && (
          <div className="loader-container">
            <div className="spinner"></div>
          </div>
        )}

        {result && !loading && (
          <div className="results-container" style={{marginTop: '30px'}}>
            {result.type === 'standard' ? (
              <div className="glass-panel result-card">
                <div className="result-section">
                  <h3><FaCheckCircle /> Analysis</h3>
                  <p style={{fontSize: '1.1rem', marginTop: '15px'}}>{result.data.response}</p>
                </div>
                
                {result.data.source_nodes && result.data.source_nodes.length > 0 && (
                  <div style={{marginTop: '40px'}}>
                    <h4 style={{color: 'var(--text-secondary)'}}>Sources Used</h4>
                    <div className="source-nodes">
                      {result.data.source_nodes.map((node, idx) => (
                        <div key={idx} className="source-node">
                          <p>"{node.text}"</p>
                          <div className="source-meta">
                            <span>Score: {node.score ? node.score.toFixed(3) : 'N/A'}</span>
                            <span style={{color: 'var(--text-secondary)'}}>ID: {node.node_id.substring(0,8)}...</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-panel result-card structured">
                <div className="result-section" style={{marginBottom: '30px'}}>
                  <h3>Theme Focus: {result.data.theme_type}</h3>
                </div>
                <div className="result-section" style={{marginBottom: '30px'}}>
                  <h4 style={{color: 'var(--text-secondary)', marginBottom: '10px'}}>Key Members & Roles (Short Response)</h4>
                  <p style={{background: 'rgba(255,255,255,0.02)', padding: '15px', borderRadius: '8px'}}>{result.data.short_response}</p>
                </div>
                <div className="result-section">
                  <h4 style={{color: 'var(--text-secondary)', marginBottom: '10px'}}>Statistics & Details</h4>
                  <p style={{background: 'rgba(255,255,255,0.02)', padding: '15px', borderRadius: '8px'}}>{result.data.detail_response}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
