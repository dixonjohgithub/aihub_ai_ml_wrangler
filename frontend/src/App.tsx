import React from 'react';
import './App.css';

function App() {
  const [health, setHealth] = React.useState<string>('checking...');

  React.useEffect(() => {
    // Check backend health
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('unhealthy'));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Hub ML Wrangler</h1>
        <p>Statistical data imputation and analysis tool</p>
        <div className="health-status">
          Backend Status: <span className={health === 'healthy' ? 'healthy' : 'unhealthy'}>
            {health}
          </span>
        </div>
        <div className="features">
          <h2>Features</h2>
          <ul>
            <li>Docker containerized deployment</li>
            <li>React TypeScript frontend</li>
            <li>FastAPI backend</li>
            <li>PostgreSQL database</li>
            <li>Redis caching</li>
            <li>Nginx reverse proxy</li>
            <li>Celery background tasks</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;