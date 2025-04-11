"""
에이전트2(답변기) 단위 테스트 모듈

구구단 문제에 대한 답변 API의 동작을 검증합니다.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import os
import asyncio
import unittest.mock as mock

# 상위 디렉터리 경로를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent2.app.api import app, get_explanation


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
    # 설명 필드가 존재하는지 확인
    assert "explanation" in result


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
        # 설명 필드가 존재하는지 확인
        assert "explanation" in result


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


@pytest.mark.asyncio
async def test_get_explanation():
    """
    Claude API를 통한 설명 생성 테스트
    
    ANTHROPIC_API_KEY 환경 변수가 설정되어 있지 않으면 스킵됩니다.
    """
    # API 키가 있는지 확인
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    # 테스트 데이터
    calculation = "5×6=30"
    answer = 30
    
    # API 호출
    explanation = await get_explanation(calculation, answer)
    
    # 응답 검증
    assert explanation is not None
    assert len(explanation) > 0
    assert isinstance(explanation, str)
    
    
@pytest.mark.asyncio
async def test_get_explanation_with_mock():
    """
    Mock을 사용하여 Claude API 호출 없이 설명 생성 기능 테스트
    """
    # 테스트 데이터
    calculation = "5×6=30"
    answer = 30
    mock_explanation = "5를 6번 더하면 30이 됩니다. 5+5+5+5+5+5=30 이에요."
    
    # httpx.AsyncClient.post 메서드를 모킹
    with mock.patch('httpx.AsyncClient.post') as mock_post:
        # 모의 응답 설정
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": mock_explanation}]
        }
        mock_post.return_value = mock_response
        
        # API 호출
        explanation = await get_explanation(calculation, answer)
        
        # 응답 검증
        assert explanation == mock_explanation
        # post 메서드가 호출되었는지 확인
        mock_post.assert_called_once() 