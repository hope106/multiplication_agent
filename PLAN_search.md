# 에이전트2 (답변기) Claude API 확장 계획

## 확장 개요
기존 구구단 프로젝트의 에이전트2(답변기)에 Claude API를 연결하여 계산 결과에 대한 교육적 설명을 제공하도록 확장합니다. 이를 통해 단순 계산을 넘어 아이들의 학습을 돕는 교육적 가치를 추가합니다.

## 주요 변경사항
1. 에이전트2(답변기)에 **Claude API 연결 기능** 추가
2. 메시지 스키마에 **설명(explanation) 필드** 추가
3. 프론트엔드에 **설명 표시 UI** 추가

## 구현 단계
1. **메시지 스키마 업데이트**
   - `shared/schemas/messages.py`의 `AnswerResponse` 클래스에 `explanation` 필드 추가
   ```python
   class AnswerResponse(BaseModel):
       """답변기로부터 문제 생성기로의 응답 메시지"""
       answer: int = Field(..., description="계산된 결과값")
       calculation: str = Field(..., description="전체 계산식 (예: '3×4=12')")
       explanation: Optional[str] = Field(None, description="계산 결과에 대한 교육적 설명")
   ```

2. **환경 변수 설정**
   - `.env` 파일에 Anthropic API 키 추가
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
   - `.env.example` 파일 업데이트

3. **에이전트2(답변기) 확장**
   - `agent2/app/api.py`에 Claude API 호출 함수 추가
   - `/answer` 엔드포인트 업데이트하여 설명 생성 및 반환

4. **슈퍼바이저 업데이트**
   - `supervisor/app/api.py`의 답변 처리 로직에 설명 필드 처리 추가
   - 웹소켓 메시지에 설명 내용 포함

5. **프론트엔드 업데이트**
   - 설명 표시를 위한 UI 컴포넌트 추가
   - 채팅 메시지 형식 확장

## Claude API 연결 구현
```python
async def get_explanation(calculation: str, answer: int) -> str:
    """
    Claude API를 호출하여 구구단 계산에 대한 설명을 생성합니다.
    
    Args:
        calculation (str): 전체 계산식 (예: "4×5=20")
        answer (int): 계산 결과
        
    Returns:
        str: 생성된 설명
    """
    prompt = f"다음 구구단 계산 결과를 초등학생이 이해할 수 있도록 간단하게 설명해주세요:\n\n계산: {calculation}\n결과: {answer}\n\n설명은 간결하게 50단어 이내로 작성해주세요."
    
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
                    "max_tokens": 100,
                    "temperature": 0.5,
                    "system": "당신은 초등학생에게 구구단을 가르치는 친절한 선생님입니다.",
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
```

## 에이전트2 엔드포인트 업데이트
```python
@app.post("/answer", response_model=AnswerResponse)
async def calculate_answer(request: AnswerRequest) -> AnswerResponse:
    """
    구구단 문제 계산 및 설명 엔드포인트
    
    Args:
        request (AnswerRequest): 계산할 구구단 문제
        
    Returns:
        AnswerResponse: 계산된 답변과 설명
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
        
        # Claude API를 통한 설명 생성
        explanation = await get_explanation(calculation, result)
        
        return AnswerResponse(
            answer=result, 
            calculation=calculation,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"계산 중 오류 발생: {str(e)}"
        )
```

## 에이전트2 (답변기) 프롬프트 업데이트
당신은 구구단 문제의 답을 계산하고 설명하는 에이전트입니다. 문제 생성기로부터 문제를 받아 정확한 답을 계산하고, Claude API를 활용하여 초등학생 수준의 설명을 제공합니다.

1. 문제 생성기로부터 {"problem": "N×X="} 형식의 JSON 데이터를 받습니다.
2. 수식을 분석하여 N과 X 값을 추출합니다.
3. N×X 계산을 수행합니다.
4. Claude API를 호출하여 계산 결과에 대한 교육적 설명을 생성합니다.
5. 계산 결과와 설명을 JSON 형태로 반환합니다: {"answer": 결과값, "calculation": "N×X=결과값", "explanation": "설명 텍스트"}

항상 정확한 계산을 수행하고, 초등학생이 이해할 수 있는 명확한 설명을 제공합니다.

## 채팅 인터페이스 응답 예시
```
에이전트1: 4×2=
에이전트2: 4×2=8
에이전트2 (설명): 4를 2번 더하는 거예요. 4+4=8이 됩니다. 두 그룹의 4개씩 사과가 있다고 생각하면, 전체 사과는 8개입니다.
```

## A2A 패러다임 강화 효과
이번 확장을 통해 에이전트2는 단순 계산을 넘어 교육적 설명을 제공하는 전문화된 역할을 갖게 됩니다. 이는 A2A(Agent-to-Agent) 통신의 핵심 가치인 "전문화된 에이전트 간 협업을 통한 복합적 문제 해결"을 더 잘 보여줍니다. 각 에이전트가 자신의 전문 영역에 집중하면서도 공통 목표를 위해 조화롭게 협력하는 모델을 구현합니다. 