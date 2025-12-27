export function TextAreas({
  originalText,
  setOriginalText,
  simplifiedText,
  estimatedCEFR
}: any) {
  return (
    <div className="text-areas">
      <div className="text-section">
        <h2>Original Text</h2>
        <div className="text-wrapper">
          {estimatedCEFR && (
            <div className="level-badge">{estimatedCEFR}</div>
          )}
          <textarea
            value={originalText}
            onChange={e => setOriginalText(e.target.value)}
            placeholder="Enter your text here..."
          />
        </div>
      </div>

      <div className="text-section">
        <h2>Simplified Text</h2>
        <textarea value={simplifiedText} disabled />
      </div>
    </div>
  )
}
