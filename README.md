# QARouting.ai (AutoRouting.ai)

> **Production-Ready Multi-Agent Legal QA & Compliance Routing Platform**

---

## 시스템 아키텍처 및 워크플로우

- 멀티에이전트 기반 문서/약관 QA, 컴플라이언스, 자동 티켓/에스컬레이션, 실시간 시각화
- 실제 법무팀 조직도/업무 분기/티켓/알림까지 자동화

```
User Prompt / Loop(수정된 약관 체크)
    │
    ▼
1. QuestionIntentionIngesterAgent
 ├─▶ 2. SimpleQuestionAnsweringAgent ──▶ Receives Answer
 ├─▶ 3. PotentialComplianceVerificationAgent
 │      └─▶ 4. TicketGeneratorAgent
 │             └─▶ 5. LegalTeamEscalatorAgent
 │                    └─▶ User (알림/에스컬레이션)
 └─▶ Outlier/Immediate Escalation → 4/5번 경로로 분기
```

---

## 주요 폴더/파일 구조

```
QARouting.ai/
├── agents/                  # 모든 에이전트(각 업무별)
│   ├── base_agent.py
│   ├── document_qa.py
│   ├── legal_team_escalator.py
│   ├── potential_compliance_verification.py
│   ├── question_intention_ingester.py
│   ├── simple_question_answering.py
│   ├── terms_check_bot.py
│   └── ticket_generator.py
├── data/                    # 실제 업무/테스트용 데이터
│   ├── complex_legal_questions.json
│   ├── legal_team_departments.json
│   ├── modified_terms.md
│   ├── sample_openai.md
│   └── simple_legal_questions.json
├── demo/
│   └── api_server.py        # FastAPI 백엔드
├── eval/                    # 벤치마크/테스트 자동화
├── frontend/                # React 프론트엔드
│   ├── src/components/visualization/LegalWorkflowDiagram.jsx
│   ├── src/components/visualization/TopologyDiagram.jsx
│   ├── ...
├── scripts/
│   └── langgraph_workflow.py # 전체 워크플로우 엔진
├── uploads/                 # 업로드 파일
├── utils/                   # 공통 유틸
├── requirements.txt         # Python 의존성
├── package.json             # 프론트엔드 의존성
├── .gitignore
└── README.md
```

---

## 주요 기능/특징

- **실제 법률/컴플라이언스 업무 즉시 적용**: 문서/약관 QA, 컴플라이언스, 티켓, 에스컬레이션까지 자동화
- **분기별 워크플로우**: 단순 질문/복잡 질문/약관/즉시 에스컬레이션 등 실제 업무 분기 반영
- **실제 조직도/담당자/티켓/알림**: data/legal_team_departments.json 기반
- **실시간 시각화**: React Flow 기반 워크플로우/토폴로지/결과 시각화
- **엣지케이스/벤치마크 자동화**: eval/benchmark_runner.py 등
- **프론트-백엔드 완전 분리, 확장성/운영성 극대화**
- **보안/비밀키 관리**: .env, .gitignore, secret scanning 정책 적용

---

## 실행 방법 (실무 기준)

### 1. AutoRouting.ai.zip 파일 로컬 개발 환경 (추천)
### 설치 준비
```bash
AutoRouting.ai.zip
zip 파일 압축 풀기(npm 환경 셋업이 잘안되었을시를 위해 준비)
```
### 백엔드 실행
```bash
cd QARouting.ai
mkdir results
uvicorn demo.api_server:app_api --host 0.0.0.0 --port 8000
http://127.0.0.1:8000
```
### 프론트엔드 실행
```bash
cd QARouting.ai/frontend 
npm start
http://127.0.0.1:3000
```

### 2. 로컬 개발 환경
### 설치 준비
```bash
# Python, Node.js 설치
pip install -r requirements.txt
cd frontend &&
npm install --force
npm run build
```
### 백엔드 실행
```bash
uvicorn demo.api_server:app_api --host 0.0.0.0 --port 8000
http://127.0.0.1:8000
```
### 프론트엔드 실행
```bash
cd frontend && npm start
http://127.0.0.1:3000
```
---
####크전체 워크플로우 토폴로지
<img width="1908" height="992" alt="image" src="https://github.com/user-attachments/assets/fcc49b57-dea4-413e-b83b-3bb98e1f2c73" />
문서 업로드 또는 텍스트 입력시 결과 도출
#### 결과 워크플로우 토폴로지
<img width="1680" height="406" alt="image" src="https://github.com/user-attachments/assets/e9e63ac5-d210-4acd-a920-68812523d89d" />
Mange Benchmark Cases 클릭시 평가 결과 도출

## API 명세 (FastAPI)

### /run_workflow (POST)
- **Request**: `multipart/form-data`
  - `file`: PDF/Markdown file
  - `text`: string
- **Response**:
```json
{
  "result": {
    "intent": "simple|complex|terms_review",
    "answer": "...",
    "assessment": "...",
    "ticket": "...",
    "escalation": "...",
    "error": null
  }
}
```

---

## 프론트엔드 주요 구조 (React)

- **LegalWorkflowDiagram.jsx**: 실시간 워크플로우 시각화 (React Flow)
- **TopologyDiagram.jsx**: 에이전트 토폴로지 시각화
- **FileList.jsx**: 파일/벤치마크 업로드/선택
- **WorkflowRunner.jsx**: 질문 입력, 워크플로우 실행
- **ResultDetail.jsx**: 워크플로우 결과 상세
- **NotionReport.jsx**: 결과 리포트/저장

---

## 벤치마크/테스트 자동화

- `eval/benchmark_runner.py`로 전체 워크플로우/에이전트 성능 자동 평가
- 단순/복잡/약관/다국어/스캔본 등 엣지케이스 포함
- 신규 에이전트/워크플로우 추가 시, `agents/` 및 `langgraph_workflow.py`에 모듈화

---

## 보안/운영

- **.env, .gitignore, secret scanning**: 비밀키/민감정보 절대 커밋 금지, 실무 보안 정책 적용
- **실제 조직도/담당자/티켓/알림**: data/legal_team_departments.json 기반, 이메일/Slack 등 연동 확장 가능
- **운영환경 확장**: DB/캐시/메시지큐/실시간 협업 등 인프라 확장 용이

---

## 차별성/혁신 포인트

- 실전 법률/컴플라이언스 업무 즉시 적용
- 엣지케이스 자동화/시각화/벤치마크
- 프론트-백엔드 완전 분리, 확장성 극대화
- 실시간 시각화/조직도/티켓/알림 자동화

---

## 한계 및 개선점

- LLM API 비용/속도/스케일 한계 (OpenAI API)
- 스캔본 PDF 등 OCR 미지원 (추후 Tesseract 등 연동 가능)
- 조직도/에스컬레이션 로직은 샘플 데이터 기반 (실제 조직 연동 필요)
- 보안/인증/권한 관리 미구현 (운영환경 적용 필요)
- 멀티유저/실시간 협업은 미지원 (확장 가능 구조)

---

## 라이선스

MIT License
