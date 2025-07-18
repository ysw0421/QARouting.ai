import React, { useState } from 'react';
import './App.css';
import FileList from './components/FileList';
import TopologyDiagram from './components/TopologyDiagram';
import ResultDetail from './components/ResultDetail';
import WorkflowRunner from './components/WorkflowRunner';
import BenchmarkResult from './components/BenchmarkResult';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [workflowResult, setWorkflowResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [selectedBenchmark, setSelectedBenchmark] = useState(null);

  // Handle file click: run workflow with selected file
  const handleFileSelect = async (filename) => {
    setSelectedFile({ name: filename });
    setWorkflowResult(null);
    setBenchmarkResult(null);
    setSelectedBenchmark(null);
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', new File([], filename)); // Placeholder, will be replaced below
      // Instead of sending empty File, use fetch to get the file from uploads/ and send as Blob
      const fileRes = await fetch(`/uploads/${filename}`);
      if (!fileRes.ok) throw new Error('파일을 읽을 수 없습니다.');
      const blob = await fileRes.blob();
      formData.set('file', new File([blob], filename));
      const res = await fetch('http://localhost:8000/run_workflow', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setWorkflowResult(data.result);
    } catch (err) {
      setError('워크플로우 실행 실패: ' + err.message);
    } finally {
      setLoading(false);
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
      // 벤치마크 파일은 /uploads/ 또는 /results/ 등에서 가져옴
      let res = await fetch(`/uploads/${filename}`);
      if (!res.ok) {
        // fallback: /results/
        res = await fetch(`/results/${filename}`);
      }
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
        <WorkflowRunner onResult={setWorkflowResult} />
        {loading && <div style={{ color: '#1890ff', fontWeight: 'bold', marginBottom: 12 }}>워크플로우 실행 중...</div>}
        {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
        {/* 벤치마크 결과가 선택된 경우 우선 표시 */}
        {benchmarkResult && selectedBenchmark && (
          <BenchmarkResult resultData={benchmarkResult} filename={selectedBenchmark} />
        )}
        {/* 일반 워크플로우 결과만 있을 때만 토폴로지/상세 표시 */}
        {!benchmarkResult && (
          <>
            <TopologyDiagram workflowResult={workflowResult} />
            <ResultDetail workflowResult={workflowResult} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
