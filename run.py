"""
전체 시스템 실행 스크립트

슈퍼바이저, 에이전트1, 에이전트2 프로세스를 모두 실행합니다.
"""
import subprocess
import sys
import os
import time
import signal
from dotenv import load_dotenv
import argparse
from pathlib import Path
import platform
import socket

# 현재 파일 위치를 기준으로 프로젝트 루트 경로를 추가
sys.path.append(str(Path(__file__).parent))

# 공통 로깅 모듈 임포트
from shared.logger import get_agent_logger

# 로깅 설정
logger = get_agent_logger("main")

# .env 파일 로드 (있는 경우)
load_dotenv()

# 실행 프로세스 관리
processes = []

def run_command(command, name):
    """
    명령어를 서브프로세스로 실행하고 프로세스 객체를 반환합니다.
    
    Args:
        command (list): 실행할 명령어와 인자들
        name (str): 프로세스 이름
        
    Returns:
        subprocess.Popen: 실행된 프로세스 객체
    """
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows에서는 새 콘솔 창에서 실행 (프로세스 분리)
            process = subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )
        else:
            # Linux, MacOS에서는 같은 터미널에서 실행하되 출력 파이프
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )
        
        logger.info(f"{name} 프로세스 시작 (PID: {process.pid})")
        return process
    
    except Exception as e:
        logger.error(f"{name} 프로세스 시작 실패: {e}")
        return None


def check_port_in_use(port):
    """
    지정된 포트가 이미 사용 중인지 확인합니다.
    
    Args:
        port (int): 확인할 포트 번호
        
    Returns:
        bool: 포트가 사용 중이면 True, 아니면 False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port(port):
    """
    지정된 포트를 사용하는 프로세스를 종료합니다.
    
    Args:
        port (int): 프로세스를 종료할 포트
    """
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(f"FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr {port}') DO taskkill /F /PID %P", shell=True)
        else:
            # Mac/Linux
            pid_cmd = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if pid_cmd.stdout.strip():
                subprocess.run(f"kill -9 {pid_cmd.stdout.strip()}", shell=True)
    except Exception as e:
        logger.error(f"포트 {port}의 프로세스 종료 중 오류: {e}")


def start_all():
    """
    모든 컴포넌트 실행
    """
    logger.info("🚀 구구단 시스템 전체 실행을 시작합니다...")
    
    # 포트 사용 중인지 확인 및 프로세스 종료
    ports = [8000, 5000, 6001]
    for port in ports:
        if check_port_in_use(port):
            logger.warning(f"포트 {port}가 이미 사용 중입니다. 해당 프로세스를 종료합니다.")
            kill_process_on_port(port)
            time.sleep(1)  # 프로세스가 완전히 종료되도록 대기
    
    try:
        # 슈퍼바이저 서버 실행
        supervisor = run_command(["python", "supervisor/main.py"], "슈퍼바이저")
        if supervisor:
            processes.append(supervisor)
            time.sleep(2)  # 슈퍼바이저가 먼저 시작되도록 대기 시간 증가
        
        # 에이전트1 (문제 생성기) 실행
        agent1 = run_command(["python", "agent1/main.py"], "문제 생성기")
        if agent1:
            processes.append(agent1)
            time.sleep(2)
        
        # 에이전트2 (답변기) 실행
        agent2 = run_command(["python", "agent2/main.py"], "답변기")
        if agent2:
            processes.append(agent2)
            time.sleep(2)
        
        # 프론트엔드 실행 (개발 서버)
        system = platform.system()
        if system == "Windows":
            frontend_cmd = ["cmd", "/c", "cd", "frontend", "&&", "npm", "run", "dev"]
        else:
            frontend_cmd = ["sh", "-c", "cd frontend && npm run dev"]
            
        frontend = run_command(frontend_cmd, "프론트엔드")
        if frontend:
            processes.append(frontend)
        
        logger.info("✅ 모든 컴포넌트가 실행되었습니다!")
        logger.info("📊 슈퍼바이저: http://localhost:8000")
        logger.info("🧮 문제 생성기: http://localhost:5000")
        logger.info("🤖 답변기: http://localhost:6001")
        logger.info("🖥️  프론트엔드: http://localhost:3000 또는 http://localhost:5173")
        logger.info("종료하려면 Ctrl+C를 누르세요...")
        
        # 메인 프로세스가 종료되지 않도록 대기
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        logger.info("👋 사용자에 의해 프로그램이 종료됩니다...")
        cleanup()


def cleanup():
    """
    모든 서브프로세스 종료 처리
    """
    logger.info("🧹 실행 중인 모든 프로세스를 종료합니다...")
    
    for process in processes:
        if process and process.poll() is None:  # 프로세스가 여전히 실행 중인지 확인
            try:
                # Unix/Windows 호환 종료 처리
                if platform.system() == "Windows":
                    process.terminate()
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                logger.info(f"PID {process.pid} 종료 요청 전송")
            except Exception as e:
                logger.error(f"프로세스 종료 오류: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2A 프로토콜 구구단 시스템 실행")
    parser.add_argument("--frontend-only", action="store_true", help="프론트엔드만 실행")
    parser.add_argument("--backend-only", action="store_true", help="백엔드만 실행")
    
    args = parser.parse_args()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup())
    
    try:
        start_all()
    except Exception as e:
        logger.error(f"시스템 실행 중 오류 발생: {e}")
        cleanup()
        sys.exit(1) 