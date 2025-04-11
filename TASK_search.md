# 2A 프로토콜 구구단 프로젝트 확장 작업

## 작업 목록 (날짜)

### Claude API 연결 설정
- [x] Anthropic API 키 환경 변수 설정 (.env 파일)
- [x] API 요청 래퍼 클래스 구현
- [x] API 호출 오류 처리 로직 구현
- [x] API 키 보안 확보

### 답변기 에이전트(Agent2) 확장
- [x] 메시지 스키마에 설명(explanation) 필드 추가
- [x] 계산 결과에 대한 설명 생성 로직 추가
- [x] Claude API 호출 기능 통합
- [x] 최적 프롬프트 설계 (구구단 설명에 적합한)
- [x] 설명 길이 최적화 및 형식 조정

### 슈퍼바이저 에이전트 업데이트
- [x] 확장된 답변 형식 처리 로직 수정
- [x] 웹소켓 메시지 형식 업데이트

### 프론트엔드 업데이트
- [x] 설명 표시 UI 컴포넌트 추가
- [x] 채팅 인터페이스 레이아웃 조정
- [x] 설명 토글 기능 추가 (선택 사항)

### 테스트
- [x] Claude API 연결 단위 테스트
- [x] 확장된 답변기 기능 테스트
- [x] 통합 테스트 업데이트

## 클로드 API 프롬프트 템플릿
```
다음 구구단 계산 결과를 초등학생이 이해할 수 있도록 간단하게 설명해주세요:

계산: {calculation}
결과: {answer}

설명은 간결하게 50단어 이내로 작성해주세요.
```

## 구현 예시
**API 호출 예시:**
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
    
    # Claude API 호출 코드
    # ...
    
    return explanation
```

**응답 예시:**
```json
{
  "answer": 20,
  "calculation": "4×5=20",
  "explanation": "4를 5번 더하는 것과 같아요. 4+4+4+4+4=20이 되죠. 또는 5를 4번 더하는 것으로 생각할 수도 있어요. 5+5+5+5=20이 됩니다."
}
``` 