import React, { useMemo } from 'react';
import Mermaid from 'mermaid-react';

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
    case 'success': return 'fill:#e6ffed,stroke:#52c41a,stroke-width:2px';
    case 'error': return 'fill:#fff1f0,stroke:#ff4d4f,stroke-width:2px';
    case 'pending': return 'fill:#f0f5ff,stroke:#faad14,stroke-width:2px,stroke-dasharray:4 2';
    case 'notrun': return 'fill:#f5f5f5,stroke:#bfbfbf,stroke-width:1px';
    default: return '';
  }
}

// 노드별 상태 텍스트 및 툴팁 생성
function getNodeLabel(node, status, workflowResult) {
  let label = '';
  switch (node) {
    case 'ingest': label = 'Ingest'; break;
    case 'intention': label = 'Intention'; break;
    case 'simple': label = 'Simple Q&A'; break;
    case 'compliance': label = 'Compliance'; break;
    case 'ticket': label = 'Ticket'; break;
    case 'escalation': label = 'Escalation'; break;
    default: label = node;
  }
  const st = statusText[status] || '';
  // 에러 메시지 툴팁
  let tooltip = st;
  if (status === 'error' && workflowResult && workflowResult.error) {
    tooltip += `\n에러: ${workflowResult.error}`;
  }
  return `${label} [${st}]:::${node}Tooltip`;
}

export default function TopologyDiagram({ workflowResult }) {
  const nodeStatus = useMemo(() => getNodeStatus(workflowResult), [workflowResult]);
  // 노드별 라벨 및 툴팁
  const nodes = [
    'ingest', 'intention', 'simple', 'compliance', 'ticket', 'escalation'
  ];
  const nodeLabels = nodes.reduce((acc, node) => {
    acc[node] = getNodeLabel(node, nodeStatus[node], workflowResult);
    return acc;
  }, {});
  // Mermaid 정의
  const mermaidDef = useMemo(() => {
    return `graph TD
      INGEST["${nodeLabels.ingest}"]:::ingest --> INTENTION["${nodeLabels.intention}"]:::intention
      INTENTION -- Simple --> SIMPLE["${nodeLabels.simple}"]:::simple
      INTENTION -- Compliance --> COMPLIANCE["${nodeLabels.compliance}"]:::compliance
      INTENTION -- Terms Review --> TICKET["${nodeLabels.ticket}"]:::ticket
      COMPLIANCE --> TICKET
      TICKET --> ESCALATION["${nodeLabels.escalation}"]:::escalation
      SIMPLE --> END((END))
      ESCALATION --> END
      classDef ingest ${getNodeStyle(nodeStatus.ingest)};
      classDef intention ${getNodeStyle(nodeStatus.intention)};
      classDef simple ${getNodeStyle(nodeStatus.simple)};
      classDef compliance ${getNodeStyle(nodeStatus.compliance)};
      classDef ticket ${getNodeStyle(nodeStatus.ticket)};
      classDef escalation ${getNodeStyle(nodeStatus.escalation)};
      class INGEST ingest;
      class INTENTION intention;
      class SIMPLE simple;
      class COMPLIANCE compliance;
      class TICKET ticket;
      class ESCALATION escalation;
    `;
  }, [nodeLabels, nodeStatus]);

  return (
    <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h4 style={{ margin: 0, marginBottom: 8, color: '#333' }}>Workflow Topology</h4>
      <Mermaid chart={mermaidDef} />
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