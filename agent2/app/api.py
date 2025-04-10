"""
에이전트2(답변기) API 엔드포인트 모듈

구구단 문제를 받아 계산하고 답변을 제공하는 API를 정의합니다.
"""
import re
from fastapi import FastAPI, HTTPException
from typing import Dict

from shared.schemas import AnswerRequest, AnswerResponse

app = FastAPI(title="구구단 답변기 에이전트")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    헬스 체크 엔드포인트

    Returns:
        Dict[str, str]: 에이전트 상태 정보
    """
    return {"status": "ok", "agent": "answer_provider"}


@app.post("/answer", response_model=AnswerResponse)
async def calculate_answer(request: AnswerRequest) -> AnswerResponse:
    """
    구구단 문제 계산 엔드포인트

    Args:
        request (AnswerRequest): 계산할 구구단 문제

    Returns:
        AnswerResponse: 계산된 답변

    Raises:
        HTTPException: 올바르지 않은 형식의 문제가 입력된 경우
    """
    problem = request.problem
    
    # 문제 형식 검증 및 숫자 추출
    pattern = r"(\d+)×(\d+)="
    match = re.match(pattern, problem)
    
    if not match:
        raise HTTPException(
            status_code=400,
            detail=f"올바르지 않은 문제 형식입니다: {problem}"
        )
    
    try:
        # 두 숫자 추출 및 계산
        n = int(match.group(1))
        x = int(match.group(2))
        result = n * x
        
        # 전체 계산식 생성
        calculation = f"{n}×{x}={result}"
        
        return AnswerResponse(answer=result, calculation=calculation)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"계산 중 오류 발생: {str(e)}"
        ) 