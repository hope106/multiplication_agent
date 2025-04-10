"""
슈퍼바이저 에이전트 단위 테스트 모듈

사용자 요청 처리 및 에이전트 조율 기능을 검증합니다.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

# 상위 디렉터리 경로를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from supervisor.app.api import app, parse_request


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
    assert response.json() == {"status": "ok", "agent": "supervisor"}


def test_parse_request_with_stop_value():
    """
    종료 조건이 있는 요청 메시지 파싱 테스트
    """
    message = "5단 구구단 시작해줘. 정답이 40에 도달하면 멈춰줘"
    table, stop_value = parse_request(message)
    
    assert table == 5
    assert stop_value == 40


def test_parse_request_without_stop_value():
    """
    종료 조건이 없는 요청 메시지 파싱 테스트
    """
    message = "7단 구구단 시작해줘"
    table, stop_value = parse_request(message)
    
    assert table == 7
    assert stop_value is None


def test_parse_request_invalid_format():
    """
    잘못된 형식의 요청 메시지 파싱 테스트
    """
    message = "구구단 좀 알려줘"
    table, stop_value = parse_request(message)
    
    assert table is None
    assert stop_value is None


@patch("supervisor.app.api.process_gugudan", new_callable=AsyncMock)
def test_process_request_with_stop_value(mock_process_gugudan, client):
    """
    종료 조건이 있는 요청 처리 테스트

    Args:
        mock_process_gugudan (AsyncMock): process_gugudan 함수 모의 객체
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 테스트 요청 데이터
    data = {"message": "6단 구구단 시작해줘. 정답이 30에 도달하면 멈춰줘"}
    
    # API 호출
    response = client.post("/request", json=data)
    
    # 응답 검증
    assert response.status_code == 200
    assert "6단 구구단을 시작합니다" in response.json()["message"]
    assert "30에 도달하면 멈추겠습니다" in response.json()["message"]
    
    # process_gugudan 함수 호출 검증
    mock_process_gugudan.assert_called_once_with(6, 30)


@patch("supervisor.app.api.process_gugudan", new_callable=AsyncMock)
def test_process_request_without_stop_value(mock_process_gugudan, client):
    """
    종료 조건이 없는 요청 처리 테스트

    Args:
        mock_process_gugudan (AsyncMock): process_gugudan 함수 모의 객체
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 테스트 요청 데이터
    data = {"message": "8단 구구단 시작해줘"}
    
    # API 호출
    response = client.post("/request", json=data)
    
    # 응답 검증
    assert response.status_code == 200
    assert "8단 구구단을 시작합니다" in response.json()["message"]
    assert "8×9까지 진행하겠습니다" in response.json()["message"]
    
    # process_gugudan 함수 호출 검증
    mock_process_gugudan.assert_called_once_with(8, None)


def test_process_request_invalid_format(client):
    """
    잘못된 형식의 요청 처리 테스트

    Args:
        client (TestClient): FastAPI 테스트 클라이언트
    """
    # 테스트 요청 데이터
    data = {"message": "구구단 좀 알려줘"}
    
    # API 호출
    response = client.post("/request", json=data)
    
    # 응답 검증
    assert response.status_code == 200
    assert "구구단 단수를 인식할 수 없습니다" in response.json()["message"] 