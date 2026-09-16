import React, { useState, useRef } from 'react';

export default function App() {
  const [file, setFile] = useState(null);
  const [fileStats, setFileStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);
  const [confThreshold, setConfThreshold] = useState(0.5);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (selectedFile) => {
    setError('');
    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please upload a valid CSV file.');
      return;
    }
    setFile(selectedFile);
    
    // Quick parse for preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split('\n');
      if (lines.length > 0) {
        const headers = lines[0].split(',').map(h => h.trim());
        setFileStats({
          rows: lines.length - 1, // minus header
          cols: headers.length,
          headers: headers,
          hasAnswer: headers.includes('answer')
        });
      }
    };
    reader.readAsText(selectedFile);
  };

  const handlePredict = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    setResults(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8002';
      const res = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to get predictions');
      }
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!results || !results.predictions) return;
    
    let csvContent = "id,prediction\n";
    results.predictions.forEach(p => {
      csvContent += `${p.id},${p.prediction.join(' ')}\n`;
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'predictions.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container">
      <header>
        <h1>Science Question Answer Predictor</h1>
        <p className="subtitle">Upload multiple-choice science questions and get AI-powered answer predictions.</p>
      </header>

      {/* Upload Section */}
      <div className="card">
        <div 
          className="upload-area"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <div className="upload-icon">📁</div>
          <h3>Upload your test CSV</h3>
          <p className="subtitle">Click to browse or drag and drop here</p>
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            style={{ display: 'none' }} 
          />
        </div>
        
        {fileStats && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f9fafb', borderRadius: '6px' }}>
            <h4 style={{ marginBottom: '0.5rem' }}>Data Preview</h4>
            <p><strong>Filename:</strong> {file.name}</p>
            <p><strong>Dataset:</strong> ~{fileStats.rows} questions</p>
            <p><strong>Columns:</strong> {fileStats.cols} ({fileStats.headers.slice(0,5).join(', ')}{fileStats.cols > 5 ? '...' : ''})</p>
            <p><strong>Ground truth:</strong> {fileStats.hasAnswer ? <span className="badge badge-success">Available</span> : <span className="badge badge-danger">Not provided</span>}</p>
          </div>
        )}

        {error && <div className="error-text">{error}</div>}

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <button 
            className="btn" 
            onClick={(e) => { e.stopPropagation(); handlePredict(); }} 
            disabled={!file || loading}
          >
            {loading ? 'Running model...' : 'Predict'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <>
          {results.metrics && (
            <div className="card">
              <h2>Evaluation Mode</h2>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">{(results.metrics.accuracy * 100).toFixed(2)}%</div>
                  <div className="metric-label">Accuracy</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{(results.metrics.map_at_3 * 100).toFixed(2)}%</div>
                  <div className="metric-label">MAP@3</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{(results.metrics.top_3_accuracy * 100).toFixed(2)}%</div>
                  <div className="metric-label">Top-3 Accuracy</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{(results.metrics.macro_f1 * 100).toFixed(2)}%</div>
                  <div className="metric-label">Macro F1</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{results.metrics.log_loss.toFixed(3)}</div>
                  <div className="metric-label">Log Loss</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{results.metrics.rmse_encoded.toFixed(3)}</div>
                  <div className="metric-label">RMSE (Encoded Classes)</div>
                  <p style={{fontSize:'0.75rem', color:'#6b7280', marginTop:'0.5rem'}}>Auxiliary metric encoding A-E as 0-4.</p>
                </div>
              </div>

              {/* Confusion Matrix */}
              {results.metrics.confusion_matrix && (
                <div style={{marginTop: '2rem'}}>
                  <h3>Confusion Matrix</h3>
                  <div className="cm-container" style={{marginTop: '1rem'}}>
                    <table className="cm-table">
                      <thead>
                        <tr>
                          <th></th>
                          <th>Pred A</th><th>Pred B</th><th>Pred C</th><th>Pred D</th><th>Pred E</th>
                        </tr>
                      </thead>
                      <tbody>
                        {['Actual A','Actual B','Actual C','Actual D','Actual E'].map((label, i) => (
                          <tr key={i}>
                            <th>{label}</th>
                            {results.metrics.confusion_matrix[i].map((val, j) => {
                              // Calculate intensity for heatmap
                              const maxVal = Math.max(...results.metrics.confusion_matrix.flat());
                              const intensity = val / (maxVal || 1);
                              const bg = `rgba(79, 70, 229, ${intensity * 0.8})`;
                              const color = intensity > 0.5 ? '#fff' : '#000';
                              return (
                                <td key={j} title={`Actual: ${label.split(' ')[1]}, Pred: ${['A','B','C','D','E'][j]}, Count: ${val}`}>
                                  <div className="cm-cell" style={{backgroundColor: bg, color: color}}>
                                    {val}
                                  </div>
                                </td>
                              )
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {!results.metrics && (
             <div className="card">
               <h2>Prediction Mode</h2>
               <p className="subtitle">No ground truth provided. Showing model predictions only.</p>
             </div>
          )}

          <div className="card">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
              <h2>Predictions Table</h2>
              <button className="btn" onClick={handleDownload}>Download Predictions CSV</button>
            </div>
            
            <div style={{overflowX: 'auto'}}>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Question (truncated)</th>
                    <th>Top</th>
                    <th>2nd</th>
                    <th>3rd</th>
                    <th>Confidence</th>
                    {results.metrics && <th>Match</th>}
                  </tr>
                </thead>
                <tbody>
                  {results.predictions.map((p, idx) => (
                    <React.Fragment key={idx}>
                      <tr className="expandable-row" onClick={() => setExpandedRow(expandedRow === idx ? null : idx)}>
                        <td>{p.id}</td>
                        <td>{p.prompt ? p.prompt.substring(0, 40) + '...' : '-'}</td>
                        <td><span className="badge badge-primary">{p.prediction[0]}</span></td>
                        <td>{p.prediction[1]}</td>
                        <td>{p.prediction[2]}</td>
                        <td>{(p.confidence * 100).toFixed(1)}%</td>
                        {results.metrics && (
                          <td>
                            {p.correct ? <span className="badge badge-success">Top 1</span> 
                              : p.top_3_correct ? <span className="badge badge-primary">Top 3</span> 
                              : <span className="badge badge-danger">Miss</span>}
                          </td>
                        )}
                      </tr>
                      {expandedRow === idx && (
                        <tr className="details-row">
                          <td colSpan={results.metrics ? "7" : "6"}>
                            <div className="details-content">
                              <h4 style={{marginBottom:'1rem'}}>Class Probabilities</h4>
                              {['A','B','C','D','E'].map(opt => (
                                <div className="prob-bar-container" key={opt}>
                                  <div className="prob-label">{opt}</div>
                                  <div className="prob-track">
                                    <div className="prob-fill" style={{width: `${p.probabilities[opt]*100}%`}}></div>
                                  </div>
                                  <div className="prob-val">{(p.probabilities[opt]*100).toFixed(1)}%</div>
                                </div>
                              ))}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="card">
             <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
               <h2>Low Confidence Predictions</h2>
               <div>
                  Threshold: <input type="number" min="0" max="1" step="0.05" value={confThreshold} onChange={e => setConfThreshold(parseFloat(e.target.value))} style={{width:'60px', marginLeft:'10px'}} />
               </div>
             </div>
             
             <div style={{overflowX: 'auto', marginTop: '1rem'}}>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Top Pred</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {results.predictions.filter(p => p.confidence < confThreshold).map((p, idx) => (
                    <tr key={idx}>
                      <td>{p.id}</td>
                      <td>{p.prediction[0]}</td>
                      <td>{(p.confidence * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                  {results.predictions.filter(p => p.confidence < confThreshold).length === 0 && (
                    <tr><td colSpan="3" style={{textAlign:'center'}}>No predictions below threshold.</td></tr>
                  )}
                </tbody>
              </table>
             </div>
          </div>
        </>
      )}
    </div>
  );
}
