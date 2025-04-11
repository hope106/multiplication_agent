"""
에이전트2(답변기) API 엔드포인트 모듈

구구단 문제를 받아 계산하고 답변을 제공하는 API를 정의합니다.
"""
import re
import os
import httpx
from fastapi import FastAPI, HTTPException
from typing import Dict, List
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from shared.schemas import AnswerRequest, AnswerResponse

# 환경 변수 로드
load_dotenv()

app = FastAPI(title="구구단 답변기 에이전트")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    헬스 체크 엔드포인트

    Returns:
        Dict[str, str]: 에이전트 상태 정보
    """
    return {"status": "ok", "agent": "answer_provider"}


async def get_explanation(calculation: str, answer: int) -> str:
    """
    Claude API를 호출하여 구구단 계산에 대한 설명을 생성합니다.
    
    Args:
        calculation (str): 전체 계산식 (예: "4×5=20")
        answer (int): 계산 결과
        
    Returns:
        str: 생성된 설명
    """
    prompt = f"다음 구구단 계산 결과를 초등학생이 이해할 수 있도록 간단하게 설명해주세요:\n\n계산: {calculation}\n결과: {answer}\n\n설명은 간결하고 완전한 문장으로 100단어 이내로 작성해주세요. 마크다운 형식으로 작성해 주세요."
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # API 키 확인
    if not api_key:
        return "API 키가 설정되지 않아 설명을 생성할 수 없습니다."
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 300,  # 토큰 제한 늘림
                    "temperature": 0.5,
                    "system": "당신은 초등학생에게 구구단을 가르치는 친절한 선생님입니다. 설명은 마크다운 형식으로 작성하고, 완전한 문장으로 끝내세요.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
            else:
                return f"설명 생성 중 오류 발생: {response.status_code}"
    
    except Exception as e:
        return f"API 호출 중 오류 발생: {str(e)}"


def generate_visual_explanation(n: int, x: int, result: int) -> str:
    """
    구구단 계산을 시각적으로 표현합니다.
    
    Args:
        n (int): 곱해지는 수
        x (int): 곱하는 수
        result (int): 계산 결과
    
    Returns:
        str: 구구단을 시각적으로 표현한 문자열
    """
    # n을 x번 더하는 방식으로 표현
    addition = " + ".join([str(n)] * x)
    
    # 시각적 표현
    visual = f"{addition} = {result}"
    
    return visual


@app.post("/answer", response_model=AnswerResponse)
async def calculate_answer(request: AnswerRequest) -> AnswerResponse:
    """
    구구단 문제 계산 및 설명 엔드포인트

    Args:
        request (AnswerRequest): 계산할 구구단 문제

    Returns:
        AnswerResponse: 계산된 답변과 설명

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
        
        # 시각적 표현 생성
        visual = generate_visual_explanation(n, x, result)
        
        # Claude API를 통한 설명 생성
        explanation = await get_explanation(calculation, result)
        
        # 최종 설명에 시각적 표현 추가
        full_explanation = f"{explanation}\n\n시각적 표현:\n{visual}"
        
        return AnswerResponse(
            answer=result, 
            calculation=calculation,
            explanation=full_explanation
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"계산 중 오류 발생: {str(e)}"
        ) 