import type { LexiGradeResponse } from '../services/types'

function getFailedTestNames(
  failed: Record<string, any> | undefined
): string[] {
  if (!failed || typeof failed !== 'object') return []
  return Object.keys(failed)
}


export function TestResults({ result }: { result: LexiGradeResponse }) {
  return (
    <div className="qc-panel">

      <div className="qc-header">
        <h3>Quality Control</h3>

        <div className="qc-summary">
          <span className={`qc-badge ${result.accepted ? 'ok' : 'fail'}`}>
            {result.accepted ? '✅ Accepted' : '❌ Rejected'}
          </span>

          <span className="qc-mode">
            {result.soft_relaxed ? 'Relaxed' : 'Strict'}
          </span>
        </div>
      </div>

      {/* 🔔 Semantic Alert */}
      {result.semantic_alert && (
        <div className="qc-semantic-alert">
          <span className="qc-alert-icon">⚠</span>
          <div>
            <strong>Semantic alert</strong>
            <p>{result.semantic_alert}</p>
          </div>
        </div>
      )}

      <div className="qc-grid">
        {/* Hard Tests */}
        <div className="qc-card">
          <h4>Hard Tests</h4>

          <div className="qc-status">
            {result.final_hard_tests.accepted ? '✅ Passed' : '❌ Failed'}
          </div>

          <div className="qc-metric">
            {result.final_hard_tests.passed_tests.length} / {result.final_hard_tests.total_tests} tests passed
          </div>

          <ul className="qc-list">
            {result.final_hard_tests.passed_tests.map(test => (
              <li key={test}>✔ {test.replaceAll('_', ' ')}</li>
            ))}

            {getFailedTestNames(result.final_hard_tests.failed_tests).map(test => (
              <li key={test}>❌ {test.replaceAll('_', ' ')}</li>
            ))}
          </ul>
        </div>

        {/* Soft Tests */}
        <div className="qc-card">
          <h4>Soft Tests</h4>

          <div className="qc-status">
            {result.final_soft_tests.accepted ? '✅ Passed' : '❌ Failed'}
          </div>

          <div className="qc-metric">
            Pass ratio: {result.final_soft_tests.pass_ratio.toFixed(2)}
            <span className="qc-muted">
              {' '} (min {result.final_soft_tests.min_required})
            </span>
          </div>

          <ul className="qc-list">
            {result.final_soft_tests.passed_tests.map(test => (
              <li key={test}>✔ {test.replaceAll('_', ' ')}</li>
            ))}

            {getFailedTestNames(result.final_soft_tests.failed_tests).map(test => (
              <li key={test}>❌ {test.replaceAll('_', ' ')}</li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  )
}
