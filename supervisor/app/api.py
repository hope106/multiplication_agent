"""
슈퍼바이저 에이전트 API 엔드포인트 모듈

사용자 요청을 처리하고 다른 에이전트들의 작업을 조율하는 API를 정의합니다.
"""
import re
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import json
from datetime import datetime

from shared.schemas import (
    SupervisorRequest,
    SupervisorResponse,
    ProblemRequest,
    ProblemGenerated,
    AnswerResponse,
    WebSocketMessage,
)

app = FastAPI(title="구구단 슈퍼바이저 에이전트")

# CORS 설정 - 개발 환경에서는 모든 출처 허용
origins = [
    "http://localhost:8080",  # 프론트엔드 개발 서버
    "http://127.0.0.1:8080",
    "http://localhost:5173",  # Vite 기본 포트
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 웹소켓 연결 클라이언트 관리
connected_clients: List[WebSocket] = []


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    헬스 체크 엔드포인트

    Returns:
        Dict[str, str]: 에이전트 상태 정보
    """
    return {"status": "ok", "agent": "supervisor"}


@app.post("/request", response_model=SupervisorResponse)
async def process_request(request: SupervisorRequest) -> SupervisorResponse:
    """
    사용자 요청 처리 엔드포인트

    사용자의 구구단 요청을 해석하고 에이전트들을 조율하여 문제 풀이를 진행합니다.

    Args:
        request (SupervisorRequest): 사용자 요청 메시지

    Returns:
        SupervisorResponse: 요청 처리 결과

    Raises:
        HTTPException: 요청 처리 중 오류 발생 시
    """
    # 요청 메시지 파싱
    message = request.message
    
    # 구구단 단수 및 종료 조건 파싱
    table, stop_value = parse_request(message)
    
    if not table:
        return SupervisorResponse(
            message="구구단 단수를 인식할 수 없습니다. 예: '5단 구구단 시작해줘'"
        )
    
    # 비동기로 구구단 처리 시작
    asyncio.create_task(process_gugudan(table, stop_value))
    
    if stop_value:
        response_message = f"{table}단 구구단을 시작합니다. 정답이 {stop_value}에 도달하면 멈추겠습니다."
    else:
        response_message = f"{table}단 구구단을 시작합니다. {table}×9까지 진행하겠습니다."
    
    return SupervisorResponse(message=response_message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    웹소켓 연결 엔드포인트

    클라이언트와의 실시간 양방향 통신을 위한 웹소켓 연결을 관리합니다.

    Args:
        websocket (WebSocket): 웹소켓 연결 객체
    """
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            try:
                # JSON 파싱
                message_data = json.loads(data)
                
                if "type" in message_data and message_data["type"] == "user_message":
                    # 사용자 메시지 처리
                    user_message = message_data.get("content", "")
                    
                    # 직접 처리 (외부 API 호출 대신)
                    request = SupervisorRequest(message=user_message)
                    response = await process_request(request)
                    
                    await broadcast_message({
                        "type": "system_message",
                        "content": response.message,
                        "sender": "supervisor",
                        "timestamp": datetime.now().isoformat()
                    })
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "system_message",
                    "content": "잘못된 형식의 메시지입니다.",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "system_message",
                    "content": f"요청 처리 중 오류가 발생했습니다: {str(e)}",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat()
                }))
    except WebSocketDisconnect:
        # 연결 종료 시 목록에서 제거
        if websocket in connected_clients:
            connected_clients.remove(websocket)


async def broadcast_message(message: Dict):
    """
    모든 웹소켓 클라이언트에게 메시지 브로드캐스트

    Args:
        message (Dict): 전송할 메시지
    """
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception:
            # 연결 오류 발생 시 목록에서 제거
            if client in connected_clients:
                connected_clients.remove(client)


