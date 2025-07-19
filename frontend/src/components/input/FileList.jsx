import React, { useEffect, useState } from 'react';
import BenchmarkCaseManager from '../result/BenchmarkCaseManager';

export default function FileList({ onSelect, selectedId, onFileSelect, onBenchmarkSelect }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBenchmarkManager, setShowBenchmarkManager] = useState(false);

  useEffect(() => {
    async function fetchFiles() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('http://localhost:8000/api/files');
        const data = await res.json();
        setFiles(data.files || []);
      } catch (err) {
        setError('파일 목록을 불러오지 못했습니다.');
      } finally {
        setLoading(false);
      }
    }
    fetchFiles();
  }, []);

  // 벤치마크 파일 구분 (예: benchmark, result, _user_ 등 포함)
  function isBenchmarkFile(file) {
    return file.endsWith('.json') && (file.includes('benchmark') || file.includes('result'));
  }

  return (
    <div style={{ width: '220px', borderRight: '1px solid #eee', height: '100vh', overflowY: 'auto', background: '#fafbfc' }}>
      <h3 style={{ padding: '16px 12px 8px', margin: 0, fontSize: '1.1em', color: '#333' }}>Result Files</h3>
      {loading && <div style={{ padding: 16, color: '#888' }}>Loading...</div>}
      {error && <div style={{ padding: 16, color: 'red' }}>{error}</div>}
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {files.map((file, idx) => (
          <li
            key={file}
            onClick={() => isBenchmarkFile(file)
              ? onBenchmarkSelect && onBenchmarkSelect(file)
              : (onFileSelect ? onFileSelect(file) : onSelect({ id: idx + 1, name: file }))}
            style={{
              padding: '10px 16px',
              cursor: 'pointer',
              background: selectedId === (idx + 1) ? '#e6f7ff' : 'transparent',
              color: isBenchmarkFile(file) ? '#faad14' : (selectedId === (idx + 1) ? '#1890ff' : '#222'),
              fontWeight: isBenchmarkFile(file) ? 'bold' : (selectedId === (idx + 1) ? 'bold' : 'normal'),
              borderLeft: isBenchmarkFile(file)
                ? '4px solid #faad14'
                : (selectedId === (idx + 1) ? '4px solid #1890ff' : '4px solid transparent'),
              transition: 'background 0.2s, color 0.2s',
            }}
            title={isBenchmarkFile(file) ? '벤치마크/테스트 결과 파일' : '일반 결과 파일'}
          >
            {isBenchmarkFile(file) ? <span>🧪 {file}</span> : file}
          </li>
        ))}
      </ul>
      <button onClick={() => setShowBenchmarkManager(true)}>
        Manage Benchmark Cases
      </button>
      {showBenchmarkManager && (
        <BenchmarkCaseManager onClose={() => setShowBenchmarkManager(false)} />
      )}
    </div>
  );
} 