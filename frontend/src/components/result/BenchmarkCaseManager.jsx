import React, { useEffect, useState } from 'react';

export default function BenchmarkCaseManager({ onClose }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editIndex, setEditIndex] = useState(null);
  const [editCase, setEditCase] = useState({ file_type: '', question: '', document_content: '', expected_routing: '', expected_answer: '' });

  useEffect(() => {
    fetch('/api/benchmark_cases')
      .then(res => res.json())
      .then(data => {
        setCases(data.cases || []);
        setLoading(false);
      })
      .catch(e => { setError('Failed to load cases'); setLoading(false); });
  }, []);

  const handleEdit = (idx) => {
    setEditIndex(idx);
    setEditCase({ ...cases[idx] });
  };
  const handleDelete = (idx) => {
    if (!window.confirm('Delete this case?')) return;
    fetch(`/api/benchmark_cases/${idx}`, { method: 'DELETE' })
      .then(() => setCases(cases => cases.filter((_, i) => i !== idx)));
  };
  const handleSave = () => {
    if (editIndex === null) {
      // Add new
      fetch('/api/benchmark_cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editCase)
      })
        .then(res => res.json())
        .then(data => setCases(cases => [...cases, data.case]));
    } else {
      // Edit existing
      fetch(`/api/benchmark_cases/${editIndex}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editCase)
      })
        .then(res => res.json())
        .then(data => setCases(cases => cases.map((c, i) => i === editIndex ? data.case : c)));
    }
    setEditIndex(null);
    setEditCase({ file_type: '', question: '', document_content: '', expected_routing: '', expected_answer: '' });
  };
  const handleAdd = () => {
    setEditIndex(null);
    setEditCase({ file_type: '', question: '', document_content: '', expected_routing: '', expected_answer: '' });
  };
  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.4)', zIndex: 1000 }}>
      <div style={{ background: '#fff', margin: '5vh auto', padding: 24, borderRadius: 8, width: 600, maxHeight: '90vh', overflow: 'auto' }}>
        <h2>Benchmark Case Manager</h2>
        <button onClick={onClose} style={{ float: 'right' }}>Close</button>
        {loading ? <div>Loading...</div> : error ? <div>{error}</div> : (
          <>
            <button onClick={handleAdd}>Add New Case</button>
            <table style={{ width: '100%', marginTop: 16, borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Question</th>
                  <th>Expected Routing</th>
                  <th>Expected Answer</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c, i) => (
                  <tr key={i} style={{ background: editIndex === i ? '#eef' : 'inherit' }}>
                    <td>{c.file_type}</td>
                    <td>{c.question}</td>
                    <td>{c.expected_routing}</td>
                    <td>{c.expected_answer}</td>
                    <td>
                      <button onClick={() => handleEdit(i)}>Edit</button>
                      <button onClick={() => handleDelete(i)} style={{ marginLeft: 8 }}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(editIndex !== null || editCase.question) && (
              <div style={{ marginTop: 24, padding: 16, background: '#f9f9f9', borderRadius: 6 }}>
                <h4>{editIndex === null ? 'Add New Case' : 'Edit Case'}</h4>
                <div>
                  <label>Type: <input value={editCase.file_type} onChange={e => setEditCase(ec => ({ ...ec, file_type: e.target.value }))} placeholder="md/pdf" /></label>
                </div>
                <div>
                  <label>Question: <input value={editCase.question} onChange={e => setEditCase(ec => ({ ...ec, question: e.target.value }))} style={{ width: 300 }} /></label>
                </div>
                <div>
                  <label>Expected Routing: <input value={editCase.expected_routing} onChange={e => setEditCase(ec => ({ ...ec, expected_routing: e.target.value }))} /></label>
                </div>
                <div>
                  <label>Expected Answer: <input value={editCase.expected_answer} onChange={e => setEditCase(ec => ({ ...ec, expected_answer: e.target.value }))} style={{ width: 300 }} /></label>
                </div>
                <div>
                  <label>Document Content:<br />
                    <textarea value={editCase.document_content} onChange={e => setEditCase(ec => ({ ...ec, document_content: e.target.value }))} rows={6} style={{ width: '100%' }} />
                  </label>
                </div>
                <button onClick={handleSave} style={{ marginTop: 8 }}>Save</button>
                <button onClick={() => { setEditIndex(null); setEditCase({ file_type: '', question: '', document_content: '', expected_routing: '', expected_answer: '' }); }} style={{ marginLeft: 8 }}>Cancel</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 