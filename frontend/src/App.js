import React, { useState, useRef } from 'react';
import './App.css';
import FileList from './components/input/FileList';
import TopologyDiagram from './components/visualization/TopologyDiagram';
import ResultDetail from './components/result/ResultDetail';
import WorkflowRunner from './components/input/WorkflowRunner';
import BenchmarkResult from './components/result/BenchmarkResult';
import LegalWorkflowDiagram from './components/visualization/LegalWorkflowDiagram';

const BENCHMARK_FILES = [
  { label: '전체 결과', file: 'benchmark_results.json' },
  { label: '실패 케이스', file: 'benchmark_failures.json' },
];

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [workflowResult, setWorkflowResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [selectedBenchmark, setSelectedBenchmark] = useState(null);
  const workflowRunnerRef = useRef();

  // Handle file click: set file in WorkflowRunner input
  const handleFileSelect = async (filename) => {
    setSelectedFile({ name: filename });
    setWorkflowResult(null);
    setBenchmarkResult(null);
    setSelectedBenchmark(null);
    setError(null);
    try {
      const fileRes = await fetch(`/uploads/${filename}`);
      if (!fileRes.ok) throw new Error('파일을 읽을 수 없습니다.');
      const blob = await fileRes.blob();
      // 파일 내용이 HTML인지 사전 체크
      const text = await blob.text();
      if (text.includes('<!DOCTYPE html') || text.includes('<html')) {
        setError('업로드 파일이 HTML로 인식됩니다. 서버에 index.html이 잘못 저장된 것일 수 있습니다.');
        return;
      }
      const file = new File([blob], filename);
      if (workflowRunnerRef.current && workflowRunnerRef.current.setFile) {
        workflowRunnerRef.current.setFile(file);
      }
    } catch (err) {
      setError('파일 불러오기 실패: ' + err.message);
    }
  };

  // 벤치마크 파일 클릭 시
  const handleBenchmarkSelect = async (filename) => {
    setSelectedFile(null);
    setWorkflowResult(null);
    setBenchmarkResult(null);
    setSelectedBenchmark(filename);
    setLoading(true);
    setError(null);
    try {
      // 벤치마크 파일은 /results/ 또는 /uploads/ 또는 /eval/ 등에서 가져옴
      let res = await fetch(`/results/${filename}`);
      if (!res.ok) res = await fetch(`/uploads/${filename}`);
      if (!res.ok) res = await fetch(`/eval/${filename}`);
      if (!res.ok) throw new Error('벤치마크 파일을 읽을 수 없습니다.');
      const data = await res.json();
      setBenchmarkResult(data);
    } catch (err) {
      setError('벤치마크 결과 불러오기 실패: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f4f6f8' }}>
      <FileList
        onSelect={file => setSelectedFile(file)}
        selectedId={selectedFile?.id}
        onFileSelect={handleFileSelect}
        onBenchmarkSelect={handleBenchmarkSelect}
      />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 32, overflow: 'auto' }}>
        <WorkflowRunner ref={workflowRunnerRef} onResult={setWorkflowResult} />
        <div style={{ marginBottom: 16 }}>
          <span style={{ fontWeight: 'bold', marginRight: 8 }}>벤치마크 파일:</span>
          {BENCHMARK_FILES.map(bf => (
            <button
              key={bf.file}
              style={{
                marginRight: 8,
                padding: '4px 12px',
                border: selectedBenchmark === bf.file ? '2px solid #1890ff' : '1px solid #bbb',
                borderRadius: 4,
                background: selectedBenchmark === bf.file ? '#e6f7ff' : '#fafbfc',
                cursor: 'pointer',
                fontWeight: selectedBenchmark === bf.file ? 'bold' : undefined,
              }}
              onClick={() => handleBenchmarkSelect(bf.file)}
            >
              {bf.label}
            </button>
          ))}
        </div>
        {loading && <div style={{ color: '#1890ff', fontWeight: 'bold', marginBottom: 12 }}>워크플로우 실행 중...</div>}
        {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
        {/* 벤치마크 결과가 선택된 경우 우선 표시 */}
        {benchmarkResult && selectedBenchmark && (
          <BenchmarkResult resultData={benchmarkResult} filename={selectedBenchmark} />
        )}
        {/* 일반 워크플로우 결과만 있을 때만 토폴로지/상세 표시 */}
        {!benchmarkResult && (
          <>
            <LegalWorkflowDiagram workflowResult={workflowResult} />
            <TopologyDiagram workflowResult={workflowResult} />
            <ResultDetail workflowResult={workflowResult} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
