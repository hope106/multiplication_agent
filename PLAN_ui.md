# 구구단 프로젝트 프론트엔드 UI 업데이트 계획

## 개요
Claude API를 통해 제공되는 구구단 계산 설명 기능을 사용자에게 효과적으로 표시하기 위한 프론트엔드 UI 업데이트 계획입니다. 구구단 계산 과정을 더 교육적으로 만들기 위해 답변에 대한 설명을 제공합니다.

## 기술 스택 (현재 구현됨)
- **Vue3**: 웹 인터페이스 및 채팅 UI 구현
- **Pinia**: 상태 관리
- **TailwindCSS**: UI 컴포넌트 및 스타일링
- **WebSocket**: 실시간 통신
- **Marked**: 마크다운 파싱 및 렌더링
- **DOMPurify**: HTML 정화 (XSS 방지)

## UI 구성 요소 업데이트

### 1. 채팅 메시지 컴포넌트 확장 (구현 완료)
- **메시지 유형 추가**: 기존 메시지 유형("user_message", "system_message", "problem", "answer")에 "explanation" 유형 추가
- **설명 메시지 스타일링**: 
  - 일반 답변 메시지와 구분되는 시각적 차별화 (파란 배경, 전구 아이콘 등)
  - 들여쓰기를 통해 해당 답변에 종속된 것임을 시각적으로 표현
  - 텍스트 스타일 변경 (폰트 크기, 색상, 굵기 등)
- **마크다운 렌더링 지원**: 설명 메시지에 마크다운 형식 지원

### 2. 메시지 표시 흐름 업데이트 (구현 완료)
```
에이전트1: 4×2=
에이전트2: 4×2=8
에이전트2 (설명): 4를 2번 더하는 거예요. 4+4=8이 됩니다. 두 그룹의 4개씩 사과가 있다고 생각하면, 전체 사과는 8개입니다.
```

### 3. 설명 토글 기능 (구현 완료)
- **토글 버튼 추가**: 채팅 인터페이스 상단에 설명 표시/숨김 전환 버튼 추가
- **사용자 기본 설정**: 설명 표시 기본값을 로컬 스토리지에 저장하여 사용자 설정 유지
- ~~**개별 설명 토글**: 각 메시지에 개별적으로 설명을 펼치고 접을 수 있는 작은 버튼 추가~~ (미구현)

### 4. 시각적 요소 개선 (구현 완료)
- **아이콘 추가**: 설명 메시지 옆에 전구 아이콘 추가
- **애니메이션**: 설명이 나타날 때 부드러운 슬라이드인 애니메이션 적용
- **스크롤 처리**: 설명이 추가될 때 자동 스크롤 조정
- **마크다운 스타일링**: 설명 메시지에 마크다운 스타일 적용

### 5. 시각적 표현 개선 (구현 완료)
- **시각적 계산 표현**: 구구단 계산 과정을 덧셈 방식으로 시각화 (예: "5 + 5 + 5 = 15")
- **마크다운 형식 적용**: 설명 텍스트에 굵은 글씨, 목록, 코드 등의 마크다운 서식 적용

## 현재 컴포넌트 구조
```
App.vue
├── AgentStatus.vue (에이전트 상태 표시)
└── ChatWindow.vue (채팅 인터페이스)
    └── ExplanationMessage.vue (설명 메시지 컴포넌트)
```

## Pinia 스토어 현황
- **messages.js**: 메시지 상태 관리, 웹소켓 연결, 설명 토글 기능
- **agents.js**: 에이전트 상태 관리 및 헬스체크

## ExplanationMessage 컴포넌트 구현 현황
```vue
<template>
  <div 
    v-if="show"
    class="explanation-message ml-8 mt-1 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-300 text-sm text-gray-700"
  >
    <div class="flex items-start">
      <div class="mr-2">
        <div class="lightbulb-icon text-blue-500">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="h-4 w-4">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
      </div>
      <div class="explanation-content markdown-body" v-html="renderedContent"></div>
    </div>
  </div>
</template>
```

