import React, { useRef, useState, useImperativeHandle, forwardRef } from 'react';

// 단계별 라벨 정의
const stepLabels = [
  '문서 인식',
  '의도 분류',
  '질의응답',
  '컴플라이언스 평가',
  '티켓 생성',
  '에스컬레이션',
];

const WorkflowRunner = forwardRef(function WorkflowRunner({ onResult }, ref) {
  const fileInput = useRef();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progressStep, setProgressStep] = useState(0);
  const [fileError, setFileError] = useState(null);

  useImperativeHandle(ref, () => ({
    setFile: (file) => {
      if (fileInput.current) {
        // 파일 확장자, MIME, 내용까지 3중 체크
        const ext = file.name.split('.').pop().toLowerCase();
        if (!["md","txt","pdf"].includes(ext)) {
          setFileError('지원하지 않는 파일 형식입니다. (PDF/MD/TXT만 허용)');
          fileInput.current.value = '';
          return;
        }
        if (file.type && !["text/plain","text/markdown","application/pdf"].includes(file.type)) {
          setFileError('지원하지 않는 파일 타입입니다.');
          fileInput.current.value = '';
          return;
        }
        const reader = new window.FileReader();
        reader.onload = (ev) => {
          const content = ev.target.result;
          if (
            content.includes('<!DOCTYPE html') ||
            content.includes('<html')
          ) {
            setFileError('HTML 파일은 업로드할 수 없습니다. (마크다운/텍스트만 허용)');
            fileInput.current.value = '';
            return;
          }
          // 정상 파일만 실제로 input에 세팅
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(file);
          fileInput.current.files = dataTransfer.files;
        };
        reader.readAsText(file);
      }
    }
  }));

  // 단계별 진행상황 애니메이션 (실제 백엔드 단계별 진행상황 연동 시 대체 가능)
  function simulateProgress() {
    setProgressStep(0);
    let step = 0;
    const interval = setInterval(() => {
      step++;
      setProgressStep(step);
      if (step >= stepLabels.length) {
        clearInterval(interval);
      }
    }, 400); // 단계별 0.4초씩
    return interval;
  }

  const handleFileChange = (e) => {
    setFileError(null);
    const file = e.target.files[0];
    if (file) {
      // 파일 확장자, MIME, 내용까지 3중 체크
      const ext = file.name.split('.').pop().toLowerCase();
      if (!["md","txt","pdf"].includes(ext)) {
        setFileError('지원하지 않는 파일 형식입니다. (PDF/MD/TXT만 허용)');
        fileInput.current.value = '';
        return;
      }
      if (file.type && !["text/plain","text/markdown","application/pdf"].includes(file.type)) {
        setFileError('지원하지 않는 파일 타입입니다.');
        fileInput.current.value = '';
        return;
      }
      const reader = new window.FileReader();
      reader.onload = (ev) => {
        const content = ev.target.result;
        if (
          content.includes('<!DOCTYPE html') ||
          content.includes('<html')
        ) {
          setFileError('HTML 파일은 업로드할 수 없습니다. (마크다운/텍스트만 허용)');
          fileInput.current.value = '';
        }
      };
      reader.readAsText(file);
    }
  };

  // 워크플로우 실행 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setProgressStep(0);
    let interval = simulateProgress();
    const formData = new FormData();
    if (fileInput.current.files[0]) {
      formData.append('file', fileInput.current.files[0]);
    } else if (text.trim()) {
      formData.append('text', text);
    } else {
      setError('파일 또는 텍스트를 입력하세요.');
      setLoading(false);
      clearInterval(interval);
      return;
    }
    try {
      const res = await fetch('/run_workflow', {
        method: 'POST',
        body: formData,
      });
      const contentType = res.headers.get('content-type');
      const raw = await res.text();
      if (raw.includes('<!DOCTYPE html') || raw.includes('<html')) {
        throw new Error('서버에서 HTML이 반환되었습니다. (API 라우팅/프록시/서버 에러 가능성)');
      }
      let data;
      try {
        data = JSON.parse(raw);
      } catch (e) {
        throw new Error('API 응답이 올바른 JSON이 아닙니다. (원본: ' + raw.slice(0, 100) + ')');
      }
      clearInterval(interval);
      setProgressStep(stepLabels.length);
      if (data.error) setError(data.error);
      else onResult(data.result);
    } catch (err) {
      clearInterval(interval);
      setError('API 호출 실패: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 24, background: '#fff', padding: 16, borderRadius: 8, border: '1px solid #eee' }} aria-label="문서 업로드 및 워크플로우 실행 폼">
      <div style={{ marginBottom: 8 }}>
        <label style={{ fontWeight: 'bold', marginRight: 8 }} htmlFor="file-upload">문서 업로드 (PDF/MD):</label>
        <input
          type="file"
          ref={fileInput}
          accept=".pdf,.md,.txt"
          id="file-upload"
          aria-label="문서 파일 업로드"
          onChange={handleFileChange}
        />
      </div>
      {fileError && <div style={{ color: 'red', marginTop: 4 }}>{fileError}</div>}
      <div style={{ marginBottom: 8 }}>
        <label style={{ fontWeight: 'bold', marginRight: 8 }} htmlFor="text-input">또는 텍스트 입력:</label>
        <textarea value={text} onChange={e => setText(e.target.value)} rows={3} style={{ width: '100%', resize: 'vertical' }} id="text-input" aria-label="텍스트 입력" />
      </div>
      <button type="submit" disabled={loading} style={{ padding: '8px 20px', fontWeight: 'bold', background: '#1890ff', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }} aria-label="워크플로우 실행">
        {loading ? '실행 중...' : '워크플로우 실행'}
      </button>
      {loading && (
        <div style={{ marginTop: 12, marginBottom: 4 }} aria-label="단계별 진행상황">
          <ProgressSteps current={progressStep} error={error} />
        </div>
      )}
      {error && <div style={{ color: 'red', marginTop: 8 }} aria-label="에러 메시지">{error}</div>}
    </form>
  );
});

export default WorkflowRunner;

// 단계별 진행상황 시각화 컴포넌트
function ProgressSteps({ current, error }) {
  return (
    <ol style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'row', gap: 8 }} aria-label="진행 단계">
      {stepLabels.map((label, idx) => {
        let color = '#bfbfbf';
        let icon = '●';
        if (error && current - 1 === idx) {
          color = '#ff4d4f';
          icon = '✖';
        } else if (current > idx) {
          color = '#52c41a';
          icon = '✔';
        } else if (current === idx) {
          color = '#1890ff';
          icon = '▶';
        }
        return (
          <li key={label} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 60 }} aria-label={`단계: ${label}`}>
            <span style={{ color, fontWeight: 'bold', fontSize: 18 }}>{icon}</span>
            <span style={{ color, fontSize: 12 }}>{label}</span>
          </li>
        );
      })}
    </ol>
  );
} 