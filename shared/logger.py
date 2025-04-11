import logging
import os
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name, log_file, level=logging.INFO):
    """
    로깅 설정을 구성하는 함수
    
    Args:
        name (str): 로거 이름
        log_file (str): 로그 파일 경로
        level (int): 로깅 레벨
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 파일 핸들러 (로그 파일로 출력)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 콘솔 핸들러 (터미널에도 출력)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_agent_logger(agent_name):
    """
    에이전트용 로거를 반환하는 함수
    
    Args:
        agent_name (str): 에이전트 이름 ('supervisor', 'agent1', 'agent2')
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 실행 폴더 기준으로 로그 파일 경로 설정
    log_file = os.path.join('logs', f'{agent_name}.log')
    return setup_logger(agent_name, log_file) 