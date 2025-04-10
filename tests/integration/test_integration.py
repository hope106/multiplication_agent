"""
구구단 프로젝트 통합 테스트 모듈

에이전트 간 통신 및 전체 흐름을 검증합니다.
"""
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

# 상위 디렉터리 경로를 모듈 검색 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from supervisor.app.api import process_gugudan, parse_request
from fastapi.testclient import TestClient
from agent1.app.api import app as agent1_app
from agent2.app.api import app as agent2_app
from supervisor.app.api import app as supervisor_app


@pytest.fixture
def agent1_client():
    """
    에이전트1(문제 생성기) 테스트 클라이언트 픽스처

    Returns:
        TestClient: FastAPI 테스트 클라이언트
    """
    return TestClient(agent1_app)


@pytest.fixture
def agent2_client():
    """
    에이전트2(답변기) 테스트 클라이언트 픽스처

    Returns:
        TestClient: FastAPI 테스트 클라이언트
    """
    return TestClient(agent2_app)


@pytest.fixture
def supervisor_client():
    """
    슈퍼바이저 테스트 클라이언트 픽스처

    Returns:
        TestClient: FastAPI 테스트 클라이언트
    """
    return TestClient(supervisor_app)


def test_request_parsing():
    """
    요청 파싱 테스트
    """
    # 종료 조건이 있는 경우
    message1 = "3단 구구단 시작해줘. 정답이 20에 도달하면 멈춰줘"
    table1, stop_value1 = parse_request(message1)
    assert table1 == 3
    assert stop_value1 == 20
    
    # 종료 조건이 없는 경우
    message2 = "5단 구구단 시작해줘"
    table2, stop_value2 = parse_request(message2)
    assert table2 == 5
    assert stop_value2 is None


def test_agent1_to_agent2_communication(agent1_client, agent2_client):
    """
    에이전트1에서 에이전트2로의 통신 테스트

    이 테스트는 에이전트1이 문제를 생성하고 에이전트2에게 직접 전달하는 대신,
    각 에이전트의 API 엔드포인트를 독립적으로 호출하여 통합 동작을 검증합니다.

    Args:
        agent1_client (TestClient): 에이전트1 테스트 클라이언트
        agent2_client (TestClient): 에이전트2 테스트 클라이언트
    """
    # 1. 에이전트1에서 문제 생성
    problem_response = agent1_client.post(
        "/problem/initialize", 
        json={"table": 4, "stop_value": 20}
    )
    assert problem_response.status_code == 200
    
    problem_data = problem_response.json()
    problem = problem_data["problem"]
    assert problem == "4×1="
    
    # 2. 에이전트2에게 문제 전달하여 계산
    answer_response = agent2_client.post(
        "/answer",
        json={"problem": problem}
    )
    assert answer_response.status_code == 200
    
    answer_data = answer_response.json()
    assert answer_data["answer"] == 4
    assert answer_data["calculation"] == "4×1=4"


@pytest.mark.asyncio
@patch("supervisor.app.api.broadcast_message", new_callable=AsyncMock)
@patch("supervisor.app.api.httpx.AsyncClient")
async def test_process_gugudan_flow(mock_async_client, mock_broadcast, agent1_client, agent2_client):
    """
    구구단 처리 흐름 통합 테스트

    모의 객체를 사용하여 에이전트 간 통신 및 메시지 브로드캐스트를 검증합니다.

    Args:
        mock_async_client (Mock): httpx.AsyncClient 모의 객체
        mock_broadcast (AsyncMock): broadcast_message 함수 모의 객체
        agent1_client (TestClient): 에이전트1 테스트 클라이언트
        agent2_client (TestClient): 에이전트2 테스트 클라이언트
    """
    # 모의 응답 데이터 설정
    initialize_response_mock = AsyncMock()
    initialize_response_mock.status_code = 200
    initialize_response_mock.json.return_value = {
        "problem": "2×1=",
        "multiplier": 2,
        "multiplicand": 1,
        "status": "continue"
    }
    
    solve_response_mock = AsyncMock()
    solve_response_mock.status_code = 200
    solve_response_mock.json.return_value = {
        "answer": 2,
        "calculation": "2×1=2"
    }
    
    next_response_mock = AsyncMock()
    next_response_mock.status_code = 200
    next_response_mock.json.return_value = {
        "problem": "2×2=",
        "multiplier": 2,
        "multiplicand": 2,
        "status": "continue"
    }
    
    # AsyncClient의 post 메서드 모의 구현
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.post.side_effect = [
        initialize_response_mock,  # 초기화 응답
        solve_response_mock,       # 답변 응답
        next_response_mock,        # 다음 문제 응답
    ]
    mock_async_client.return_value = mock_client_instance
    
    # process_gugudan 함수 호출
    await process_gugudan(2, 10)
    
    # 에이전트1 초기화 호출 검증
    mock_client_instance.__aenter__.return_value.post.assert_any_call(
        "http://localhost:5000/problem/initialize",
        json={"table": 2, "stop_value": 10}
    )
    
    # 브로드캐스트 메시지 검증
    assert mock_broadcast.call_count >= 2
    
    # 문제 브로드캐스트 검증
    mock_broadcast.assert_any_call({
        "type": "problem",
        "content": "2×1=",
        "sender": "agent1",
        "timestamp": mock_broadcast.call_args_list[0][0][0]["timestamp"]
    })
    
    # 답변 브로드캐스트 검증
    mock_broadcast.assert_any_call({
        "type": "answer",
        "content": "2×1=2",
        "sender": "agent2",
        "timestamp": mock_broadcast.call_args_list[1][0][0]["timestamp"]
    }) 