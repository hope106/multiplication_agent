<template>
  <div class="agent-status-container flex flex-col">
    <div class="flex mb-2">
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
    
    <div class="flex">
      <el-dropdown @command="viewLog" class="mr-2">
        <el-button type="primary" size="small">
          로그 보기 <i class="el-icon-arrow-down"></i>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="supervisor">슈퍼바이저 로그</el-dropdown-item>
            <el-dropdown-item command="agent1">문제 생성기 로그</el-dropdown-item>
            <el-dropdown-item command="agent2">답변기 로그</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <el-dialog
        v-model="logDialogVisible"
        :title="`${selectedAgent} 로그`"
        width="80%"
      >
        <div class="log-content">
          <pre v-if="logContent">{{ logContent }}</pre>
          <div v-else class="text-gray-500">로그를 불러오는 중...</div>
        </div>
        <template #footer>
          <div class="flex justify-between">
            <el-button @click="refreshLog" type="primary" plain>새로고침</el-button>
            <el-button @click="logDialogVisible = false">닫기</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAgentStore } from '../store/agents';
import axios from 'axios';

const agentStore = useAgentStore();
const logDialogVisible = ref(false);
const selectedAgent = ref('');
const logContent = ref('');

const refreshStatus = () => {
  agentStore.checkAgentsStatus();
};

const viewLog = async (agent) => {
  selectedAgent.value = agent === 'supervisor' ? '슈퍼바이저' : 
                        agent === 'agent1' ? '문제 생성기' : '답변기';
  logDialogVisible.value = true;
  logContent.value = '';
  await refreshLog();
};

const refreshLog = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/logs/${selectedAgent.value === '슈퍼바이저' ? 'supervisor' : 
                                     selectedAgent.value === '문제 생성기' ? 'agent1' : 'agent2'}`);
    logContent.value = response.data.log_content;
  } catch (error) {
    console.error('로그 불러오기 오류:', error);
    logContent.value = '로그를 불러올 수 없습니다. 서버 상태를 확인해주세요.';
  }
};
</script>

<style scoped>
.agent-status-container {
  display: flex;
  align-items: center;
}

.agent-status {
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-active {
  background-color: #67C23A;
}

.status-inactive {
  background-color: #F56C6C;
}

.log-content {
  max-height: 500px;
  overflow-y: auto;
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}
</style> 