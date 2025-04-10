"""
에이전트2(답변기) 단위 테스트 모듈

구구단 문제에 대한 답변 API의 동작을 검증합니다.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 상위 디렉터리 경로를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent2.app.api import app


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
    assert response.json() == {"status": "ok", "agent": "answer_provider"}


def test_calculate_answer_success(client):
    """
    구구단 문제 계산 성공 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 테스트용 문제
    data = {"problem": "7×8="}
    
    # API 호출
    response = client.post("/answer", json=data)
    
    # 응답 검증
    assert response.status_code == 200
    
    result = response.json()
    assert result["answer"] == 56
    assert result["calculation"] == "7×8=56"


def test_calculate_answer_with_different_numbers(client):
    """
    다양한 숫자 조합에 대한 계산 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    test_cases = [
        {"problem": "1×1=", "expected_answer": 1, "expected_calculation": "1×1=1"},
        {"problem": "12×5=", "expected_answer": 60, "expected_calculation": "12×5=60"},
        {"problem": "9×9=", "expected_answer": 81, "expected_calculation": "9×9=81"},
        {"problem": "0×100=", "expected_answer": 0, "expected_calculation": "0×100=0"},
    ]
    
    for case in test_cases:
        response = client.post("/answer", json={"problem": case["problem"]})
        assert response.status_code == 200
        
        result = response.json()
        assert result["answer"] == case["expected_answer"]
        assert result["calculation"] == case["expected_calculation"]


def test_calculate_answer_invalid_format(client):
    """
    잘못된 형식의 문제 입력에 대한 오류 처리 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    invalid_cases = [
        {"problem": "7+8="},    # 곱셈이 아님
        {"problem": "7xx8="},   # 잘못된 연산자
        {"problem": "7×"},      # 두 번째 숫자 없음
        {"problem": "×8="},     # 첫 번째 숫자 없음
        {"problem": "hello"},   # 완전히 잘못된 형식
    ]
    
    for case in invalid_cases:
        response = client.post("/answer", json=case)
        assert response.status_code == 400  # Bad Request 응답 코드 확인 