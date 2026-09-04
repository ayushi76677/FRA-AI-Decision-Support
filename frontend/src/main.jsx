import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function getJson(path) {
  const response = await fetch(`${API}${path}`)
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  return response.json()
}

function App() {
  const [stats, setStats] = useState(null)
  const [states, setStates] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getJson('/api/v1/statistics/states'),
      getJson('/api/v1/states'),
      getJson('/api/v1/anomalies'),
    ]).then(([summary, stateData, anomalyData]) => {
      setStats(summary); setStates(stateData.data); setAnomalies(anomalyData.data)
    }).catch(() => setError('Backend unavailable. Start the FastAPI service and reload.'))
  }, [])

  return <div className="shell">
    <aside><div className="brand"><span>FRA</span><div>Evidence Ledger<small>Decision support system</small></div></div>
      <nav>{['Dashboard', 'Cases', 'Evidence Ledger', 'Map', 'Field Verification', 'Community Review', 'Data Provenance'].map((item, index) => <a className={index === 0 ? 'active' : ''} href="#" key={item}>{item}</a>)}</nav>
      <div className="side-note">Human-in-the-loop<br/><strong>Evidence first</strong></div>
    </aside>
    <main><header><div><p className="eyebrow">FOREST RIGHTS ACT MONITORING</p><h1>Decision overview</h1><p className="muted">State-level progress from supplied government datasets - 2024 reporting period</p></div><div className="status"><i /> Read-only data source</div></header>
      {error && <div className="error">{error}</div>}
      <section className="cards"><Metric label="Claims received" value={stats?.claims_received_total} /><Metric label="Titles distributed" value={stats?.titles_distributed_total} /><Metric label="Pending claims" value={stats?.pending_claims_total} tone="amber" /><Metric label="Distribution rate" value={stats ? `${stats.title_distribution_rate_percent}%` : null} /></section>
      <section className="grid"><div className="panel wide"><div className="panel-head"><div><h2>State progress</h2><p className="muted">Claims and titles reported by state</p></div><span className="tag">2024</span></div><div className="table-wrap"><table><thead><tr><th>State</th><th>Claims received</th><th>Titles distributed</th><th>Pending</th><th>Rate</th></tr></thead><tbody>{states.map((state) => <tr key={state.state}><td><strong>{state.state}</strong></td><td>{state.claims_received.total.toLocaleString()}</td><td>{state.titles_distributed.total.toLocaleString()}</td><td>{state.pending_claims.toLocaleString()}</td><td><Bar value={state.title_distribution_rate_percent} /></td></tr>)}</tbody></table></div></div>
      <div className="panel"><div className="panel-head"><div><h2>Review signals</h2><p className="muted">Transparent operational triage</p></div></div>{anomalies.length ? anomalies.slice(0, 7).map((item) => <div className="signal" key={item.state}><span className="dot amber" /><div><strong>{item.state}</strong><p>{item.pending_rate_percent}% pending - {item.explanation}</p></div></div>) : <div className="empty">No threshold signals in the current dataset.</div>}<div className="limitation">Signals are not legal findings. Human verification is required.</div></div></section>
      <section className="panel map-panel"><div className="panel-head"><div><h2>WebGIS readiness</h2><p className="muted">State-level properties are available for map joining</p></div><span className="tag neutral">Geometry unavailable</span></div><div className="map-empty"><div className="map-icon">⌖</div><h3>District geometry not supplied</h3><p>The current CSV sources contain no district boundaries, claim coordinates, or individual claim records. A boundary GeoJSON layer can join on state or district codes when provided.</p></div></section>
      <footer>Observation → explainable signal → human review. The machine assists; authorized humans decide.</footer>
    </main>
  </div>
}

function Metric({ label, value, tone }) { return <div className={`metric ${tone || ''}`}><span>{label}</span><strong>{value == null ? '—' : value.toLocaleString?.() ?? value}</strong><small>Supplied dataset</small></div> }
function Bar({ value }) { return <div className="bar"><span style={{ width: `${Math.min(value || 0, 100)}%` }} /><b>{value}%</b></div> }
createRoot(document.getElementById('root')).render(<App />)
