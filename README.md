# 2A 프로토콜 구구단 프로젝트

두 개의 독립적인 AI 에이전트가 API를 통해 통신하며 구구단 문제를 해결하는 시스템입니다. 슈퍼바이저 에이전트가 전체 과정을 조율합니다.

## 프로젝트 구조
- `agent1/`: 문제 생성기 에이전트 (포트 5000)
- `agent2/`: 답변기 에이전트 (포트 6000)
- `supervisor/`: 슈퍼바이저 에이전트
- `frontend/`: Vue3 기반 웹 인터페이스 (포트 8000)
- `shared/`: 공유 모듈 (메시지 스키마 등)
- `tests/`: 테스트 코드

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
# 에이전트1 실행
python agent1/main.py

# 에이전트2 실행
python agent2/main.py

# 슈퍼바이저 실행
python supervisor/main.py

# 프론트엔드 실행
cd frontend
npm run dev
```

## 기능
- 사용자가 "N단 구구단 시작해줘. 정답이 M에 도달하면 멈춰줘." 형식으로 요청
- 에이전트1이 구구단 문제 생성
- 에이전트2가 문제 해결
- 실시간 모니터링 및 상호작용을 위한 채팅 인터페이스

## 라이센스
MIT 