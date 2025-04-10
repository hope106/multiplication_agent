import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useMessageStore = defineStore('messages', () => {
  const messages = ref([]);
  const isConnected = ref(false);
  let socket = null;

  // 웹소켓 연결 초기화
  function initWebSocket() {
    if (socket && socket.readyState !== WebSocket.CLOSED) {
      return;
    }

    console.log("웹소켓 연결 시도...");
    
    // 웹소켓 연결 수정 - 절대 경로로 변경
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws`;
    
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
        content: '연결이 종료되었습니다. 페이지를 새로고침하여 다시 연결해주세요.',
        sender: 'system',
        timestamp: new Date().toISOString()
      });
    };

    socket.onerror = (error) => {
      console.error("웹소켓 오류:", error);
      isConnected.value = false;
      addMessage({
        type: 'system_message',
        content: '연결 오류가 발생했습니다. 나중에 다시 시도해주세요.',
        sender: 'system',
        timestamp: new Date().toISOString()
      });
    };
  }

  // 메시지 추가
  function addMessage(message) {
    // 타임스탬프가 없으면 현재 시간 추가
    if (!message.timestamp) {
      message.timestamp = new Date().toISOString();
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
    initWebSocket,
    addMessage,
    sendMessage
  };
}); 