import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useMessageStore = defineStore('messages', () => {
  const messages = ref([]);
  const isConnected = ref(false);
  const showExplanations = ref(true);
  let socket = null;

  // 초기화 시 로컬 스토리지에서 설명 표시 설정 로드
  try {
    const savedPreference = localStorage.getItem('showExplanations');
    if (savedPreference !== null) {
      showExplanations.value = JSON.parse(savedPreference);
    }
  } catch (e) {
    console.error('설명 표시 설정 로드 오류:', e);
  }

  // 웹소켓 연결 초기화
  function initWebSocket() {
    if (socket && socket.readyState !== WebSocket.CLOSED) {
      return;
    }

    console.log("웹소켓 연결 시도...");
    
    // 웹소켓 연결 수정 - 절대 경로로 변경
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = 'localhost'; // 명시적으로 localhost 지정
    const wsPort = '8000';
    const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws`;
    
    socket = new WebSocket(wsUrl);
    console.log(`웹소켓 연결 URL: ${wsUrl}`);

    // 웹소켓 이벤트 핸들러
    socket.onopen = () => {
      console.log("웹소켓 연결 성공!");
      isConnected.value = true;
      addMessage({
        type: 'system_message',
        content: '연결되었습니다. 구구단을 시작해보세요!',
        sender: 'system',
        timestamp: new Date().toISOString()
      });
    };

    socket.onmessage = (event) => {
      console.log("메시지 수신:", event.data);
      try {
        const data = JSON.parse(event.data);
        addMessage(data);
      } catch (e) {
        console.error('메시지 파싱 오류:', e);
      }
    };

    socket.onclose = (event) => {
      console.log("웹소켓 연결 종료:", event);
      isConnected.value = false;
      addMessage({
        type: 'system_message',
        content: '연결이 종료되었습니다. 자동으로 재연결을 시도합니다...',
        sender: 'system',
        timestamp: new Date().toISOString()
      });
      
      // 3초 후 자동 재연결 시도
      setTimeout(() => {
        initWebSocket();
      }, 3000);
    };

    socket.onerror = (error) => {
      console.error("웹소켓 오류:", error);
      isConnected.value = false;
      addMessage({
        type: 'system_message',
        content: '연결 오류가 발생했습니다. 자동으로 재연결을 시도합니다...',
        sender: 'system',
        timestamp: new Date().toISOString()
      });
      
      // 소켓 닫기 시도
      try {
        socket.close();
      } catch (e) {
        console.error("소켓 닫기 오류:", e);
      }
      
      // 3초 후 재연결 시도
      setTimeout(() => {
        initWebSocket();
      }, 3000);
    };
  }

  // 설명 표시 여부 토글
  function toggleExplanations() {
    showExplanations.value = !showExplanations.value;
    // 로컬 스토리지에 설정 저장
    localStorage.setItem('showExplanations', JSON.stringify(showExplanations.value));
  }

  // 메시지 추가
  function addMessage(message) {
    // 타임스탬프가 없으면 현재 시간 추가
    if (!message.timestamp) {
      message.timestamp = new Date().toISOString();
    }
    
    // 메시지에 고유 ID 추가
    message.id = `msg-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // 설명 메시지인 경우 부모 메시지와 연결
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
    
    messages.value.push(message);
    
    // 메시지가 너무 많으면 오래된 것부터 제거
    if (messages.value.length > 100) {
      messages.value.shift();
    }
  }

  // 사용자 메시지 전송
  function sendMessage(text) {
    if (!isConnected.value || !socket) return;
    
    const message = {
      type: 'user_message',
      content: text,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    // 메시지 목록에 추가
    addMessage(message);
    
    // 웹소켓으로 전송
    console.log("메시지 전송:", message);
    socket.send(JSON.stringify(message));
  }

  return {
    messages,
    isConnected,
    showExplanations,
    initWebSocket,
    addMessage,
    sendMessage,
    toggleExplanations
  };
}); 