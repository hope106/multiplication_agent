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

<script setup>
import { computed } from 'vue';
import { useMessageStore } from '../store/messages';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const props = defineProps({
  content: {
    type: String,
    required: true
  }
});

const messageStore = useMessageStore();
const show = computed(() => messageStore.showExplanations);

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
</script>

<style>
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
</style>

<style scoped>
.explanation-message {
  max-width: 90%;
  margin-left: 2rem;
  margin-top: 0.25rem;
  animation: slideIn 0.3s ease-out;
  word-break: break-word;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.explanation-content {
  width: 100%;
  overflow-wrap: break-word;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 