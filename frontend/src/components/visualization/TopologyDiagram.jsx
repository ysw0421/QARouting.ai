import React, { useMemo } from 'react';
// import Mermaid from 'mermaid-react'; // REMOVE

// 상태별 텍스트 및 색상
const statusText = {
  success: '성공',
  error: '실패',
  pending: '대기',
  notrun: '미실행',
};
const statusColor = {
  success: '#52c41a',
  error: '#ff4d4f',
  pending: '#faad14',
  notrun: '#bfbfbf',
};

function getNodeStatus(workflowResult) {
  const status = {
    ingest: 'notrun',
    intention: 'notrun',
    simple: 'notrun',
    compliance: 'notrun',
    ticket: 'notrun',
    escalation: 'notrun',
  };
  if (!workflowResult) return status;
  if (workflowResult.text) status.ingest = 'success';
  if (workflowResult.intent) status.intention = 'success';
  if (workflowResult.answer) status.simple = 'success';
  if (workflowResult.assessment) status.compliance = 'success';
  if (workflowResult.ticket) status.ticket = 'success';
  if (workflowResult.escalation) status.escalation = 'success';
  if (workflowResult.error) {
    const steps = ['ingest','intention','simple','compliance','ticket','escalation'];
    for (let i = steps.length - 1; i >= 0; i--) {
      if (status[steps[i]] === 'success') {
        status[steps[i]] = 'error';
        break;
      }
    }
  }
  let errorFound = false;
  for (const step of ['ingest','intention','simple','compliance','ticket','escalation']) {
    if (errorFound) status[step] = 'pending';
    if (status[step] === 'error') errorFound = true;
  }
  return status;
}

function getNodeStyle(status) {
  switch (status) {
    case 'success': return { background: '#e6ffed', border: '2px solid #52c41a' };
    case 'error': return { background: '#fff1f0', border: '2px solid #ff4d4f' };
    case 'pending': return { background: '#f0f5ff', border: '2px dashed #faad14' };
    case 'notrun': return { background: '#f5f5f5', border: '1px solid #bfbfbf' };
    default: return {};
  }
}

const nodeLabels = [
  { key: 'ingest', label: 'Ingest' },
  { key: 'intention', label: 'Intention' },
  { key: 'simple', label: 'Simple Q&A' },
  { key: 'compliance', label: 'Compliance' },
  { key: 'ticket', label: 'Ticket' },
  { key: 'escalation', label: 'Escalation' },
];

export default function TopologyDiagram({ workflowResult }) {
  const nodeStatus = useMemo(() => getNodeStatus(workflowResult), [workflowResult]);
  return (
    <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h4 style={{ margin: 0, marginBottom: 8, color: '#333' }}>Workflow Topology</h4>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        {nodeLabels.map((node, idx) => (
          <div key={node.key} style={{
            ...getNodeStyle(nodeStatus[node.key]),
            flex: 1,
            margin: '0 8px',
            padding: 16,
            borderRadius: 8,
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#333',
            position: 'relative',
          }}>
            {node.label}
            <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>{statusText[nodeStatus[node.key]]}</div>
            {idx < nodeLabels.length - 1 && (
              <div style={{
                position: 'absolute',
                right: -16,
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: 24,
                color: '#bbb',
              }}>→</div>
            )}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, fontSize: 13, color: '#888' }}>
        <b>상태 안내:</b>
        <span style={{ color: statusColor.success, marginLeft: 8 }}>[성공]</span>
        <span style={{ color: statusColor.error, marginLeft: 8 }}>[실패]</span>
        <span style={{ color: statusColor.pending, marginLeft: 8 }}>[대기]</span>
        <span style={{ color: statusColor.notrun, marginLeft: 8 }}>[미실행]</span>
      </div>
    </div>
  );
} 