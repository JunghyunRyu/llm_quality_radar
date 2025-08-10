"""
Google ADK 설정 모듈
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class ADKConfig:
    """Google ADK 설정 클래스"""

    def __init__(self):
        # Google Cloud 설정
        self.google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT", "demo-project")
        self.google_cloud_region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        # Google AI API 설정 - 데모용으로 일단 비활성화
        self.use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1"
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "demo-key")
        self.google_application_credentials = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", ""
        )

        # Playwright MCP 설정
        self.playwright_mcp_command = os.getenv("PLAYWRIGHT_MCP_COMMAND", "npx")
        self.playwright_mcp_args = os.getenv(
            "PLAYWRIGHT_MCP_ARGS", "@playwright/mcp@latest"
        ).split(",")
        self.playwright_mcp_headless = (
            os.getenv("PLAYWRIGHT_MCP_HEADLESS", "true").lower() == "true"
        )
        self.playwright_mcp_browser = os.getenv("PLAYWRIGHT_MCP_BROWSER", "chrome")

        # ADK 서버 설정
        self.adk_web_port = int(os.getenv("ADK_WEB_PORT", "8000"))
        self.adk_api_port = int(os.getenv("ADK_API_PORT", "8001"))

        # 로깅 설정
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "structured")

        # 환경 설정 적용
        self._apply_environment_config()

    def _apply_environment_config(self):
        """환경 설정을 시스템 환경변수에 적용"""

        # Google AI API 설정
        if self.use_vertex_ai:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
            if self.google_cloud_project:
                os.environ["GOOGLE_CLOUD_PROJECT"] = self.google_cloud_project
            if self.google_cloud_region:
                os.environ["GOOGLE_CLOUD_LOCATION"] = self.google_cloud_region
            if self.google_application_credentials:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                    self.google_application_credentials
                )
        else:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
            if self.google_api_key:
                os.environ["GOOGLE_API_KEY"] = self.google_api_key

    def get_playwright_mcp_config(self) -> Dict[str, Any]:
        """Playwright MCP 설정 반환"""
        return {
            "command": self.playwright_mcp_command,
            "args": self.playwright_mcp_args
            + [
                "--headless" if self.playwright_mcp_headless else "",
                f"--browser={self.playwright_mcp_browser}",
            ],
            "headless": self.playwright_mcp_headless,
            "browser": self.playwright_mcp_browser,
        }

    def validate_config(self) -> Dict[str, bool]:
        """설정 유효성 검사"""
        validation_results = {}

        # Google Cloud 프로젝트 설정 확인
        validation_results["google_cloud_project"] = bool(self.google_cloud_project)

        # API 키 설정 확인
        if self.use_vertex_ai:
            validation_results["vertex_ai_credentials"] = bool(
                self.google_application_credentials
                and os.path.exists(self.google_application_credentials)
            )
        else:
            validation_results["google_api_key"] = bool(self.google_api_key)

        return validation_results


# 전역 설정 인스턴스
adk_config = ADKConfig()
