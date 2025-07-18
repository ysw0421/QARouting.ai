import React from 'react';
import { Pie } from 'react-chartjs-2';

// Chart.js 등록
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
ChartJS.register(ArcElement, Tooltip, Legend);

export default function BenchmarkResult({ resultData, filename }) {
  // resultData: 배열 또는 오브젝트
  const results = Array.isArray(resultData)
    ? resultData
    : (resultData.workflow || resultData.results || []);

  // 성공/실패 통계
  const total = results.length;
  const successCount = results.filter(r => r.success || r.status === 'Success' || r.final_status === 'Success').length;
  const failCount = total - successCount;

  // 그래프 데이터
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
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafbfc' }}>
              <th style={thStyle}>#</th>
              <th style={thStyle}>질문</th>
              <th style={thStyle}>기대 라우팅</th>
              <th style={thStyle}>실제 라우팅</th>
              <th style={thStyle}>성공</th>
              <th style={thStyle}>에러</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} style={{ background: r.success ? '#f6ffed' : '#fff1f0' }}>
                <td style={tdStyle}>{i + 1}</td>
                <td style={tdStyle}>{r.question || r.input?.question || '-'}</td>
                <td style={tdStyle}>{r.expected_routing || r.expected || '-'}</td>
                <td style={tdStyle}>{r.actual_routing || r.actual || r.final_status || '-'}</td>
                <td style={{ ...tdStyle, color: r.success ? '#52c41a' : '#ff4d4f', fontWeight: 'bold' }}>{r.success ? 'O' : 'X'}</td>
                <td style={{ ...tdStyle, color: '#ff4d4f' }}>{r.error || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle = { border: '1px solid #eee', padding: 6, fontWeight: 'bold', color: '#333' };
const tdStyle = { border: '1px solid #eee', padding: 6 }; 