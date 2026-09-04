import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import './gis.css'
import AppShell from './components/AppShell'
import Dashboard from './components/Dashboard'
import CaseDetails from './components/CaseDetails'
import CasesPage from './components/CasesPage'
import MapPage from './components/MapPage'
import ModulePage from './components/ModulePage'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
function readRoute() {
  const path = location.hash.replace(/^#/, '') || '/'; const caseMatch = path.match(/^\/cases\/([^/]+)$/)
  if (caseMatch) return { name: 'case-details', claimId: decodeURIComponent(caseMatch[1]) }
  const routes = {'/':'dashboard','/cases':'cases','/map':'map','/field-verification':'field-verification','/community-review':'community-review','/evidence-ledger':'evidence-ledger','/anomalies':'anomalies','/data-provenance':'data-provenance','/settings':'settings'}
  return { name: routes[path] || 'not-found' }
}
function App() {
  const [route, setRoute] = useState(readRoute())
  useEffect(() => { const update = () => setRoute(readRoute()); addEventListener('hashchange', update); return () => removeEventListener('hashchange', update) }, [])
  const openCase = id => { location.hash = `#/cases/${encodeURIComponent(id)}` }
  const view = route.name === 'dashboard' ? <Dashboard api={API} onOpenCase={openCase}/> : route.name === 'cases' ? <CasesPage api={API} onOpenCase={openCase}/> : route.name === 'case-details' ? <CaseDetails api={API} claimId={route.claimId} onOpenCase={openCase}/> : route.name === 'map' ? <MapPage api={API} onOpenCase={openCase}/> : <ModulePage api={API} module={route.name}/>
  return <AppShell activeRoute={route.name}>{view}</AppShell>
}
createRoot(document.getElementById('root')).render(<App />)
