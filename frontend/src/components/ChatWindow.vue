<template>
  <div class="chat-window">
    <div class="chat-container" ref="chatContainer">
      <template v-for="(message, index) in messages" :key="index">
        <div :class="['message', getMessageClass(message)]">
          <div class="message-sender">{{ getSenderDisplay(message.sender) }}</div>
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time" v-if="message.timestamp">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
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

const messageStore = useMessageStore();
const chatContainer = ref(null);
const userInput = ref('');

const messages = computed(() => messageStore.messages);
const isConnected = computed(() => messageStore.isConnected);

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

.clearfix {
  clear: both;
}
</style> 