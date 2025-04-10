"""
슈퍼바이저 에이전트 메인 실행 파일

사용자 요청을 처리하고 에이전트들의 작업을 조율하는 슈퍼바이저 서버를 실행합니다.
"""
import uvicorn
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 현재 파일 위치를 기준으로 프로젝트 루트 경로를 추가
sys.path.append(str(Path(__file__).parent.parent))

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# .env 파일 로드 (있는 경우)
load_dotenv()

# 기본 포트 설정
DEFAULT_PORT = 8000
PORT = int(os.getenv("SUPERVISOR_PORT", DEFAULT_PORT))
HOST = os.getenv("SUPERVISOR_HOST", "0.0.0.0")


def main():
    """
    슈퍼바이저 에이전트 서버 실행 함수
    """
    print(f"🚀 슈퍼바이저 에이전트 서버를 {HOST}:{PORT}에서 시작합니다...")
    print(f"WebSocket 엔드포인트: ws://{HOST}:{PORT}/ws")
    uvicorn.run(
        "app.api:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="debug",
    )


if __name__ == "__main__":
    main() 