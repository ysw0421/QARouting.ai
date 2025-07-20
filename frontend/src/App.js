import React, { useState, useRef } from 'react';
import './App.css';
import FileList from './components/input/FileList';
import TopologyDiagram from './components/visualization/TopologyDiagram';
import ResultDetail from './components/result/ResultDetail';
import WorkflowRunner from './components/input/WorkflowRunner';
import BenchmarkResult from './components/result/BenchmarkResult';
import dayjs from 'dayjs';

const BENCHMARK_FILES = [
  { label: '전체 결과', file: 'benchmark_results.json' },
  { label: '실패 케이스', file: 'benchmark_failures.json' },
];

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [workflowResult, setWorkflowResult] = useState(null);
  const [loading, setLoading] = useState(false);
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
    // 서버 파일 실행: 파일명만 setFile에 전달
    if (workflowRunnerRef.current && workflowRunnerRef.current.setFile) {
      workflowRunnerRef.current.setFile(filename);
    }
  };

  // 벤치마크 파일 클릭 시
  const handleBenchmarkSelect = async (filename) => {
    setSelectedFile(null);
    setWorkflowResult({ loading: true });
    setBenchmarkResult(null);
    setSelectedBenchmark(filename);
    setLoading(true);
    try {
      let res = await fetch(`/results/${filename}`);
      if (!res.ok) res = await fetch(`/uploads/${filename}`);
      if (!res.ok) res = await fetch(`/eval/${filename}`);
      if (!res.ok) throw new Error('벤치마크 파일을 읽을 수 없습니다.');
      const data = await res.json();
      setBenchmarkResult(data);
      if (Array.isArray(data)) {
        // Find first valid case with at least one key field
        const valid = data.find(
          d => d && (d.file_path || d.text || d.intent || d.assessment || d.ticket || d.escalation)
        );
        if (valid) {
          setWorkflowResult(valid);
        } else {
          setWorkflowResult({ error: "벤치마크 케이스에 유효한 결과가 없습니다." });
        }
      } else if (data && (
        data.file_path || data.text || data.intent || data.assessment || data.ticket || data.escalation
      )) {
        setWorkflowResult(data);
      } else {
        setWorkflowResult({ error: "벤치마크 케이스에 유효한 결과가 없습니다." });
      }
    } catch (err) {
      setWorkflowResult({ error: "벤치마크 결과 불러오기 실패: " + err.message });
    } finally {
      setLoading(false);
    }
  };

  // 워크플로우 결과가 새로 생성될 때 uploads/에 저장
  React.useEffect(() => {
    if (workflowResult && !benchmarkResult) {
      const save = async () => {
        const ts = dayjs().format('YYYYMMDD_HHmmss');
        const filename = `workflow_result_${ts}`;
        try {
          const res = await fetch('/api/save_final_result', {
            method: 'POST',
            body: (() => {
              const form = new FormData();
              form.append('result', new Blob([JSON.stringify(workflowResult)], { type: 'application/json' }));
              form.append('filename', filename);
              return form;
            })(),
          });
          const data = await res.json();
          if (data.success) {
            alert(`최종 결과가 uploads/${filename}.json 으로 저장되었습니다.`);
          } else {
            alert('최종 결과 저장 실패: ' + (data.error || 'Unknown error'));
          }
        } catch (e) {
          alert('최종 결과 저장 중 오류: ' + e.message);
        }
      };
      save();
    }
  }, [workflowResult, benchmarkResult]);

  console.log('App workflowResult:', workflowResult);

  const hasWorkflowResult =
    workflowResult &&
    (
      workflowResult.file_path ||
      workflowResult.text ||
      workflowResult.intent ||
      workflowResult.assessment ||
      workflowResult.ticket ||
      workflowResult.escalation ||
      workflowResult.answer // <-- 추가: simple Q&A 결과도 정상 인식
    );

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
        {/* 에러 메시지 */}
        {workflowResult && workflowResult.error && (
          <div style={{ color: 'red', fontWeight: 700, margin: '12px 0' }}>
            {workflowResult.error}
          </div>
        )}
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
        {/* 워크플로우 결과가 없을 때 메시지 */}
        {!workflowResult?.error && !hasWorkflowResult && (
          <div style={{ color: 'red', fontWeight: 700, margin: '12px 0' }}>
            워크플로우 결과를 받을 수 없습니다.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
