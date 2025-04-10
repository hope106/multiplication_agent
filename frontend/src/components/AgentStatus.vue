<template>
  <div class="agent-status-container flex">
    <div class="agent-status">
      <div :class="['status-indicator', agentStore.supervisor ? 'status-active' : 'status-inactive']"></div>
      <span class="text-xs font-medium">슈퍼바이저</span>
    </div>
    
    <div class="agent-status">
      <div :class="['status-indicator', agentStore.agent1 ? 'status-active' : 'status-inactive']"></div>
      <span class="text-xs font-medium">문제 생성기</span>
    </div>
    
    <div class="agent-status">
      <div :class="['status-indicator', agentStore.agent2 ? 'status-active' : 'status-inactive']"></div>
      <span class="text-xs font-medium">답변기</span>
    </div>
    
    <el-button 
      type="text" 
      size="small" 
      @click="refreshStatus" 
      :loading="agentStore.isChecking"
    >
      <i class="el-icon-refresh"></i>
    </el-button>
  </div>
</template>

<script setup>
import { useAgentStore } from '../store/agents';

const agentStore = useAgentStore();

const refreshStatus = () => {
  agentStore.checkAgentsStatus();
};
</script>

<style scoped>
.agent-status-container {
  display: flex;
  align-items: center;
}
</style> 