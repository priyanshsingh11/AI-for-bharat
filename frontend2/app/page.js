'use client';

import { useState } from 'react';

const API = 'http://127.0.0.1:8000';

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
    'Eligible': ['pill-eligible', 'ELIGIBLE'],
    'Not Eligible': ['pill-not-eligible', 'NOT ELIGIBLE'],
    'Needs Review': ['pill-needs-review', 'NEEDS REVIEW'],
  };
  const [cls, label] = map[status] || ['', status];
  return <span className={`final-status-pill ${cls}`}>{label}</span>;
}

function BidderCard({ data, filename, onReview }) {
  const ev = data.evaluations || [];
  const passed = data.passed ?? ev.filter(e => e.result === 'pass').length;
  const total = data.total ?? ev.length;
  const finalStatus = data.final_status || data.ai_status || 'Unknown';
  const humanStatus = data.human_status;

  return (
    <div className="bidder-card">
      <div className="bidder-card-header">
        <div>
          <div className="bidder-name">{filename.replace('.json', '')}</div>
          <div className="bidder-file">{humanStatus ? `Human override: ${humanStatus}` : 'Pending human review'}</div>
        </div>
        <div className="criteria-badge">
          <div className="criteria-label">Compliance</div>
          <div className="criteria-count">{passed}/{total} Criteria</div>
        </div>
      </div>

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

      {ev.some(e => e.evidence) && (
        <div className="evidence-section">
          <div className="evidence-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            Verified Evidence Snippets
          </div>
          <div className="evidence-items">
            {ev.filter(e => e.evidence && e.evidence !== 'No direct match found').map((e, i) => (
              <div key={i} className={`evidence-item ${e.result}`}>
                <div>
                  <div className="evidence-text">
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {e.criterion?.replace(/\b\w/g, c => c.toUpperCase())}
                    </strong>{' '}
                    — &ldquo;{e.evidence}&rdquo;
                  </div>
                  {e.page && <div className="evidence-page">Page {e.page}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="review-footer">
        <div className="review-hint">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          Pending final human determination
        </div>
        <div className="review-actions">
          <button className="btn btn-approve" onClick={() => onReview(filename, 'Eligible')}>Approve</button>
          <button className="btn btn-reject" onClick={() => onReview(filename, 'Not Eligible')}>Mark Not Eligible</button>
          <button className="btn btn-review" onClick={() => onReview(filename, 'Needs Review')}>Needs Review</button>
        </div>
      </div>
    </div>
  );
}

export default function CombinedPage() {
  const [tenderFile, setTenderFile] = useState(null);
  const [bidderFiles, setBidderFiles] = useState([]);
  const [running, setRunning] = useState(false);
  const [statusMsgs, setStatusMsgs] = useState([]);
  const [results, setResults] = useState([]);
  const [dragOver, setDragOver] = useState(false);

  const addStatus = (msg, type = 'info') =>
    setStatusMsgs(prev => [...prev, { msg, type }]);

  const addBidderFile = (file) => {
    if (file) setBidderFiles(prev => [...prev, file]);
  };

  const removeBidder = (idx) =>
    setBidderFiles(prev => prev.filter((_, i) => i !== idx));

  const loadResults = async () => {
    try {
      const res = await fetch(`${API}/results`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      }
    } catch { /* silent */ }
  };

  const runPipeline = async () => {
    if (!tenderFile) { addStatus('Upload a tender document first.', 'error'); return; }
    if (!bidderFiles.length) { addStatus('Upload at least one bidder document.', 'error'); return; }

    setRunning(true);
    setStatusMsgs([]);
    setResults([]);

    try {
      addStatus('Uploading documents...', 'info');
      const form = new FormData();
      form.append('tender_file', tenderFile);
      bidderFiles.forEach(f => form.append('bidder_files', f));
      const uploadRes = await fetch(`${API}/upload`, { method: 'POST', body: form });
      if (!uploadRes.ok) throw new Error(`Upload failed: ${await uploadRes.text()}`);
      addStatus('Documents uploaded successfully.', 'success');

      addStatus('Running OCR text extraction...', 'info');
      const processRes = await fetch(`${API}/process`, { method: 'POST' });
      if (!processRes.ok) throw new Error(`OCR failed: ${await processRes.text()}`);
      addStatus('OCR processing complete.', 'success');

      addStatus('Extracting structured data via LLM...', 'info');
      const extractRes = await fetch(`${API}/extract`, { method: 'POST' });
      if (!extractRes.ok) throw new Error(`Extraction failed: ${await extractRes.text()}`);
      addStatus('LLM extraction complete.', 'success');

      addStatus('Running rule engine evaluation...', 'info');
      const evalRes = await fetch(`${API}/evaluate`, { method: 'POST' });
      if (!evalRes.ok) throw new Error(`Evaluation failed: ${await evalRes.text()}`);
      addStatus('Evaluation complete.', 'success');

      await loadResults();
    } catch (err) {
      addStatus(err.message, 'error');
    } finally {
      setRunning(false);
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
        addStatus(`Marked "${filename.replace('.json', '')}" as ${status}.`, 'success');
        await loadResults();
      } else {
        addStatus(`Review failed: ${await res.text()}`, 'error');
      }
    } catch (err) {
      addStatus(err.message, 'error');
    }
  };

  const scrollToApp = () => {
    document.getElementById('app-section').scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="landing-logo">TrustGraph AI</div>
      </nav>

      {/* Hero Section */}
      <main className="hero" style={{ minHeight: '100vh' }}>
        <div className="hero-glow" />
        <span className="section-tag">Next-Gen Evaluation</span>
        <h1>Revolutionizing Tender Compliance with Explainable AI</h1>
        <p>
          Automate the tedious process of bidder evaluation with our precision engine. 
          Upload documents, extract critical data, and get instant, verifiable eligibility reports.
        </p>
        <div className="hero-image-container" style={{ animation: 'slideUp 0.8s ease-out 0.3s backwards', maxWidth: '800px', marginTop: '40px' }}>
           <img src="/hero.png" alt="TrustGraph AI Evaluation" style={{ maxWidth: '100%', borderRadius: '20px', boxShadow: '0 20px 50px rgba(0,0,0,0.5)', border: '1px solid var(--border-bright)' }} />
        </div>
        <div className="scroll-hint" style={{ marginTop: '40px', animation: 'bounce 2s infinite' }}>
           <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ opacity: 0.5 }}>
              <path d="M7 13l5 5 5-5M7 6l5 5 5-5" />
           </svg>
        </div>
      </main>

      {/* App Section */}
      <section id="app-section" className="main" style={{ background: 'var(--bg-primary)', padding: '80px 0' }}>
        <div className="content" style={{ margin: '0 auto', maxWidth: '1100px' }}>
          <div className="page-header" style={{ textAlign: 'center', marginBottom: '60px' }}>
            <span className="section-tag">Dashboard</span>
            <h1 style={{ fontSize: '40px' }}>TrustGraph AI System</h1>
            <p>Automated eligibility analysis with explainable AI engine.</p>
          </div>

          <div className="upload-grid">
            <div className="upload-card">
              <div className="upload-card-label">Tender Document</div>
              {!tenderFile ? (
                <div
                  className={`upload-drop-zone ${dragOver ? 'drag-over' : ''}`}
                  onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={e => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) setTenderFile(e.dataTransfer.files[0]); }}
                >
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg"
                    onChange={e => { if (e.target.files[0]) setTenderFile(e.target.files[0]); }} />
                  <div className="upload-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.4">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="17 8 12 3 7 8" />
                      <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                  </div>
                  <p>Drag and drop tender RFP or <a>browse files</a></p>
                </div>
              ) : (
                <div className="file-item">
                  <div className="file-item-name">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.6">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    <span>{tenderFile.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="file-item-size">{formatBytes(tenderFile.size)}</span>
                    <button className="file-remove" onClick={() => setTenderFile(null)}>x</button>
                  </div>
                </div>
              )}
            </div>

            <div className="upload-card">
              <div className="upload-card-label">Bidder Documents</div>
              <div className="file-list">
                {bidderFiles.map((f, i) => (
                  <div key={i} className="file-item">
                    <div className="file-item-name">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.6">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <span>{f.name}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="file-item-size">{formatBytes(f.size)}</span>
                      <button className="file-remove" onClick={() => removeBidder(i)}>x</button>
                    </div>
                  </div>
                ))}
                <label className="add-file-btn">
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg" multiple
                    onChange={e => Array.from(e.target.files).forEach(addBidderFile)} />
                  + Add Bidder Document
                </label>
              </div>
            </div>
          </div>

          <div className="run-section">
            <button className="run-btn" onClick={runPipeline} disabled={running}>
              {running
                ? <><span className="spinner" /> Running Evaluation...</>
                : <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                  Run Evaluation
                </>
              }
            </button>
          </div>

          {statusMsgs.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              {statusMsgs.map((s, i) => (
                <div key={i} className={`status-message ${s.type}`}>
                  {s.type === 'success' ? '[OK]' : s.type === 'error' ? '[ERR]' : '[...]'} {s.msg}
                </div>
              ))}
            </div>
          )}

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
        </div>
      </section>

      <footer className="landing-footer" style={{ background: 'var(--bg-secondary)' }}>
        <p>&copy; 2026 TrustGraph AI Engine. Empowering Bharat with Intelligent Procurement.</p>
      </footer>

      <style jsx global>{`
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
          40% {transform: translateY(-10px);}
          60% {transform: translateY(-5px);}
        }
      `}</style>
    </div>
  );
}
