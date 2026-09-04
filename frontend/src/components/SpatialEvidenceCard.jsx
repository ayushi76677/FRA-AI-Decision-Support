export default function SpatialEvidenceCard({ spatial, onMap }) {
 if(!spatial) return <div className="empty">Loading spatial evidence...</div>
 const flags=spatial.spatial_flags || []
 return <section className="panel spatial-card"><div className="panel-head"><div><p className="eyebrow">SPATIAL EVIDENCE</p><h2>Geography and relationships</h2></div><button onClick={onMap}>View on Map</button></div><div className="spatial-grid"><Metric label="Claim area" value={spatial.area_hectares != null ? `${spatial.area_hectares} ha` : 'Unavailable'}/><Metric label="Geometry" value={spatial.geometry_valid ? 'Valid' : 'Unavailable'}/><Metric label="Nearby claims" value={spatial.nearby_claims?.length || 0}/><Metric label="Overlaps" value={spatial.overlaps?.length || 0}/></div>{flags.map(flag=><div className="spatial-flag" key={flag.code}><strong>{flag.code.replaceAll('_',' ')}</strong><span>{flag.message} {flag.action}</span></div>)}<p className="limitation">{spatial.limitations?.[0] || 'Spatial relationships require human review.'}</p></section>
}
function Metric({label,value}) { return <div><span>{label}</span><strong>{value}</strong></div> }
