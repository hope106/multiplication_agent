"""
웹소켓 연결 관리 모듈

클라이언트의 웹소켓 연결을 관리하는 기능을 제공합니다.
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json


class ConnectionManager:
    """
    웹소켓 클라이언트 연결을 관리하는 클래스
    
    클라이언트 연결 상태 관리 및 메시지 브로드캐스트 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        ConnectionManager 초기화
        """
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        새로운 클라이언트 연결 수락
        
        Args:
            websocket (WebSocket): 웹소켓 연결 객체
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        클라이언트 연결 종료 처리
        
        Args:
            websocket (WebSocket): 웹소켓 연결 객체
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        모든 클라이언트에게 메시지 브로드캐스트
        
        Args:
            message (Dict[str, Any]): 전송할 메시지 데이터
        """
        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # 연결 오류 발생 시 나중에 제거할 목록에 추가
                disconnected_clients.append(connection)
        
        # 오류가 발생한 연결 제거
        for connection in disconnected_clients:
            self.disconnect(connection)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        특정 클라이언트에게만 메시지 전송
        
        Args:
            message (Dict[str, Any]): 전송할 메시지 데이터
            websocket (WebSocket): 메시지를 수신할 웹소켓 연결 객체
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            # 연결 오류 발생 시 연결 제거
            self.disconnect(websocket) 