"""
구구단 프로젝트 메시지 스키마 정의 모듈

에이전트 간 통신에 사용되는 메시지 형식을 정의합니다.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class SupervisorRequest(BaseModel):
    """사용자로부터 슈퍼바이저로의 요청 메시지"""
    message: str = Field(..., description="사용자 요청 메시지")


class SupervisorResponse(BaseModel):
    """슈퍼바이저로부터 사용자로의 응답 메시지"""
    message: str = Field(..., description="슈퍼바이저 응답 메시지")


class ProblemRequest(BaseModel):
    """슈퍼바이저로부터 문제 생성기로의 요청 메시지"""
    table: int = Field(..., description="구구단 단수 (N)", ge=1, le=100)
    stop_value: Optional[int] = Field(None, description="종료할 결과값 (M)")


class ProblemGenerated(BaseModel):
    """문제 생성기로부터 슈퍼바이저로의 문제 생성 메시지"""
    problem: str = Field(..., description="생성된 구구단 문제 (예: '3×4=')")
    multiplier: int = Field(..., description="첫 번째 숫자 (N)")
    multiplicand: int = Field(..., description="두 번째 숫자 (X)")
    status: Literal["continue", "completed"] = Field(
        "continue", description="구구단 진행 상태"
    )


class AnswerRequest(BaseModel):
    """문제 생성기로부터 답변기로의 문제 전송 메시지"""
    problem: str = Field(..., description="구구단 문제 (예: '3×4=')")


class AnswerResponse(BaseModel):
    """답변기로부터 문제 생성기로의 응답 메시지"""
    answer: int = Field(..., description="계산된 결과값")
    calculation: str = Field(..., description="전체 계산식 (예: '3×4=12')")


class StatusUpdate(BaseModel):
    """에이전트 상태 업데이트 메시지"""
    agent: Literal["supervisor", "problem_generator", "answer_provider"] = Field(
        ..., description="에이전트 이름"
    )
    status: Literal["active", "inactive", "error"] = Field(
        ..., description="에이전트 상태"
    )
    message: Optional[str] = Field(None, description="상태 관련 추가 메시지")


class WebSocketMessage(BaseModel):
    """웹소켓을 통한 메시지"""
    type: Literal["user_message", "system_message", "problem", "answer", "status_update"] = Field(
        ..., description="메시지 유형"
    )
    content: str = Field(..., description="메시지 내용")
    sender: Literal["user", "system", "agent1", "agent2", "supervisor"] = Field(
        ..., description="메시지 발신자"
    )
    timestamp: Optional[str] = Field(None, description="메시지 타임스탬프") 