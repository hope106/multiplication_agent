"""
에이전트1(문제 생성기) 단위 테스트 모듈

구구단 문제 생성 API의 동작을 검증합니다.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 상위 디렉터리 경로를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent1.app.api import app


@pytest.fixture
def client():
    """
    FastAPI 테스트 클라이언트 픽스처

    Returns:
        TestClient: FastAPI 테스트 클라이언트
    """
    return TestClient(app)


def test_health_check(client):
    """
    헬스 체크 엔드포인트 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "agent": "problem_generator"}


def test_initialize_problem(client):
    """
    구구단 문제 초기화 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 테스트 요청 데이터
    data = {"table": 5, "stop_value": 20}
    
    # API 호출
    response = client.post("/problem/initialize", json=data)
    
    # 응답 검증
    assert response.status_code == 200
    
    result = response.json()
    assert result["problem"] == "5×1="
    assert result["multiplier"] == 5
    assert result["multiplicand"] == 1
    assert result["status"] == "continue"


def test_next_problem(client):
    """
    다음 구구단 문제 생성 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 먼저 초기화
    client.post("/problem/initialize", json={"table": 3})
    
    # 다음 문제 요청
    response = client.post("/problem/next")
    
    # 응답 검증
    assert response.status_code == 200
    
    result = response.json()
    assert result["problem"] == "3×2="
    assert result["multiplier"] == 3
    assert result["multiplicand"] == 2
    assert result["status"] == "continue"


def test_end_problem(client):
    """
    구구단 문제 생성 종료 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 먼저 초기화
    client.post("/problem/initialize", json={"table": 3})
    
    # 종료 요청
    response = client.post("/problem/end")
    
    # 응답 검증
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # 이후 다음 문제 요청 시 None이 반환되는지 확인
    next_response = client.post("/problem/next")
    assert next_response.status_code == 200
    assert next_response.json() is None


def test_complete_sequence(client):
    """
    9단까지 전체 시퀀스 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 초기화
    client.post("/problem/initialize", json={"table": 2})
    
    # 9번째 문제까지 요청
    for i in range(8):
        response = client.post("/problem/next")
        assert response.status_code == 200
        result = response.json()
        assert result["multiplier"] == 2
        assert result["multiplicand"] == i + 2
    
    # 9번째 이후 요청 시 상태가 completed로 변경되어야 함
    final_response = client.post("/problem/next")
    final_result = final_response.json()
    assert final_result["status"] == "completed" 