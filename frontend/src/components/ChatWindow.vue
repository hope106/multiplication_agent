<template>
  <div class="chat-window">
    <div class="chat-header p-2 bg-gray-100 flex justify-between items-center">
      <div class="text-sm text-gray-600">구구단 채팅</div>
      <button 
        @click="toggleExplanations" 
        class="explanation-toggle flex items-center text-xs px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300 transition-colors"
      >
        <span v-if="showExplanations">설명 숨기기</span>
        <span v-else>설명 표시하기</span>
      </button>
    </div>
    
    <div class="chat-container" ref="chatContainer">
      <template v-for="(message, index) in messages" :key="message.id || index">
        <!-- 일반 메시지 표시 -->
        <div v-if="message.type !== 'explanation'" :class="['message', getMessageClass(message)]">
          <div class="message-sender">{{ getSenderDisplay(message.sender) }}</div>
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time" v-if="message.timestamp">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
        
        <!-- 설명 메시지 표시 -->
        <ExplanationMessage 
          v-else-if="message.type === 'explanation'"
          :content="message.content"
        />
        
        <div class="clearfix"></div>
      </template>
    </div>
    
    <div class="chat-input bg-gray-100 p-4">
      <div class="flex">
        <el-input
          v-model="userInput"
          placeholder="구구단을 시작하려면 '5단 구구단 시작해줘'와 같이 입력하세요."
          @keyup.enter="sendMessage"
          class="flex-grow"
          :disabled="!isConnected"
        />
        <el-button 
          type="primary" 
          @click="sendMessage" 
          class="ml-2" 
          :disabled="!isConnected || !userInput.trim()"
        >
          전송
        </el-button>
      </div>
      <div class="mt-2 text-xs text-gray-500">
        * 예: "5단 구구단 시작해줘" 또는 "7단 구구단 시작해줘. 정답이 50에 도달하면 멈춰줘."
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useMessageStore } from '../store/messages';
import ExplanationMessage from './ExplanationMessage.vue';

const messageStore = useMessageStore();
const chatContainer = ref(null);
const userInput = ref('');

const messages = computed(() => messageStore.messages);
const isConnected = computed(() => messageStore.isConnected);
const showExplanations = computed(() => messageStore.showExplanations);

// 토글 설명 표시
const toggleExplanations = () => {
  messageStore.toggleExplanations();
};

// 메시지 타입에 따른 클래스 반환
const getMessageClass = (message) => {
  switch (message.type) {
    case 'user_message':
      return 'user-message';
    case 'system_message':
      return 'system-message';
    case 'problem':
      return 'problem-message';
    case 'answer':
      return 'answer-message';
    default:
      return 'system-message';
  }
};

// 발신자 표시 이름 반환
const getSenderDisplay = (sender) => {
  switch (sender) {
    case 'user':
      return '사용자';
    case 'system':
      return '시스템';
    case 'agent1':
      return '문제 생성기';
    case 'agent2':
      return '답변기';
    case 'supervisor':
      return '슈퍼바이저';
    default:
      return sender;
  }
};

// 타임스탬프 형식 변환
const formatTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return '';
  }
};

// 사용자 메시지 전송
const sendMessage = () => {
  if (!userInput.value.trim() || !isConnected.value) return;
  
  messageStore.sendMessage(userInput.value);
  userInput.value = '';
};

// 메시지 목록이 변경될 때마다 스크롤을 최하단으로 이동
watch(messages, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}, { deep: true });
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
}

.chat-header {
  border-bottom: 1px solid #e2e8f0;
}

.explanation-toggle {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  background-color: #edf2f7;
  transition: background-color 0.2s;
}

.explanation-toggle:hover {
  background-color: #e2e8f0;
}

.chat-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  margin-bottom: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  max-width: 80%;
  position: relative;
}

.user-message {
  background-color: #4299e1;
  color: white;
  margin-left: auto;
}

.system-message,
.problem-message,
.answer-message {
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  margin-right: auto;
}

.problem-message {
  background-color: #feebc8;
}

.answer-message {
  background-color: #c6f6d5;
}

.message-sender {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.message-content {
  word-break: break-word;
}

.message-time {
  font-size: 0.625rem;
  opacity: 0.75;
  position: absolute;
  bottom: 0.25rem;
  right: 0.5rem;
}

.clearfix {
  clear: both;
}
</style> 