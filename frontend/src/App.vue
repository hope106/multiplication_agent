<template>
  <div class="app-container">
    <header class="bg-white shadow-md p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold text-blue-600">2A 프로토콜 구구단</h1>
        <div class="flex">
          <AgentStatus />
        </div>
      </div>
    </header>

    <main class="container mx-auto py-4">
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <ChatWindow />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useMessageStore } from './store/messages';
import { useAgentStore } from './store/agents';
import ChatWindow from './components/ChatWindow.vue';
import AgentStatus from './components/AgentStatus.vue';

const messageStore = useMessageStore();
const agentStore = useAgentStore();

onMounted(() => {
  // 웹소켓 연결 및 상태 확인 초기화
  messageStore.initWebSocket();
  agentStore.checkAgentsStatus();
});
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style> 