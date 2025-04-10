"""
구구단 시스템 실행 스크립트

모든 에이전트 및 프론트엔드를 동시에 실행합니다.
"""
import subprocess
import os
import time
import signal
import sys
from typing import List

# 프로세스 목록
processes: List[subprocess.Popen] = []


def cleanup():
    """
    실행 중인 모든 프로세스를 종료
    """
    print("\n모든 프로세스를 종료합니다...")
    for process in processes:
        try:
            # Windows에서는 SIGTERM이 지원되지 않으므로 조건부 처리
            if os.name == 'nt':
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        except Exception as e:
            print(f"프로세스 종료 중 오류 발생: {e}")
    
    print("모든 프로세스가 종료되었습니다.")


def start_agent(command, name):
    """
    에이전트 프로세스 시작

    Args:
        command (str): 실행 명령어
        name (str): 에이전트 이름
    """
    try:
        print(f"{name} 시작 중...")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append(process)
        return process
    except Exception as e:
        print(f"{name} 시작 중 오류 발생: {e}")
        return None


def main():
    """
    메인 실행 함수
    """
    try:
        # SIGINT(Ctrl+C) 핸들러 등록
        signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

        # 에이전트1(문제 생성기) 시작
        agent1_process = start_agent("python agent1/main.py", "에이전트1(문제 생성기)")
        time.sleep(2)  # 서버가 시작될 때까지 대기

        # 에이전트2(답변기) 시작
        agent2_process = start_agent("python agent2/main.py", "에이전트2(답변기)")
        time.sleep(2)

        # 슈퍼바이저 에이전트 시작
        supervisor_process = start_agent("python supervisor/main.py", "슈퍼바이저")
        time.sleep(2)

        # 프론트엔드 시작 (개발 모드)
        frontend_process = start_agent("cd frontend && npm run dev", "프론트엔드")

        print("\n모든 서비스가 시작되었습니다.")
        print("프론트엔드: http://localhost:8080")
        print("슈퍼바이저 API: http://localhost:8000")
        print("에이전트1 API: http://localhost:5000")
        print("에이전트2 API: http://localhost:6000")
        print("종료하려면 Ctrl+C를 누르세요...\n")

        # 모든 프로세스가 실행 중인지 주기적으로 확인
        while all(process.poll() is None for process in processes):
            time.sleep(1)

        # 어떤 프로세스가 종료되었는지 확인
        for i, process in enumerate(processes):
            if process.poll() is not None:
                name = ["에이전트1", "에이전트2", "슈퍼바이저", "프론트엔드"][min(i, 3)]
                print(f"{name} 프로세스가 종료되었습니다. 종료 코드: {process.returncode}")
                
                # 표준 출력/에러 로그 출력
                stdout, stderr = process.communicate()
                if stdout:
                    print(f"[{name} stdout] {stdout}")
                if stderr:
                    print(f"[{name} stderr] {stderr}")

    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main() 