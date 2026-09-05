import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import './gis.css'
import './map-dashboard.css'
import './case-overview.css'
import './india-map.css'
import AppShell from './components/AppShell'
import Dashboard from './components/Dashboard'
import CaseDetails from './components/CaseDetails'
import CasesPage from './components/CasesPage'
import MapPage from './components/MapPage'
import ModulePage from './components/ModulePage'
import SettingsPage from './components/SettingsPage'
import { loadPreferences, savePreferences } from './components/preferences'

const API = import.meta.env.VITE_API_BASE_URL || 'http://fra-ai-decision-support.vercel.app'
function readRoute() {
  const rawPath = location.hash.replace(/^#/, '') || '/'; const [path, query = ''] = rawPath.split('?'); const caseMatch = path.match(/^\/cases\/([^/]+)$/)
  if (caseMatch) return { name: 'case-details', claimId: decodeURIComponent(caseMatch[1]) }
  const routes = {'/':'dashboard','/cases':'cases','/map':'map','/field-verification':'field-verification','/community-review':'community-review','/evidence-ledger':'evidence-ledger','/anomalies':'anomalies','/data-provenance':'data-provenance','/settings':'settings'}
  return { name: routes[path] || 'not-found', focusClaimId: new URLSearchParams(query).get('claim') || undefined }
}
function App() {
  const [route, setRoute] = useState(readRoute())
  const [prefs, setPrefs] = useState(loadPreferences)
  useEffect(() => { const update = () => setRoute(readRoute()); addEventListener('hashchange', update); return () => removeEventListener('hashchange', update) }, [])
  useEffect(() => { savePreferences(prefs) }, [prefs])
  const openCase = id => { location.hash = `#/cases/${encodeURIComponent(id)}` }
  const view = route.name === 'dashboard' ? <Dashboard api={API} onOpenCase={openCase}/> : route.name === 'cases' ? <CasesPage api={API} onOpenCase={openCase}/> : route.name === 'case-details' ? <CaseDetails api={API} claimId={route.claimId} onOpenCase={openCase}/> : route.name === 'map' ? <MapPage api={API} onOpenCase={openCase} focusClaimId={route.focusClaimId}/> : route.name === 'settings' ? <SettingsPage api={API} prefs={prefs} setPrefs={setPrefs}/> : <ModulePage api={API} module={route.name}/>
  return <AppShell activeRoute={route.name}>{view}</AppShell>
}
createRoot(document.getElementById('root')).render(<App />)
