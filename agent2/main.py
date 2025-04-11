"""
에이전트2(답변기) 메인 실행 파일

구구단 문제의 답변을 제공하는 에이전트 서버를 실행합니다.
"""
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 현재 파일 위치를 기준으로 프로젝트 루트 경로를 추가
sys.path.append(str(Path(__file__).parent.parent))

# 공통 로깅 모듈 임포트
from shared.logger import get_agent_logger

# 로깅 설정
logger = get_agent_logger("agent2")

# .env 파일 로드 (있는 경우)
load_dotenv()

# 기본 포트 설정
DEFAULT_PORT = 6001  # 6000에서 6001로 변경 (6001은 브라우저에서 안전하지 않은 포트로 간주됨)
PORT = int(os.getenv("AGENT2_PORT", DEFAULT_PORT))
HOST = os.getenv("AGENT2_HOST", "0.0.0.0")


def main():
    """
    답변기 에이전트 서버 실행 함수
    """
    logger.info(f"🚀 답변기 에이전트 서버를 {HOST}:{PORT}에서 시작합니다...")
    uvicorn.run(
        "app.api:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main() 