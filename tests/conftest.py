"""
테스트 구성 모듈

테스트에 필요한 공통 설정과 픽스처를 정의합니다.
"""
import sys
import os
import pytest
from pathlib import Path

# 프로젝트 루트 디렉터리 경로를 모듈 검색 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))


# 환경 변수 설정
os.environ["TESTING"] = "1"


# asyncio 마커 등록
def pytest_configure(config):
    """
    pytest 구성 설정
    
    Args:
        config: pytest 구성 객체
    """
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio coroutine"
    )

    # pytest 설정 작업 수행
    pass 