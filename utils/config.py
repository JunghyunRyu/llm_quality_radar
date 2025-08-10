"""
설정 관리 유틸리티
애플리케이션 설정을 관리하는 모듈
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """설정 관리 클래스"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self._load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """기본 설정 로드"""
        return {
            "app": {
                "name": "QA Quality Radar",
                "version": "1.0.0",
                "debug": False,
                "host": "0.0.0.0",
                "port": 8000,
            },
            "mcp": {
                "server_path": "npx",
                "server_args": ["@modelcontextprotocol/server-playwright"],
                "timeout": 30000,
                "headless": True,
                "viewport": {"width": 1920, "height": 1080},
            },
            "auto_healing": {
                "enabled": True,
                "max_retry_attempts": 3,
                "retry_delay": 2.0,
                "strategies": {
                    "element_not_found": [
                        "wait_for_element",
                        "try_alternative_selectors",
                        "refresh_page",
                        "scroll_to_element",
                    ],
                    "element_not_clickable": [
                        "wait_for_clickable",
                        "scroll_to_element",
                        "try_javascript_click",
                        "wait_for_page_load",
                    ],
                    "timeout_error": [
                        "increase_timeout",
                        "retry_with_delay",
                        "check_network_status",
                        "refresh_page",
                    ],
                },
            },
            "quality_monitor": {
                "enabled": True,
                "thresholds": {
                    "performance": {
                        "page_load_time": 3.0,
                        "first_contentful_paint": 1.8,
                        "largest_contentful_paint": 2.5,
                        "cumulative_layout_shift": 0.1,
                    },
                    "accessibility": {
                        "wcag_aa_compliance": 0.95,
                        "keyboard_navigation": 1.0,
                        "screen_reader_compatibility": 1.0,
                    },
                    "seo": {
                        "meta_tags": 0.8,
                        "heading_structure": 0.9,
                        "image_alt_texts": 0.9,
                        "internal_links": 0.7,
                    },
                    "functionality": {
                        "broken_links": 0.0,
                        "javascript_errors": 0.0,
                        "form_validation": 1.0,
                    },
                },
                "weights": {
                    "performance": 0.3,
                    "accessibility": 0.25,
                    "seo": 0.2,
                    "functionality": 0.25,
                },
            },
            "operational": {
                "auto_cleanup_days": 30,
                "max_concurrent_tests": 5,
                "notification_enabled": True,
                "dashboard_refresh_interval": 60,
                "backup_enabled": True,
                "backup_interval_hours": 24,
                "database": {"path": "data/qa_radar.db", "backup_path": "backups/"},
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/qa_radar.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5,
            },
            "security": {
                "cors_origins": ["*"],
                "rate_limit": {"enabled": True, "requests_per_minute": 100},
            },
        }

    def _load_config(self):
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    self._merge_config(self.config, file_config)
                    logger.info(f"설정 파일 로드 완료: {self.config_file}")
            else:
                self._save_config()
                logger.info(f"기본 설정 파일 생성: {self.config_file}")

        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")

    def _merge_config(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ):
        """설정 병합"""
        for key, value in override_config.items():
            if (
                key in base_config
                and isinstance(base_config[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value

    def _save_config(self):
        """설정 파일 저장"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"설정 파일 저장 완료: {self.config_file}")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        try:
            keys = key.split(".")
            value = self.config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value
        except Exception as e:
            logger.error(f"설정 값 조회 실패 ({key}): {e}")
            return default

    def set(self, key: str, value: Any):
        """설정 값 설정"""
        try:
            keys = key.split(".")
            config = self.config

            # 마지막 키까지 탐색
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # 값 설정
            config[keys[-1]] = value

            # 설정 파일 저장
            self._save_config()

            logger.info(f"설정 값 설정 완료: {key} = {value}")

        except Exception as e:
            logger.error(f"설정 값 설정 실패 ({key}): {e}")

    def get_mcp_config(self) -> Dict[str, Any]:
        """MCP 설정 조회"""
        return self.get("mcp", {})

    def get_auto_healing_config(self) -> Dict[str, Any]:
        """Auto Healing 설정 조회"""
        return self.get("auto_healing", {})

    def get_quality_monitor_config(self) -> Dict[str, Any]:
        """품질 모니터 설정 조회"""
        return self.get("quality_monitor", {})

    def get_operational_config(self) -> Dict[str, Any]:
        """운영 설정 조회"""
        return self.get("operational", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 조회"""
        return self.get("logging", {})

    def get_security_config(self) -> Dict[str, Any]:
        """보안 설정 조회"""
        return self.get("security", {})

    def update_config(self, updates: Dict[str, Any]):
        """설정 업데이트"""
        try:
            self._merge_config(self.config, updates)
            self._save_config()
            logger.info("설정 업데이트 완료")
        except Exception as e:
            logger.error(f"설정 업데이트 실패: {e}")

    def reload_config(self):
        """설정 재로드"""
        try:
            self.config = self._load_default_config()
            self._load_config()
            logger.info("설정 재로드 완료")
        except Exception as e:
            logger.error(f"설정 재로드 실패: {e}")

    def export_config(self, export_path: str):
        """설정 내보내기"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)

            logger.info(f"설정 내보내기 완료: {export_file}")

        except Exception as e:
            logger.error(f"설정 내보내기 실패: {e}")

    def import_config(self, import_path: str):
        """설정 가져오기"""
        try:
            import_file = Path(import_path)

            if not import_file.exists():
                raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {import_path}")

            with open(import_file, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            self._merge_config(self.config, imported_config)
            self._save_config()

            logger.info(f"설정 가져오기 완료: {import_file}")

        except Exception as e:
            logger.error(f"설정 가져오기 실패: {e}")

    def validate_config(self) -> Dict[str, Any]:
        """설정 유효성 검사"""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        try:
            # 필수 설정 검사
            required_configs = [
                "app.name",
                "app.version",
                "mcp.server_path",
                "operational.database.path",
            ]

            for config_key in required_configs:
                if not self.get(config_key):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"필수 설정 누락: {config_key}")

            # 설정 값 범위 검사
            port = self.get("app.port")
            if port and (port < 1 or port > 65535):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    "포트 번호가 유효하지 않습니다 (1-65535)"
                )

            timeout = self.get("mcp.timeout")
            if timeout and timeout < 1000:
                validation_result["warnings"].append("MCP 타임아웃이 너무 짧습니다")

            # 데이터베이스 경로 검사
            db_path = self.get("operational.database.path")
            if db_path:
                db_dir = Path(db_path).parent
                if not db_dir.exists():
                    validation_result["warnings"].append(
                        f"데이터베이스 디렉토리가 존재하지 않습니다: {db_dir}"
                    )

            logger.info(f"설정 유효성 검사 완료: {validation_result['valid']}")

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"설정 유효성 검사 중 오류: {e}")
            logger.error(f"설정 유효성 검사 실패: {e}")

        return validation_result

    def get_environment_config(self) -> Dict[str, Any]:
        """환경별 설정 조회"""
        env = os.getenv("QA_RADAR_ENV", "development")

        env_configs = {
            "development": {
                "app.debug": True,
                "logging.level": "DEBUG",
                "mcp.headless": False,
            },
            "production": {
                "app.debug": False,
                "logging.level": "WARNING",
                "mcp.headless": True,
                "security.rate_limit.enabled": True,
            },
            "testing": {
                "app.debug": True,
                "logging.level": "INFO",
                "mcp.headless": True,
                "operational.auto_cleanup_days": 1,
            },
        }

        return env_configs.get(env, {})

    def apply_environment_config(self):
        """환경별 설정 적용"""
        try:
            env_config = self.get_environment_config()
            self._merge_config(self.config, env_config)
            logger.info("환경별 설정 적용 완료")
        except Exception as e:
            logger.error(f"환경별 설정 적용 실패: {e}")