def parse_request(message: str) -> tuple[Optional[int], Optional[int]]:
    """
    사용자 요청 메시지 파싱

    Args:
        message (str): 사용자 요청 메시지

    Returns:
        tuple[Optional[int], Optional[int]]: (구구단 단수, 종료 조건 값)
    """
    # 구구단 단수 추출
    table_pattern = r"(\d+)\s*단"
    table_match = re.search(table_pattern, message)
    
    table = int(table_match.group(1)) if table_match else None
    
    # 종료 조건 추출
    stop_pattern = r"정답이\s*(\d+)에\s*도달하면"
    stop_match = re.search(stop_pattern, message)
    
    stop_value = int(stop_match.group(1)) if stop_match else None
    
    return table, stop_value


async def process_gugudan(table: int, stop_value: Optional[int] = None):
    """
    구구단 문제 풀이 과정 처리

    에이전트1과 에이전트2를 조율하여 구구단 문제를 생성하고 풀이합니다.

    Args:
        table (int): 구구단 단수
        stop_value (Optional[int], optional): 종료 조건 값
    """
    try:
        # 에이전트1 (문제 생성기) 초기화
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5000/problem/initialize",
                json={"table": table, "stop_value": stop_value}
            )
            
            if response.status_code != 200:
                await broadcast_message({
                    "type": "system_message",
                    "content": "문제 생성기 초기화 실패",
                    "sender": "supervisor",
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            problem_data = response.json()
            problem = problem_data.get("problem", "")
            
            # 문제 브로드캐스트
            await broadcast_message({
                "type": "problem",
                "content": problem,
                "sender": "agent1",
                "timestamp": datetime.now().isoformat()
            })
            
            # 지속적으로 문제 생성 및 풀이
            while True:
                # 답변 요청
                answer_response = await client.post(
                    "http://localhost:5000/problem/solve",
                    json={"problem": problem}
                )
                
                if answer_response.status_code != 200:
                    await broadcast_message({
                        "type": "system_message",
                        "content": "답변 처리 실패",
                        "sender": "supervisor",
                        "timestamp": datetime.now().isoformat()
                    })
                    break
                
                answer_data = answer_response.json()
                calculation = answer_data.get("calculation", "")
                answer = answer_data.get("answer", 0)
                
                # 답변 브로드캐스트
                await broadcast_message({
                    "type": "answer",
                    "content": calculation,
                    "sender": "agent2",
                    "timestamp": datetime.now().isoformat()
                })
                
                # 종료 조건 확인
                if stop_value and answer >= stop_value:
                    await broadcast_message({
                        "type": "system_message",
                        "content": f"정답이 {stop_value}에 도달했습니다. 구구단이 끝났습니다.",
                        "sender": "supervisor",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 에이전트1에 종료 요청
                    await client.post("http://localhost:5000/problem/end")
                    break
                
                # 다음 문제 요청
                next_response = await client.post("http://localhost:5000/problem/next")
                
                if next_response.status_code != 200:
                    await broadcast_message({
                        "type": "system_message",
                        "content": "다음 문제 생성 실패",
                        "sender": "supervisor",
                        "timestamp": datetime.now().isoformat()
                    })
                    break
                
                next_data = next_response.json()
                
                # 완료 확인
                if next_data is None or next_data.get("status") == "completed":
                    await broadcast_message({
                        "type": "system_message",
                        "content": f"구구단이 끝났습니다. {table}단 학습 완료!",
                        "sender": "supervisor",
                        "timestamp": datetime.now().isoformat()
                    })
                    break
                
                problem = next_data.get("problem", "")
                
                # 다음 문제 브로드캐스트
                await broadcast_message({
                    "type": "problem",
                    "content": problem,
                    "sender": "agent1",
                    "timestamp": datetime.now().isoformat()
                })
                
                # 너무 빠른 요청 방지
                await asyncio.sleep(1)
    
    except Exception as e:
        await broadcast_message({
            "type": "system_message",
            "content": f"구구단 처리 중 오류 발생: {str(e)}",
            "sender": "supervisor",
            "timestamp": datetime.now().isoformat()
        }) 