## 마크다운 렌더링 지원 (구현 완료)
현재 구현에서는 `marked` 라이브러리와 `DOMPurify`를 사용하여 마크다운 텍스트를 안전하게 HTML로 변환하고 렌더링합니다:

```javascript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// 마크다운을 HTML로 변환하고 보안을 위해 정화
const renderedContent = computed(() => {
  try {
    // 마크다운을 HTML로 변환
    const rawHtml = marked.parse(props.content);
    // XSS 공격 방지를 위한 HTML 정화
    return DOMPurify.sanitize(rawHtml);
  } catch (error) {
    console.error('마크다운 변환 오류:', error);
    return props.content;
  }
});
```

## 개선된 마크다운 스타일링 (구현 완료)
```css
/* 마크다운 스타일 */
.markdown-body h1, .markdown-body h2, .markdown-body h3,
.markdown-body h4, .markdown-body h5, .markdown-body h6 {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.markdown-body p {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.markdown-body ul, .markdown-body ol {
  padding-left: 1.5em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.markdown-body li {
  margin-bottom: 0.25em;
}

.markdown-body code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
}

.markdown-body pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.5em;
  border-radius: 3px;
  overflow-x: auto;
}

.markdown-body blockquote {
  padding-left: 1em;
  border-left: 0.25em solid #ddd;
  color: #666;
  margin-left: 0;
  margin-right: 0;
}

.markdown-body a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}
```

## 메시지 필터링 (구현 완료)
`messages.js` 스토어에서 설명 표시 여부에 따라 메시지를 필터링하는 기능:

```javascript
// 설명 표시 여부 토글
function toggleExplanations() {
  showExplanations.value = !showExplanations.value;
  // 로컬 스토리지에 설정 저장
  localStorage.setItem('showExplanations', JSON.stringify(showExplanations.value));
}

// 메시지 추가 시 설명 메시지와 부모 메시지 연결
if (message.type === 'explanation' && messages.value.length > 0) {
  // 가장 최근 답변 메시지 찾기
  const lastAnswerIndex = [...messages.value].reverse()
    .findIndex(m => m.type === 'answer');
  
  if (lastAnswerIndex >= 0) {
    const actualIndex = messages.value.length - 1 - lastAnswerIndex;
    message.parentId = messages.value[actualIndex].id;
    messages.value[actualIndex].hasExplanation = true;
  }
}
```

## 추가 개선 항목 (미구현)
1. **MessageGroup 컴포넌트 추가**: 답변과 설명을 함께 그룹화하는 컴포넌트 구현 필요
2. **개별 설명 토글 기능**: 각 설명 메시지를 개별적으로 토글할 수 있는 기능 추가
3. **코드 블록 하이라이팅**: 마크다운의 코드 블록에 대한 구문 강조 기능 추가
4. **테마 지원**: 라이트/다크 테마 전환 기능 구현
5. **모바일 대응**: 반응형 디자인 개선 및 모바일 친화적 UI 최적화
6. **접근성 개선**: 키보드 네비게이션, 스크린 리더 지원 등 추가

## 구현 우선순위 (업데이트)
1. ✅ **구현 완료**: 설명 메시지 표시 기능
2. ✅ **구현 완료**: 설명 메시지 스타일링
3. ✅ **구현 완료**: 전체 설명 표시/숨김 토글 기능
4. ✅ **구현 완료**: 마크다운 렌더링 지원
5. 🔄 **구현 중**: 메시지 그룹화 및 개선된 시각화 
6. 🔜 **구현 예정**: 개별 설명 펼치기/접기 기능
7. 🔜 **구현 예정**: 테마 지원 및 모바일 최적화

## 예상 추가 작업 시간
- MessageGroup 컴포넌트 구현: 2-3시간
- 개별 설명 토글 기능: 1-2시간
- 코드 블록 하이라이팅: 1시간
- 테마 지원: 2-3시간
- 모바일 최적화: 2-3시간
- 접근성 개선: 2-3시간

총 추가 작업 시간: 약 10-15시간 