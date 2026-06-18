import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [communes, setCommunes] = useState([]);
  const [leftCode, setLeftCode] = useState('');
  const [rightCode, setRightCode] = useState('');
  const [loadingCommunes, setLoadingCommunes] = useState(true);
  const [loadingCompare, setLoadingCompare] = useState(false);
  const [error, setError] = useState(null);
  const [compareData, setCompareData] = useState(null);

  // Fetch communes list on component mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/communes')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to fetch communes from API.');
        }
        return res.json();
      })
      .then((data) => {
        setCommunes(data.communes || []);
        // Set default dropdown values
        if (data.communes && data.communes.length >= 2) {
          setLeftCode(data.communes[0].code);
          setRightCode(data.communes[1].code);
        }
        setLoadingCommunes(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Error loading communes. Please verify that the backend is running at http://127.0.0.1:8000.');
        setLoadingCommunes(false);
      });
  }, []);

  const handleCompare = (e) => {
    e.preventDefault();
    if (!leftCode || !rightCode) {
      setError('Please select two communes to compare.');
      return;
    }
    if (leftCode === rightCode) {
      setError('Please select two different communes.');
      return;
    }

    setLoadingCompare(true);
    setError(null);

    fetch(`http://127.0.0.1:8000/compare?left=${leftCode}&right=${rightCode}`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Failed to fetch comparison statistics.');
        }
        return data;
      })
      .then((data) => {
        setCompareData(data);
        setLoadingCompare(false);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message || 'An error occurred while comparing the communes.');
        setLoadingCompare(false);
        setCompareData(null);
      });
  };

  const formatCurrency = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatSurface = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('fr-FR', {
      maximumFractionDigits: 1
    }).format(value) + ' m²';
  };

  const formatNumber = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('fr-FR').format(value);
  };

  return (
    <div className="container">
      <header>
        <h1 id="app-title">Val-de-Marne Real Estate Comparator</h1>
        <p className="subtitle">
          Compare property transactions, average prices, and price per square meter across communes in Val-de-Marne (94) using official DVF public data.
        </p>
      </header>

      <main>
        {/* Selection panel */}
        <section aria-labelledby="comparison-form-title">
          <h2 id="comparison-form-title" className="sr-only" style={{ display: 'none' }}>Select Communes</h2>
          <form onSubmit={handleCompare} className="comparison-panel" id="comparison-form">
            <div className="select-group">
              <label htmlFor="left-commune-select">Left Territory</label>
              <div className="select-wrapper">
                <select
                  id="left-commune-select"
                  value={leftCode}
                  onChange={(e) => setLeftCode(e.target.value)}
                  disabled={loadingCommunes}
                >
                  {loadingCommunes ? (
                    <option>Loading communes...</option>
                  ) : (
                    communes.map((c) => (
                      <option key={`left-${c.code}`} value={c.code}>
                        {c.name} ({c.code})
                      </option>
                    ))
                  )}
                </select>
              </div>
            </div>

            <div className="select-group">
              <label htmlFor="right-commune-select">Right Territory</label>
              <div className="select-wrapper">
                <select
                  id="right-commune-select"
                  value={rightCode}
                  onChange={(e) => setRightCode(e.target.value)}
                  disabled={loadingCommunes}
                >
                  {loadingCommunes ? (
                    <option>Loading communes...</option>
                  ) : (
                    communes.map((c) => (
                      <option key={`right-${c.code}`} value={c.code}>
                        {c.name} ({c.code})
                      </option>
                    ))
                  )}
                </select>
              </div>
            </div>

            <button
              id="compare-btn"
              type="submit"
              className="btn-compare"
              disabled={loadingCommunes || loadingCompare}
            >
              {loadingCompare ? 'Loading...' : 'Compare'}
            </button>
          </form>
        </section>

        {/* Global Error Banner */}
        {error && (
          <div className="error-banner" id="error-message" role="alert">
            {error}
          </div>
        )}

        {/* Comparison Results */}
        {loadingCompare && (
          <div className="spinner-container" id="loading-spinner">
            <div className="spinner" aria-label="Loading data"></div>
            <p>Analyzing real estate data...</p>
          </div>
        )}

        {!loadingCompare && !compareData && !error && (
          <div className="welcome-panel" id="welcome-message">
            <p>Select two communes above and click Compare to view and contrast real estate statistics.</p>
          </div>
        )}

        {!loadingCompare && compareData && (
          <section className="results-container" id="comparison-results" aria-label="Comparison Results">
            {/* Winner highlight banner */}
            {compareData.winner && (
              <div className="winner-badge" id="winner-banner">
                <span className="winner-title">
                  🏆 More Affordable Option
                </span>
                <span className="winner-detail">
                  <strong>{compareData.winner.commune_name}</strong> is more affordable on average at{' '}
                  <strong>{formatCurrency(compareData.winner.average_price_per_sqm)}/m²</strong>
                </span>
              </div>
            )}

            {/* Side by side comparison cards */}
            <div className="cards-grid">
              {/* Left card */}
              <article
                className={`commune-card ${
                  compareData.winner && compareData.winner.cadastre_code === compareData.left.cadastre_code
                    ? 'is-winner'
                    : ''
                }`}
                id="left-result-card"
              >
                <div className="card-header">
                  <div className="card-title-group">
                    <h3 className="commune-name">{compareData.left.commune_name}</h3>
                    <span className="commune-codes">
                      INSEE Code: {compareData.left.cadastre_code} (DVF: {compareData.left.dvf_commune_code})
                    </span>
                  </div>
                  {compareData.winner && compareData.winner.cadastre_code === compareData.left.cadastre_code && (
                    <span className="card-badge winner-indicator">Affordable</span>
                  )}
                </div>

                <div className="metric-grid">
                  <div className="metric-row main-metric winner-metric">
                    <span className="metric-label">Avg. Price / m²</span>
                    <div className="metric-value-container">
                      <span className="metric-value">{formatCurrency(compareData.left.average_price_per_sqm)}</span>
                    </div>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Transactions Count</span>
                    <span className="metric-value">{formatNumber(compareData.left.transaction_count)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Average Sale Price</span>
                    <span className="metric-value">{formatCurrency(compareData.left.average_price)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Median Sale Price</span>
                    <span className="metric-value">{formatCurrency(compareData.left.median_price)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Average Surface</span>
                    <span className="metric-value">{formatSurface(compareData.left.average_surface)}</span>
                  </div>
                </div>
              </article>

              {/* Right card */}
              <article
                className={`commune-card ${
                  compareData.winner && compareData.winner.cadastre_code === compareData.right.cadastre_code
                    ? 'is-winner'
                    : ''
                }`}
                id="right-result-card"
              >
                <div className="card-header">
                  <div className="card-title-group">
                    <h3 className="commune-name">{compareData.right.commune_name}</h3>
                    <span className="commune-codes">
                      INSEE Code: {compareData.right.cadastre_code} (DVF: {compareData.right.dvf_commune_code})
                    </span>
                  </div>
                  {compareData.winner && compareData.winner.cadastre_code === compareData.right.cadastre_code && (
                    <span className="card-badge winner-indicator">Affordable</span>
                  )}
                </div>

                <div className="metric-grid">
                  <div className="metric-row main-metric winner-metric">
                    <span className="metric-label">Avg. Price / m²</span>
                    <div className="metric-value-container">
                      <span className="metric-value">{formatCurrency(compareData.right.average_price_per_sqm)}</span>
                    </div>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Transactions Count</span>
                    <span className="metric-value">{formatNumber(compareData.right.transaction_count)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Average Sale Price</span>
                    <span className="metric-value">{formatCurrency(compareData.right.average_price)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Median Sale Price</span>
                    <span className="metric-value">{formatCurrency(compareData.right.median_price)}</span>
                  </div>

                  <div className="metric-row">
                    <span className="metric-label">Average Surface</span>
                    <span className="metric-value">{formatSurface(compareData.right.average_surface)}</span>
                  </div>
                </div>
              </article>
            </div>
          </section>
        )}
      </main>

      <footer>
        <p>© 2026 Val-de-Marne Real Estate Comparator. Built with React & FastAPI.</p>
      </footer>
    </div>
  );
}

export default App;
