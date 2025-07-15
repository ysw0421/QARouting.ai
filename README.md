# AutoRouting.ai

## 🚀 프로젝트 개요

AutoRouting.ai는 입력된 Task Description(작업 설명)에 따라 최적화된 멀티 에이전트 워크플로우를 자동 생성하고, 에이전트 간의 상호작용 및 역할을 명확히 설계하는 시스템입니다. 기술 문서 처리, 법률 문서 분석, 연구 논문 요약, 고객 지원 문서 라우팅 등 다양한 업무 자동화를 지원합니다.

---

## 📌 주요 기능

- 입력된 작업 설명에 따라 멀티 에이전트 워크플로우 자동 설계 및 최적화
- 에이전트별 최적화된 프롬프트 자동 생성 및 역할 분담
- 에이전트 간 커뮤니케이션 토폴로지 및 워크플로우 시각화
- 자동화된 성능 평가 지표(metrics) 및 테스트 케이스 제공
- 컴플라이언스(준법) 이슈 자동 탐지 및 티켓 생성, 법률팀 자동 에스컬레이션
- 연구 논문 분석, 요약, 논문 간 연결점 및 연구 방향 제안
- FastAPI 기반 API 엔드포인트 제공 (선택 사항)
- 웹 기반 시스템 시각화 데모 (선택 사항)

---

## 🏗️ 아키텍처 및 에이전트 역할

- **Document Ingestor**: 문서(PDF/Markdown) 수집 및 전처리, 텍스트 추출
- **Section Classifier**: 문서 내 섹션(조항, 제목, 본문 등) 자동 분류
- **Question Answering Agent**: 사용자/시스템 질문에 대해 문서 기반 정확한 답변 제공
- **Compliance Issue Detector**: 컴플라이언스(준법) 관련 이슈 자동 식별 및 관련 법령 매핑
- **Legal Escalation Agent**: 복잡하거나 자동화 불가한 법률 쿼리/이슈를 법률팀에 자동 에스컬레이션
- **Ticket Generator**: 식별된 이슈/질문에 대해 컴플라이언스 검토 티켓(이슈/작업) 자동 생성 및 트래커 연동
- **Paper Analysis Agent**: 연구 논문에서 핵심 정보 추출, 요약, 논문 간 연결점 분석, 연구 방향 제안
- **Routing & Notification Agent**: 이슈/질문/티켓을 적절한 담당자에게 자동 라우팅 및 알림 전송
- **Audit & Logging Agent**: 모든 상호작용, 이슈, 티켓 생성 내역을 기록 및 감사 로그 관리

---

## 📂 폴더 구조

```
.
├── agents/              # 에이전트 구현 코드 및 프롬프트
├── data/                # 평가 데이터셋 및 테스트 케이스
├── eval/                # 성능 평가 및 벤치마크 코드
├── api/                 # FastAPI API 엔드포인트 (선택 사항)
├── frontend/            # 웹 시각화 데모 (선택 사항)
├── docs/                # 기술 문서 및 아키텍처 다이어그램
├── logs/                # 로그 파일
├── scripts/             # 실행 및 환경 설정 스크립트
├── README.md            # 본 문서
└── requirements.txt     # 패키지 의존성 목록
```

---

## ⚙️ 설치 방법

```bash
# 프로젝트 클론
git clone https://github.com/ysw0421/AutoRouting.ai.git
cd AutoRouting.ai

# 가상 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

---

## 🚦 사용 방법

### 시스템 실행

```bash
python scripts/run_workflow.py --task "Document QA & Routing" --input "./data/sample.pdf"
```

### (선택 사항) FastAPI 서버 실행

```bash
uvicorn api.main:app --reload
```

### (선택 사항) 웹 애플리케이션 실행

```bash
streamlit run frontend/app.py
```

---

## 🧪 테스트 및 평가

```bash
python eval/run_evaluation.py --scenario "Technical Documentation QA"
```

### 예시 테스트 시나리오
- 법률 문서(이용약관)에서 컴플라이언스 이슈 자동 탐지 및 티켓 생성
- 연구 논문 PDF에서 핵심 정보 추출, 요약, 논문 간 비교 및 연구 방향 제안
- 기술 문서에서 API QA, 업데이트 티켓 자동 생성, 복잡 쿼리 에스컬레이션

---

## 📝 기여 방법

1. 이슈 또는 Pull Request를 통해 버그, 개선사항, 신규 기능 제안
2. 코드 기여 전 반드시 이슈 등록 및 토론 권장
3. 커밋 메시지는 명확하게 작성

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. LICENSE 파일을 참고하세요. 