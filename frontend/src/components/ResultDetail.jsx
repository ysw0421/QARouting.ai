import React from 'react';

const stepDefs = [
  { key: 'text', label: '문서 인식' },
  { key: 'intent', label: '의도 분류' },
  { key: 'answer', label: '질의응답' },
  { key: 'assessment', label: '컴플라이언스 평가' },
  { key: 'ticket', label: '티켓 생성' },
  { key: 'escalation', label: '에스컬레이션' },
];

// 워크플로우 결과에서 언어 감지 (간단 버전)
function detectLanguageFromResult(result) {
  if (result && result.answer_lang) return result.answer_lang;
  if (result && result.answer) {
    const answer = result.answer;
    if (/[a-zA-Z]/.test(answer)) return '영어';
    if (/[\uac00-\ud7af]/.test(answer)) return '한글';
    if (/[\u3040-\u30ff\u31f0-\u31ff\u4e00-\u9faf]/.test(answer)) return '일본어';
  }
  return '미확인';
}

// 결과를 JSON 파일로 다운로드
function downloadResultAsJson(result) {
  const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const now = new Date();
  const pad = n => n.toString().padStart(2, '0');
  const fname = `workflow_result_${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}.json`;
  const a = document.createElement('a');
  a.href = url;
  a.download = fname;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 100);
}

export default function ResultDetail({ workflowResult }) {
  if (!workflowResult) {
    return <div style={{ color: '#888', padding: 24 }} aria-label="결과 없음">결과를 선택하거나 실행하세요.</div>;
  }
  // 다국어/엣지케이스 정보 추출
  const lang = detectLanguageFromResult(workflowResult);
  const intent = workflowResult.intent || '-';
  const escalation = workflowResult.escalation ? '예' : '아니오';
  // 일본어/한자 포함 여부로 엣지케이스 감지
  const edgecase = (workflowResult.text && /[\u3040-\u30ff\u31f0-\u31ff\u4e00-\u9faf]/.test(workflowResult.text)) ? '다국어 문서' : '';

  // 단계별 상태 추정
  const steps = stepDefs.map(def => {
    let status = 'notrun';
    if (workflowResult[def.key]) status = 'success';
    if (workflowResult.error && isErrorStep(def.key, workflowResult)) status = 'error';
    if (status === 'notrun' && hasPrevError(def.key, workflowResult)) status = 'pending';
    return {
      ...def,
      status,
      data: workflowResult[def.key],
      error: workflowResult.error && isErrorStep(def.key, workflowResult) ? workflowResult.error : null,
    };
  });
  return (
    <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 8, padding: 16 }} role="region" aria-label="워크플로우 결과 상세">
      {/* 다국어/엣지케이스 정보 박스 + 다운로드 버튼 */}
      <div style={{ background: '#f6f8fa', border: '1px solid #eee', borderRadius: 6, padding: 10, marginBottom: 16, display: 'flex', gap: 24, fontSize: 14, alignItems: 'center', justifyContent: 'space-between' }} aria-label="분석 정보 및 다운로드">
        <div style={{ display: 'flex', gap: 24 }}>
          <div><b>감지 언어:</b> <span style={{ color: '#1890ff' }}>{lang}</span></div>
          <div><b>의도(라우팅):</b> <span style={{ color: '#faad14' }}>{intent}</span></div>
          <div><b>에스컬레이션:</b> <span style={{ color: escalation === '예' ? '#ff4d4f' : '#52c41a' }}>{escalation}</span></div>
          {edgecase && <div><b>엣지케이스:</b> <span style={{ color: '#faad14' }}>{edgecase}</span></div>}
        </div>
        <button onClick={() => downloadResultAsJson(workflowResult)} style={{ padding: '6px 16px', background: '#1890ff', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 'bold', cursor: 'pointer' }} aria-label="결과 파일 다운로드">
          결과 파일 다운로드
        </button>
      </div>
      <h4 style={{ margin: 0, marginBottom: 12, color: '#333' }}>워크플로우 상세</h4>
      <ol style={{ paddingLeft: 20, margin: 0 }} aria-label="단계별 결과">
        {steps.map((s, idx) => (
          <li key={s.key} style={{ marginBottom: 10 }} aria-label={`단계: ${s.label}`}> {/* 단계별 결과 */}
            <div style={{ fontWeight: 'bold', color: '#222' }}>{s.label} <span style={{ fontWeight: 'normal', color: statusColor(s.status), marginLeft: 8 }}>[{s.status}]</span></div>
            <div style={{ color: '#444', marginLeft: 8, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{s.data ? (typeof s.data === 'object' ? JSON.stringify(s.data, null, 2) : s.data) : '미실행'}</div>
            {s.error && <div style={{ color: '#ff4d4f', marginLeft: 8 }} aria-label="에러">에러: {s.error}</div>}
          </li>
        ))}
      </ol>
    </div>
  );
}

function statusColor(status) {
  switch (status) {
    case 'success': return '#52c41a';
    case 'error': return '#ff4d4f';
    case 'pending': return '#faad14';
    case 'notrun': return '#bfbfbf';
    default: return '#888';
  }
}

// 에러가 발생한 마지막 단계 추정
function isErrorStep(key, result) {
  if (!result.error) return false;
  const order = ['text','intent','answer','assessment','ticket','escalation'];
  for (let i = order.length - 1; i >= 0; i--) {
    if (result[order[i]]) return order[i] === key;
  }
  return key === 'text';
}
// 이전 단계에 에러가 있었는지 확인
function hasPrevError(key, result) {
  if (!result.error) return false;
  const order = ['text','intent','answer','assessment','ticket','escalation'];
  let found = false;
  for (let i = 0; i < order.length; i++) {
    if (order[i] === key) return found;
    if (isErrorStep(order[i], result)) found = true;
  }
  return false;
} 