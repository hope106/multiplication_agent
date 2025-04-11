"""
에이전트1(문제 생성기) API 엔드포인트 모듈

구구단 문제를 생성하고 답변기 에이전트와 통신하는 API를 정의합니다.
"""
import httpx
from fastapi import FastAPI, HTTPException
from typing import Dict, Optional
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas import (
    ProblemRequest,
    ProblemGenerated,
    AnswerRequest,
    AnswerResponse,
)

app = FastAPI(title="구구단 문제 생성기 에이전트")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에이전트 상태 저장
state: Dict[str, any] = {
    "current_table": None,
    "current_index": 1,
    "stop_value": None,
    "is_completed": False,
}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    헬스 체크 엔드포인트

    Returns:
        Dict[str, str]: 에이전트 상태 정보
    """
    return {"status": "ok", "agent": "problem_generator"}


@app.post("/problem/initialize", response_model=ProblemGenerated)
async def initialize_problem(request: ProblemRequest) -> ProblemGenerated:
    """
    구구단 문제 초기화 엔드포인트

    Args:
        request (ProblemRequest): 구구단 단수 및 종료 조건 정보

    Returns:
        ProblemGenerated: 생성된 첫 번째 구구단 문제
    """
    # 상태 초기화
    state["current_table"] = request.table
    state["current_index"] = 1
    state["stop_value"] = request.stop_value
    state["is_completed"] = False

    # 첫 번째 문제 생성
    problem = f"{request.table}×{state['current_index']}="
    
    return ProblemGenerated(
        problem=problem,
        multiplier=request.table,
        multiplicand=state["current_index"],
        status="continue"
    )


@app.post("/problem/next", response_model=Optional[ProblemGenerated])
async def next_problem() -> Optional[ProblemGenerated]:
    """
    다음 구구단 문제 생성 엔드포인트

    Returns:
        Optional[ProblemGenerated]: 다음 구구단 문제 또는 None (완료된 경우)
    """
    if state["is_completed"] or state["current_table"] is None:
        return None
    
    # 다음 인덱스로 증가
    state["current_index"] += 1
    
    # 9단까지만 진행 (기본 종료 조건)
    if state["current_index"] > 9:
        state["is_completed"] = True
        return ProblemGenerated(
            problem=f"{state['current_table']}×{state['current_index']-1}=",
            multiplier=state["current_table"],
            multiplicand=state["current_index"]-1,
            status="completed"
        )
    
    # 다음 문제 생성
    problem = f"{state['current_table']}×{state['current_index']}="
    
    return ProblemGenerated(
        problem=problem,
        multiplier=state["current_table"],
        multiplicand=state["current_index"],
        status="continue"
    )


@app.post("/problem/solve", response_model=AnswerResponse)
async def solve_problem(problem: AnswerRequest) -> AnswerResponse:
    """
    생성된 문제를 답변기 에이전트에 전송하여 해결 요청

    Args:
        problem (AnswerRequest): 해결할 구구단 문제

    Returns:
        AnswerResponse: 답변기로부터 받은 답변

    Raises:
        HTTPException: 답변기 에이전트 통신 오류 시
    """
    agent2_url = "http://localhost:6001/answer"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(agent2_url, json=problem.dict())
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"답변기 에이전트 응답 오류: {response.text}"
                )
            return AnswerResponse.parse_obj(response.json())
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"답변기 에이전트 연결 실패: {str(e)}"
        )


@app.post("/problem/end")
async def end_problem() -> Dict[str, str]:
    """
    구구단 문제 생성 종료 엔드포인트

    Returns:
        Dict[str, str]: 종료 상태 메시지
    """
    state["is_completed"] = True
    return {"status": "ok", "message": "구구단 문제 생성이 종료되었습니다."} 