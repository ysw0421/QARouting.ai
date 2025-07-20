import React from 'react';
import ReactFlow, { MiniMap, Controls, Background, ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';

const nodes = [
  { id: '1', type: 'input', data: { label: '입력 전처리\n(텍스트 변환, 언어 자동 감지)' }, position: { x: 0, y: 0 } },
  { id: '2', data: { label: '처리 유형 분석\n(단순/복잡/약관)' }, position: { x: 250, y: 0 } },
  { id: '3', data: { label: '단순 질문 처리' }, position: { x: 500, y: -120 } },
  { id: '4', data: { label: '복잡 질문 처리' }, position: { x: 500, y: 0 } },
  { id: '5', data: { label: '약관 컴플라이언스 분석' }, position: { x: 500, y: 120 } },
  { id: '6', data: { label: '준법 리스크 분석' }, position: { x: 750, y: 0 } },
  { id: '7', data: { label: '통합 티켓 생성 및 라우팅' }, position: { x: 1000, y: 0 } },
  { id: '8', data: { label: '법무팀 에스컬레이션 알림' }, position: { x: 1250, y: 0 } },
  { id: '9', type: 'output', data: { label: '최종 사용자 응답' }, position: { x: 1500, y: 0 } },
];

const edges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', label: '단순', animated: true },
  { id: 'e2-4', source: '2', target: '4', label: '복잡', animated: true },
  { id: 'e2-5', source: '2', target: '5', label: '약관', animated: true },
  { id: 'e3-9', source: '3', target: '9', animated: true },
  { id: 'e4-6', source: '4', target: '6', animated: true },
  { id: 'e5-6', source: '5', target: '6', animated: true },
  { id: 'e6-7', source: '6', target: '7', animated: true },
  { id: 'e7-8', source: '7', target: '8', animated: true },
  { id: 'e8-9', source: '8', target: '9', animated: true },
];

export default function LegalWorkflowDiagram({ workflowResult }) {
  return (
    <div style={{ height: 500, background: '#fff', borderRadius: 8, margin: 16, boxShadow: '0 2px 8px #eee' }}>
      <ReactFlowProvider>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
} 