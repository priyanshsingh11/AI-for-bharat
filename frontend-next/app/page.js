'use client';

import { useState, useCallback } from 'react';

const API = 'http://127.0.0.1:8000';

// ─── Helpers ────────────────────────────────────────────────────────────────
function formatBytes(bytes) {
  if (!bytes) return '';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function StatusBadge({ result }) {
  const classes = { pass: 'status-pass', fail: 'status-fail', review: 'status-review' };
  const labels = { pass: 'PASS', fail: 'FAIL', review: 'REVIEW' };
  return <span className={`status-badge ${classes[result] || ''}`}>{labels[result] || result}</span>;
}

function FinalStatusPill({ status }) {
  const map = {
    'Eligible': ['pill-eligible', '●'],
    'Not Eligible': ['pill-not-eligible', '●'],
    'Needs Review': ['pill-needs-review', '▲'],
  };
  const [cls, icon] = map[status] || ['', ''];
  return <span className={`final-status-pill ${cls}`}>{icon} {status}</span>;
}

// ─── Bidder Result Card ──────────────────────────────────────────────────────
function BidderCard({ data, filename, onReview }) {
  const ev = data.evaluations || [];
  const passed = data.passed ?? ev.filter(e => e.result === 'pass').length;
  const total = data.total ?? ev.length;
  const finalStatus = data.final_status || data.ai_status || 'Unknown';
  const humanStatus = data.human_status;

  return (
    <div className="bidder-card">
      {/* Header */}
      <div className="bidder-card-header">
        <div>
          <div className="bidder-name">{filename.replace('.json', '')}</div>
          <div className="bidder-file">{humanStatus ? `Human: ${humanStatus}` : 'Pending human review'}</div>
        </div>
        <div className="criteria-badge">
          <div className="criteria-label">Compliance</div>
          <div className="criteria-count">{passed}/{total} Criteria</div>
        </div>
      </div>

      {/* Summary bar */}
      <div className="summary-bar">
        <div className="summary-item">
          <span className="summary-label">AI Status</span>
          <span className="summary-val">{data.ai_status}</span>
        </div>
        <span style={{ color: 'var(--border-bright)' }}>|</span>
        <div className="summary-item">
          <span className="summary-label">Final Status</span>
          <FinalStatusPill status={finalStatus} />
        </div>
        <span style={{ color: 'var(--border-bright)' }}>|</span>
        <div className="summary-item">
          <span className="summary-label">Summary</span>
          <span className="summary-val">{data.summary || `${passed}/${total} criteria passed`}</span>
        </div>
      </div>

      {/* Criteria Table */}
      {ev.length > 0 && (
        <table className="criteria-table">
          <thead>
            <tr>
              <th>Requirement</th>
              <th>Expected</th>
              <th>Identified</th>
              <th>Status</th>
              <th>AI Reasoning</th>
            </tr>
          </thead>
          <tbody>
            {ev.map((e, i) => (
              <tr key={i}>
                <td className="criterion-name">{e.criterion?.replace(/\b\w/g, c => c.toUpperCase())}</td>
                <td className="value-cell">{e.required_display || e.required || '—'}</td>
                <td className="value-cell">{e.found_display || (e.found === null ? 'Not Found' : e.found)}</td>
                <td><StatusBadge result={e.result} /></td>
                <td>{e.reason || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Evidence */}
      {ev.some(e => e.evidence) && (
        <div className="evidence-section">
          <div className="evidence-label">
            <span>✦</span> Verified Evidence Snippets
          </div>
          <div className="evidence-items">
            {ev.filter(e => e.evidence && e.evidence !== 'No direct match found').map((e, i) => (
              <div key={i} className={`evidence-item ${e.result}`}>
                <div>
                  <div className="evidence-text">
                    <strong style={{ color: 'var(--text-primary)' }}>{e.criterion?.replace(/\b\w/g, c => c.toUpperCase())}</strong>{' '}
                    — &ldquo;{e.evidence}&rdquo;
                  </div>
                  {e.page && <div className="evidence-page">📄 Page {e.page}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Human Review */}
      <div className="review-footer">
        <div className="review-hint">
          <span>👤</span> Pending final human determination
        </div>
        <div className="review-actions">
          <button className="btn btn-approve" onClick={() => onReview(filename, 'Eligible')}>✓ Approve</button>
          <button className="btn btn-reject" onClick={() => onReview(filename, 'Not Eligible')}>✕ Mark Not Eligible</button>
          <button className="btn btn-review" onClick={() => onReview(filename, 'Needs Review')}>▲ Needs Review</button>
        </div>
      </div>
    </div>
  );
}

// ─── Sidebar ─────────────────────────────────────────────────────────────────
function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>Tender AI</h2>
        <div><span>Precision Evaluation Engine</span></div>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-item active">
          <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          Dashboard
        </div>
      </nav>
    </aside>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function HomePage() {
  const [tenderFile, setTenderFile] = useState(null);
  const [bidderFiles, setBidderFiles] = useState([]);
  const [running, setRunning] = useState(false);
  const [statusMsgs, setStatusMsgs] = useState([]);
  const [results, setResults] = useState([]);
  const [dragOver, setDragOver] = useState(false);

  const addStatus = (msg, type = 'info') => setStatusMsgs(prev => [...prev, { msg, type }]);

  const handleTenderFile = (file) => {
    if (file) setTenderFile(file);
  };

  const addBidderFile = (file) => {
    if (file) setBidderFiles(prev => [...prev, file]);
  };

  const removeBidder = (idx) => setBidderFiles(prev => prev.filter((_, i) => i !== idx));

  const runPipeline = async () => {
    if (!tenderFile) { addStatus('Upload a tender document first.', 'error'); return; }
    if (bidderFiles.length === 0) { addStatus('Upload at least one bidder document.', 'error'); return; }

    setRunning(true);
    setStatusMsgs([]);
    setResults([]);

    try {
      // Upload
      addStatus('Uploading documents…', 'info');
      const form = new FormData();
      form.append('tender_file', tenderFile);
      bidderFiles.forEach(f => form.append('bidder_files', f));
      const uploadRes = await fetch(`${API}/upload`, { method: 'POST', body: form });
      if (!uploadRes.ok) throw new Error(`Upload failed: ${await uploadRes.text()}`);
      addStatus('Documents uploaded successfully.', 'success');

      // Process
      addStatus('Running OCR text extraction…', 'info');
      const processRes = await fetch(`${API}/process`, { method: 'POST' });
      if (!processRes.ok) throw new Error(`OCR failed: ${await processRes.text()}`);
      addStatus('OCR processing complete.', 'success');

      // Extract
      addStatus('Extracting structured data via LLM…', 'info');
      const extractRes = await fetch(`${API}/extract`, { method: 'POST' });
      if (!extractRes.ok) throw new Error(`Extraction failed: ${await extractRes.text()}`);
      addStatus('LLM extraction complete.', 'success');

      // Evaluate
      addStatus('Running rule engine evaluation…', 'info');
      const evalRes = await fetch(`${API}/evaluate`, { method: 'POST' });
      if (!evalRes.ok) throw new Error(`Evaluation failed: ${await evalRes.text()}`);
      const evalData = await evalRes.json();
      addStatus(`Evaluation complete — ${evalData.summary?.processed_files?.length || 0} bidder(s) evaluated.`, 'success');

      // Load results
      await loadResults();
    } catch (err) {
      addStatus(err.message, 'error');
    } finally {
      setRunning(false);
    }
  };

  const loadResults = async () => {
    // Fetch results via dedicated endpoint
    try {
      const res = await fetch(`${API}/results`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      }
    } catch {
      // Results endpoint may not exist; fallback silent
    }
  };

  const handleReview = async (filename, status) => {
    try {
      const res = await fetch(`${API}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bidder: filename, human_status: status }),
      });
      if (res.ok) {
        addStatus(`Marked ${filename.replace('.json','')} as "${status}".`, 'success');
        await loadResults();
      } else {
        addStatus(`Review failed: ${await res.text()}`, 'error');
      }
    } catch (err) {
      addStatus(err.message, 'error');
    }
  };

  return (
    <div className="layout">
      <Sidebar />
      <div className="main">
        <div className="topbar">
          <span className="topbar-title">Dashboard</span>
          <div className="system-badge">
            <span className="system-dot" />
            SYSTEM: OPERATIONAL
          </div>
        </div>

        <div className="content">
          {/* Header */}
          <div className="page-header">
            <h1>AI Tender Evaluation System</h1>
            <p>Automated eligibility analysis with explainable AI engine.</p>
          </div>

          {/* Upload Grid */}
          <div className="upload-grid">
            {/* Tender */}
            <div className="upload-card">
              <div className="upload-card-label">Tender Document</div>
              {!tenderFile ? (
                <div
                  className={`upload-drop-zone ${dragOver ? 'drag-over' : ''}`}
                  onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={e => { e.preventDefault(); setDragOver(false); handleTenderFile(e.dataTransfer.files[0]); }}
                >
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={e => handleTenderFile(e.target.files[0])} />
                  <div className="upload-icon">⬆</div>
                  <p>Drag and drop tender RFP or <a>browse files</a></p>
                </div>
              ) : (
                <div className="file-item">
                  <div className="file-item-name">
                    <span>📄</span>
                    <span>{tenderFile.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="file-item-size">{formatBytes(tenderFile.size)}</span>
                    <button className="file-remove" onClick={() => setTenderFile(null)}>✕</button>
                  </div>
                </div>
              )}
            </div>

            {/* Bidders */}
            <div className="upload-card">
              <div className="upload-card-label">Bidder Documents</div>
              <div className="file-list">
                {bidderFiles.map((f, i) => (
                  <div key={i} className="file-item">
                    <div className="file-item-name">
                      <span>📋</span>
                      <span>{f.name}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="file-item-size">{formatBytes(f.size)}</span>
                      <button className="file-remove" onClick={() => removeBidder(i)}>✕</button>
                    </div>
                  </div>
                ))}
                <label className="add-file-btn">
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg" multiple onChange={e => Array.from(e.target.files).forEach(addBidderFile)} />
                  <span>+</span> Add Bidder Document
                </label>
              </div>
            </div>
          </div>

          {/* Run Button */}
          <div className="run-section">
            <button className="run-btn" onClick={runPipeline} disabled={running}>
              {running ? <span className="spinner" /> : '⚡'}
              {running ? 'Running Evaluation…' : 'Run Evaluation'}
            </button>
            <div className="run-hint">Estimated completion: ~45 seconds depending on document size</div>
          </div>

          {/* Status Messages */}
          {statusMsgs.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              {statusMsgs.map((s, i) => (
                <div key={i} className={`status-message ${s.type}`}>
                  {s.type === 'success' ? '✓' : s.type === 'error' ? '✕' : '●'} {s.msg}
                </div>
              ))}
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <>
              <div className="report-header">
                <h2>Evaluation Report</h2>
              </div>
              {results.map((r, i) => (
                <BidderCard key={i} data={r.data} filename={r.filename} onReview={handleReview} />
              ))}
            </>
          )}

          {results.length === 0 && statusMsgs.some(s => s.type === 'success') && (
            <div className="empty-state">
              Results could not be loaded. Check the backend /results endpoint.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
