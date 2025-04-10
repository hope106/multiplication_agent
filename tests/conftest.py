"""
프로젝트 테스트 설정 파일

pytest 설정 및 공통 픽스처를 정의합니다.
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉터리를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))


def pytest_configure(config):
    """
    pytest 설정을 구성하는 함수

    Args:
        config: pytest 설정 객체
    """
    # pytest 설정 작업 수행
    pass 