import MapView from './MapView'
export default function MapPage({ api, onOpenCase, focusClaimId }) {
  return <main className="map-dashboard" aria-label="India evidence map"><MapView api={api} onOpenCase={onOpenCase} focusClaimId={focusClaimId}/></main>
}
