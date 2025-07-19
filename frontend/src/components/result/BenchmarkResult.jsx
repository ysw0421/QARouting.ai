import React, { useState } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
ChartJS.register(ArcElement, Tooltip, Legend);

const EDGE_TYPES = ['다국어', '스캔본', '비정형', '실전문서'];

function isEdgeCase(r) {
  if (!r || !r.document_content) return false;
  const doc = r.document_content;
  if (/英語|日本語|English|Japanese|混合|multi[- ]?language|多国語|다국어|日本語/.test(doc)) return '다국어';
  if (/스캔본|scan|이미지|텍스트 없음|text not found|OCR|pdfplumber.*None|extract_text.*None/i.test(doc)) return '스캔본';
  if (/표|table|코드|code|이미지|image|<table|<img|```/.test(doc)) return '비정형';
  if (/약관|매뉴얼|API|manual|terms|policy|contract|서비스|OpenAI|제품/.test(doc)) return '실전문서';
  return false;
}

export default function BenchmarkResult({ resultData, filename }) {
  const [showOnlyFail, setShowOnlyFail] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState(null);
  const [edgeFilter, setEdgeFilter] = useState('전체');
  const results = Array.isArray(resultData)
    ? resultData
    : (resultData.workflow || resultData.results || []);
  const withEdge = results.map(r => ({ ...r, edge: isEdgeCase(r) }));
  const filtered = withEdge.filter(r =>
    (!showOnlyFail || !r.success) &&
    (edgeFilter === '전체' || r.edge === edgeFilter)
  );
  const total = withEdge.length;
  const successCount = withEdge.filter(r => r.success || r.status === 'Success' || r.final_status === 'Success').length;
  const failCount = total - successCount;
  const pieData = {
    labels: ['성공', '실패'],
    datasets: [
      {
        data: [successCount, failCount],
        backgroundColor: ['#52c41a', '#ff4d4f'],
        borderWidth: 1,
      },
    ],
  };
  // 엣지케이스별 통계
  const edgeStats = EDGE_TYPES.map(type => {
    const cases = withEdge.filter(r => r.edge === type);
    const succ = cases.filter(r => r.success).length;
    return { type, total: cases.length, success: succ, fail: cases.length - succ };
  });
  function downloadFailures() {
    const fails = withEdge.filter(r => !r.success);
    const blob = new Blob([JSON.stringify(fails, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'benchmark_failures.json';
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h4 style={{ margin: 0, marginBottom: 12, color: '#333' }}>벤치마크 결과: {filename}</h4>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ width: 120, height: 120 }}>
          <Pie data={pieData} options={{ plugins: { legend: { position: 'bottom' } } }} />
        </div>
        <div style={{ marginLeft: 24, fontWeight: 'bold', fontSize: 16 }}>
          전체: {total} <br />
          성공: <span style={{ color: '#52c41a' }}>{successCount}</span> <br />
          실패: <span style={{ color: '#ff4d4f' }}>{failCount}</span> <br />
          성공률: {(total ? (successCount / total * 100).toFixed(1) : 0)}%
        </div>
        <div style={{ marginLeft: 32 }}>
          <button onClick={() => setShowOnlyFail(f => !f)} style={btnStyle}>
            {showOnlyFail ? '전체 보기' : '실패만 보기'}
          </button>
          <button onClick={downloadFailures} style={btnStyle}>
            실패 다운로드
          </button>
        </div>
      </div>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontWeight: 'bold', marginRight: 8 }}>엣지케이스 필터:</span>
        <button style={edgeBtn(edgeFilter === '전체')} onClick={() => setEdgeFilter('전체')}>전체</button>
        {EDGE_TYPES.map(type => (
          <button key={type} style={edgeBtn(edgeFilter === type)} onClick={() => setEdgeFilter(type)}>{type}</button>
        ))}
      </div>
      <div style={{ marginBottom: 16 }}>
        <table style={{ borderCollapse: 'collapse', fontSize: 13, marginBottom: 0 }}>
          <thead>
            <tr style={{ background: '#fafbfc' }}>
              <th style={thStyle}>엣지케이스</th>
              <th style={thStyle}>전체</th>
              <th style={thStyle}>성공</th>
              <th style={thStyle}>실패</th>
              <th style={thStyle}>성공률</th>
            </tr>
          </thead>
          <tbody>
            {edgeStats.map(stat => (
              <tr key={stat.type}>
                <td style={tdStyle}>{stat.type}</td>
                <td style={tdStyle}>{stat.total}</td>
                <td style={{ ...tdStyle, color: '#52c41a' }}>{stat.success}</td>
                <td style={{ ...tdStyle, color: '#ff4d4f' }}>{stat.fail}</td>
                <td style={tdStyle}>{stat.total ? ((stat.success / stat.total) * 100).toFixed(1) + '%' : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafbfc' }}>
              <th style={thStyle}>#</th>
              <th style={thStyle}>질문</th>
              <th style={thStyle}>엣지케이스</th>
              <th style={thStyle}>기대 라우팅</th>
              <th style={thStyle}>실제 라우팅</th>
              <th style={thStyle}>성공</th>
              <th style={thStyle}>에러</th>
              <th style={thStyle}>상세</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <React.Fragment key={i}>
                <tr style={{ background: r.success ? '#f6ffed' : '#fff1f0' }}>
                  <td style={tdStyle}>{i + 1}</td>
                  <td style={tdStyle}>{r.question || r.input?.question || '-'}</td>
                  <td style={{ ...tdStyle, color: r.edge ? '#faad14' : '#bbb', fontWeight: r.edge ? 'bold' : undefined }}>{r.edge || '-'}</td>
                  <td style={tdStyle}>{r.expected_routing || r.expected || '-'}</td>
                  <td style={tdStyle}>{r.actual_routing || r.actual || r.final_status || '-'}</td>
                  <td style={{ ...tdStyle, color: r.success ? '#52c41a' : '#ff4d4f', fontWeight: 'bold' }}>{r.success ? 'O' : 'X'}</td>
                  <td style={{ ...tdStyle, color: '#ff4d4f' }}>{r.error || ''}</td>
                  <td style={tdStyle}>
                    <button style={btnStyle} onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}>
                      {expandedIdx === i ? '닫기' : '확대'}
                    </button>
                  </td>
                </tr>
                {expandedIdx === i && (
                  <tr>
                    <td colSpan={8} style={{ background: '#f9f9f9', padding: 16 }}>
                      <div style={{ fontWeight: 'bold', marginBottom: 4 }}>기대 답변</div>
                      <pre style={preStyle}>{r.expected_answer || '-'}</pre>
                      <div style={{ fontWeight: 'bold', marginBottom: 4, marginTop: 8 }}>실제 답변</div>
                      <pre style={preStyle}>{r.answer || '-'}</pre>
                      {r.assessment && <><div style={{ fontWeight: 'bold', marginBottom: 4, marginTop: 8 }}>Assessment</div><pre style={preStyle}>{JSON.stringify(r.assessment, null, 2)}</pre></>}
                      {r.ticket && <><div style={{ fontWeight: 'bold', marginBottom: 4, marginTop: 8 }}>Ticket</div><pre style={preStyle}>{JSON.stringify(r.ticket, null, 2)}</pre></>}
                      {r.escalation && <><div style={{ fontWeight: 'bold', marginBottom: 4, marginTop: 8 }}>Escalation</div><pre style={preStyle}>{JSON.stringify(r.escalation, null, 2)}</pre></>}
                      {r.error && <><div style={{ fontWeight: 'bold', marginBottom: 4, marginTop: 8, color: '#ff4d4f' }}>Error</div><pre style={preStyle}>{r.error}</pre></>}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle = { border: '1px solid #eee', padding: 6, fontWeight: 'bold', color: '#333' };
const tdStyle = { border: '1px solid #eee', padding: 6 };
const btnStyle = { padding: '2px 10px', border: '1px solid #bbb', borderRadius: 4, background: '#fafbfc', cursor: 'pointer', marginRight: 4 };
const preStyle = { background: '#f4f4f4', padding: 8, borderRadius: 4, fontSize: 13, whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0 };
const edgeBtn = (active) => ({ padding: '2px 10px', marginRight: 4, border: active ? '2px solid #1890ff' : '1px solid #bbb', borderRadius: 4, background: active ? '#e6f7ff' : '#fafbfc', fontWeight: active ? 'bold' : undefined, cursor: 'pointer' }); 