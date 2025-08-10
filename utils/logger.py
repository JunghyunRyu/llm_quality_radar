"""
로깅 유틸리티
애플리케이션 로깅을 관리하는 모듈
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """로거 설정"""
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 이미 핸들러가 설정되어 있으면 중복 방지
    if logger.handlers:
        return logger
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 로테이팅 파일 핸들러
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def suppress_log_messages(substrings: list[str], logger_names: Optional[list[str]] = None) -> None:
    """특정 문자열을 포함하는 로그를 필터링하여 숨긴다.
    substrings: 숨길 메시지의 부분 문자열 리스트.
    logger_names: 필터를 적용할 로거 이름 리스트. None이면 root 로거에 적용.
    """
    class _SuppressBySubstring(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            try:
                message = record.getMessage()
            except Exception:
                return True
            for sub in substrings:
                if sub and sub in message:
                    return False
            return True

    target_loggers: list[logging.Logger]
    if logger_names:
        target_loggers = [logging.getLogger(name) for name in logger_names]
    else:
        target_loggers = [logging.getLogger()]  # root

    for lg in target_loggers:
        # 중복 추가 방지: 동일 클래스 필터가 이미 있으면 스킵
        if any(isinstance(f, _SuppressBySubstring) for f in lg.filters):
            continue
        lg.addFilter(_SuppressBySubstring())

def setup_qa_radar_logger(config: dict) -> logging.Logger:
    """QA Radar 전용 로거 설정"""
    
    level = config.get("level", "INFO")
    log_file = config.get("file", "logs/qa_radar.log")
    max_size = config.get("max_size", 10*1024*1024)  # 10MB
    backup_count = config.get("backup_count", 5)
    
    # 로거 생성
    logger = logging.getLogger("qa_radar")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 이미 핸들러가 설정되어 있으면 중복 방지
    if logger.handlers:
        return logger
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 로테이팅 파일 핸들러
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class QARadarLogger:
    """QA Radar 로깅 클래스"""
    
    def __init__(self, name: str, config: dict = None):
        self.name = name
        self.config = config or {}
        self.logger = setup_logger(name, self.config.get("level", "INFO"))
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """오류 로그"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self.logger.debug(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """치명적 오류 로그"""
        self.logger.critical(message, **kwargs)
    
    def test_start(self, test_id: str, url: str):
        """테스트 시작 로그"""
        self.info(f"테스트 시작 - ID: {test_id}, URL: {url}")
    
    def test_complete(self, test_id: str, status: str, execution_time: float, quality_score: float):
        """테스트 완료 로그"""
        self.info(f"테스트 완료 - ID: {test_id}, 상태: {status}, 실행시간: {execution_time:.2f}초, 품질점수: {quality_score:.1f}")
    
    def test_error(self, test_id: str, error: str):
        """테스트 오류 로그"""
        self.error(f"테스트 오류 - ID: {test_id}, 오류: {error}")
    
    def auto_healing(self, action: str, success: bool, details: str = ""):
        """Auto Healing 로그"""
        status = "성공" if success else "실패"
        self.info(f"Auto Healing {status} - 액션: {action}, 상세: {details}")
    
    def quality_assessment(self, category: str, score: float, details: str = ""):
        """품질 평가 로그"""
        self.info(f"품질 평가 - 카테고리: {category}, 점수: {score:.1f}, 상세: {details}")
    
    def mcp_operation(self, operation: str, success: bool, details: str = ""):
        """MCP 작업 로그"""
        status = "성공" if success else "실패"
        self.info(f"MCP 작업 {status} - 작업: {operation}, 상세: {details}")
    
    def operational_event(self, event: str, details: str = ""):
        """운영 이벤트 로그"""
        self.info(f"운영 이벤트 - 이벤트: {event}, 상세: {details}")

def create_test_logger(test_id: str) -> QARadarLogger:
    """테스트별 로거 생성"""
    return QARadarLogger(f"test.{test_id}")

def create_operation_logger(operation: str) -> QARadarLogger:
    """운영별 로거 생성"""
    return QARadarLogger(f"operation.{operation}")

def log_performance_metrics(logger: logging.Logger, metrics: dict):
    """성능 메트릭 로깅"""
    logger.info("성능 메트릭 수집 완료:")
    for metric, value in metrics.items():
        logger.info(f"  {metric}: {value}")

def log_quality_scores(logger: logging.Logger, scores: dict):
    """품질 점수 로깅"""
    logger.info("품질 점수 평가 완료:")
    for category, score in scores.items():
        logger.info(f"  {category}: {score:.1f}/100")

def log_healing_actions(logger: logging.Logger, actions: list):
    """복구 액션 로깅"""
    if actions:
        logger.info("Auto Healing 액션 수행:")
        for action in actions:
            logger.info(f"  - {action}")
    else:
        logger.info("Auto Healing 액션 없음")

def setup_error_logging():
    """전역 오류 로깅 설정"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Ctrl+C는 정상 종료로 처리
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = logging.getLogger("qa_radar.error")
        logger.critical("처리되지 않은 예외 발생:", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception

def log_system_info(logger: logging.Logger):
    """시스템 정보 로깅"""
    import platform
    import psutil
    
    logger.info("시스템 정보:")
    logger.info(f"  OS: {platform.system()} {platform.release()}")
    logger.info(f"  Python: {platform.python_version()}")
    logger.info(f"  CPU: {psutil.cpu_count()} 코어")
    logger.info(f"  메모리: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    logger.info(f"  디스크: {psutil.disk_usage('/').total / (1024**3):.1f} GB")

def log_config_info(logger: logging.Logger, config: dict):
    """설정 정보 로깅"""
    logger.info("애플리케이션 설정:")
    for key, value in config.items():
        if isinstance(value, dict):
            logger.info(f"  {key}:")
            for sub_key, sub_value in value.items():
                logger.info(f"    {sub_key}: {sub_value}")
        else:
            logger.info(f"  {key}: {value}")

def create_log_summary(log_file: str) -> dict:
    """로그 요약 생성"""
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return {"error": "로그 파일이 존재하지 않습니다"}
        
        summary = {
            "total_lines": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "debug_count": 0,
            "recent_errors": []
        }
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                summary["total_lines"] += 1
                
                if "ERROR" in line:
                    summary["error_count"] += 1
                    if len(summary["recent_errors"]) < 10:
                        summary["recent_errors"].append(line.strip())
                elif "WARNING" in line:
                    summary["warning_count"] += 1
                elif "INFO" in line:
                    summary["info_count"] += 1
                elif "DEBUG" in line:
                    summary["debug_count"] += 1
        
        return summary
        
    except Exception as e:
        return {"error": f"로그 요약 생성 실패: {e}"} 