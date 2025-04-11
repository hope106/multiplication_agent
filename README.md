# 2A 프로토콜 구구단 프로젝트

두 개의 독립적인 AI 에이전트가 API를 통해 통신하며 구구단 문제를 해결하는 시스템입니다. 슈퍼바이저 에이전트가 전체 과정을 조율합니다.

## 프로젝트 구조
- `agent1/`: 문제 생성기 에이전트 (포트 5000)
- `agent2/`: 답변기 에이전트 (포트 6001)
- `supervisor/`: 슈퍼바이저 에이전트
- `frontend/`: Vue3 기반 웹 인터페이스 (포트 8000)
- `shared/`: 공유 모듈 (메시지 스키마 등)
- `tests/`: 테스트 코드
- `logs/`: 에이전트 로그 파일 저장 디렉토리

## 시작하기

### 요구사항
- Python 3.8+
- Node.js 14+
- NPM 또는 Yarn

### 설치
```bash
# 백엔드 의존성 설치
pip install -r requirements.txt

# 프론트엔드 의존성 설치
cd frontend
npm install
```

### 실행
```bash
# 전체 시스템 실행 (권장)
python run.py

# 개별 컴포넌트 실행
python agent1/main.py  # 에이전트1 실행
python agent2/main.py  # 에이전트2 실행 
python supervisor/main.py  # 슈퍼바이저 실행

# 프론트엔드 실행
cd frontend
npm run dev
```

## 기능
- 사용자가 "N단 구구단 시작해줘. 정답이 M에 도달하면 멈춰줘." 형식으로 요청
- 에이전트1이 구구단 문제 생성
- 에이전트2가 문제 해결 및 설명 제공
- 실시간 모니터링 및 상호작용을 위한 채팅 인터페이스

## 에이전트 로그 확인
각 에이전트의 로그는 다음과 같은 방법으로 확인할 수 있습니다:

1. **웹 인터페이스**: 상단의 에이전트 상태 표시줄에서 "로그 보기" 버튼을 클릭하면 팝업 창을 통해 각 에이전트의 로그를 확인할 수 있습니다.

2. **로그 파일 직접 확인**: 모든 로그는 `logs/` 디렉토리에 저장됩니다.
   - `logs/supervisor.log`: 슈퍼바이저 로그
   - `logs/agent1.log`: 문제 생성기 로그
   - `logs/agent2.log`: 답변기 로그
   - `logs/main.log`: 전체 시스템 실행 로그

## 라이센스
MIT 