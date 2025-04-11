import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

export const useAgentStore = defineStore('agents', () => {
  const supervisor = ref(false);
  const agent1 = ref(false);
  const agent2 = ref(false);
  const isChecking = ref(false);

  // 에이전트 상태 확인
  async function checkAgentsStatus() {
    isChecking.value = true;
    
    try {
      // 슈퍼바이저 상태 확인
      await checkAgent('supervisor', 'http://localhost:8000/health');
    } catch (error) {
      supervisor.value = false;
      console.error('슈퍼바이저 상태 확인 실패:', error);
    }
    
    try {
      // 에이전트1(문제 생성기) 상태 확인
      await checkAgent('agent1', 'http://localhost:5000/health');
    } catch (error) {
      agent1.value = false;
      console.error('문제 생성기 상태 확인 실패:', error);
    }
    
    try {
      // 에이전트2(답변기) 상태 확인
      await checkAgent('agent2', 'http://localhost:6001/health');
    } catch (error) {
      agent2.value = false;
      console.error('답변기 상태 확인 실패:', error);
    }
    
    isChecking.value = false;
  }

  // 개별 에이전트 상태 확인
  async function checkAgent(agentName, url) {
    try {
      const response = await axios.get(url, { timeout: 10000 });
      if (response.status === 200) {
        if (agentName === 'supervisor') {
          supervisor.value = true;
        } else if (agentName === 'agent1') {
          agent1.value = true;
        } else if (agentName === 'agent2') {
          agent2.value = true;
        }
        return true;
      }
    } catch (error) {
      if (agentName === 'supervisor') {
        supervisor.value = false;
      } else if (agentName === 'agent1') {
        agent1.value = false;
      } else if (agentName === 'agent2') {
        agent2.value = false;
      }
      throw error;
    }
    return false;
  }

  return {
    supervisor,
    agent1,
    agent2,
    isChecking,
    checkAgentsStatus
  };
}); 