export default function ReviewResultCard({review}) {
  if (!review) return <section className="panel"><p className="empty">Loading review explanation...</p></section>
  return <section className="panel review-card">
    <div className="panel-head"><div><p className="eyebrow">WHY FLAGGED</p><h2>{review.priority.replaceAll('_',' ')}</h2><p className="muted">{review.priority_reason}</p></div><span className="tag">Deterministic rules</span></div>
    <h3>Signals</h3>
    {review.signals.length ? review.signals.map(signal => <details className="review-signal" key={signal.code}><summary><strong>{signal.title.replaceAll('_',' ')}</strong><span className={`severity ${signal.severity.toLowerCase()}`}>{signal.severity}</span></summary><p>{signal.explanation}</p><dl><dt>Source</dt><dd>{signal.source}</dd><dt>Deterministic</dt><dd>{signal.deterministic ? 'Yes' : 'No'}</dd></dl></details>) : <p className="empty">No significant review signals.</p>}
    <ReviewList title="Evidence For Review" items={review.evidence_for}/><ReviewList title="Evidence Requiring Caution" items={review.evidence_against}/><ReviewList title="Limitations" items={review.limitations}/>
    <div className="next-action"><strong>Recommended Next Action</strong><p>{review.recommended_next_action}</p></div>
  </section>
}
function ReviewList({title,items}) { return <div className="review-list"><h3>{title}</h3>{items?.length ? <ul>{items.map((item,index)=><li key={`${title}-${index}`}>{item}</li>)}</ul> : <p className="muted">None recorded.</p>}</div> }
