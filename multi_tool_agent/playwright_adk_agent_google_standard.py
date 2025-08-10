"""
Google ADK 표준 방식 Playwright MCP 에이전트
LLM 에이전트가 자연어로 웹 브라우저를 제어하는 방식
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)
from google.genai import types
from utils.logger import setup_logger, suppress_log_messages

# 환경 변수 기반 로거 설정 (LOG_LEVEL, LOG_FILE 지원)
logger = setup_logger(
    __name__, level=os.getenv("LOG_LEVEL", "INFO"), log_file=os.getenv("LOG_FILE")
)

# 노이즈 억제: ADK 인증 경고 문자열 전역 필터링
suppress_log_messages(
    substrings=[
        "auth_config or auth_config.auth_scheme is missing",
        "Will skip authentication.Using FunctionTool instead",
    ],
    logger_names=["", "google_adk"],
)


class PlaywrightADKAgentGoogleStandard:
    """Google ADK 표준 방식 Playwright MCP 에이전트"""

    def __init__(self):
        self.agent = None
        self.mcp_toolset = None
        self.runner = None
        self.session_service = None
        self.artifact_service = None
        self.session = None

        # 에이전트 초기화
        self._initialize_agent()

    def _initialize_agent(self):
        """Google ADK 표준 방식 에이전트 초기화"""
        # ADK 내부 인증 경고 노이즈 억제 (auth_scheme 미설정 경고 메시지 필터)
        adk_logger = logging.getLogger("google_adk")

        class _SuppressAuthWarnings(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                msg = record.getMessage()
                return "auth_config or auth_config.auth_scheme is missing" not in msg

        adk_logger.addFilter(_SuppressAuthWarnings())

        # 환경 변수 기반 Playwright MCP 실행 옵션 (Windows 비대화형 실행 대응)
        npx_command = os.getenv("PLAYWRIGHT_MCP_COMMAND", "npx")
        # 공백으로 분리된 인자 문자열 혹은 단일 패키지명 지원
        raw_args = os.getenv("PLAYWRIGHT_MCP_ARGS", "@playwright/mcp").strip()
        base_args = raw_args.split() if raw_args else ["@playwright/mcp"]

        headless = os.getenv("PLAYWRIGHT_MCP_HEADLESS", "true").lower() == "true"
        browser_channel = os.getenv("PLAYWRIGHT_MCP_BROWSER", "chrome")

        stdio_args = ["-y", *base_args]
        if headless:
            stdio_args.append("--headless")
        if browser_channel:
            stdio_args.append(f"--browser={browser_channel}")

        logger.info(
            "Playwright MCP 설정: command=%s, args=%s, headless=%s, browser=%s",
            npx_command,
            " ".join(stdio_args),
            headless,
            browser_channel,
        )

        # Playwright MCP 서버 설정 (필요한 도구만 필터링)
        self.mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=npx_command,
                    args=stdio_args,
                    env={"NODE_ENV": "production", "TIMEOUT": "30000"},  # 30초 타임아웃
                )
            ),
            tool_filter=[
                "browser_navigate",
                "browser_snapshot",
                "browser_click",
                "browser_type",
                "browser_wait_for",
                "browser_take_screenshot",
                "browser_close",
            ],
        )
        logger.debug(
            "MCP tool_filter=%s",
            [
                "browser_navigate",
                "browser_snapshot",
                "browser_click",
                "browser_type",
                "browser_wait_for",
                "browser_take_screenshot",
                "browser_close",
            ],
        )

        # Google ADK LlmAgent 초기화
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="playwright_qa_agent_google_standard",
            instruction=(
                "당신은 웹 자동화 테스트 전문가입니다. Playwright MCP를 통해 "
                "웹 브라우저를 제어하고, 웹사이트를 테스트하며, 품질 분석을 수행합니다. "
                "사용자의 자연어 요청에 따라 웹 브라우저를 조작하고, "
                "웹사이트의 기능을 테스트하며, 문제점을 분석하고 개선 방안을 제시합니다. "
                "항상 단계별로 작업을 수행하고, 각 단계의 결과를 명확히 보고하세요."
            ),
            tools=[self.mcp_toolset],
        )

        # 서비스 초기화
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()

        # Runner 초기화 (타임아웃 30초 설정)
        self.runner = Runner(
            app_name="playwright_qa_app",
            agent=self.agent,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
        )
        logger.info(
            "ADK Runner 초기화 완료: app_name=playwright_qa_app, model=%s",
            "gemini-2.0-flash",
        )

    async def create_session(self, user_id: str = "test_user"):
        """세션 생성"""
        self.session = await self.session_service.create_session(
            state={}, app_name="playwright_qa_app", user_id=user_id
        )
        logger.info(
            "세션 생성 완료: id=%s, user_id=%s",
            getattr(self.session, "id", None),
            user_id,
        )
        return self.session

    async def run_web_test_natural_language(self, test_request: str) -> Dict[str, Any]:
        """자연어로 웹 테스트 실행 (Google ADK 표준 방식)

        Args:
            test_request (str): 자연어 테스트 요청 (예: "Google.com에 접속해서 검색창을 찾고 'test'를 입력해주세요")

        Returns:
            Dict: 테스트 실행 결과
        """
        try:
            logger.info("자연어 웹 테스트 시작")
            logger.debug("요청 내용=%s", test_request)
            start_time = datetime.now()

            # 세션 생성
            if not self.session:
                await self.create_session()

            # 사용자 메시지 생성
            content = types.Content(role="user", parts=[types.Part(text=test_request)])
            logger.debug(
                "ADK Content 생성 완료: role=user, parts_len=%d",
                len(getattr(content, "parts", []) or []),
            )

            # 에이전트 실행
            events_async = self.runner.run_async(
                session_id=self.session.id,
                user_id=self.session.user_id,
                new_message=content,
            )

            # 결과 수집
            responses = []
            async for event in events_async:
                responses.append(event)
                evt_type = type(event).__name__
                size_hint = len(str(event)) if event is not None else 0
                logger.debug("이벤트 수신: type=%s size~=%d", evt_type, size_hint)

            # 실행 시간 계산
            execution_time = (datetime.now() - start_time).total_seconds()

            # 결과 정리
            result = {
                "test_id": f"nl_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "request": test_request,
                "status": "completed",
                "execution_time": execution_time,
                "events_count": len(responses),
                "events": responses,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                "자연어 웹 테스트 완료: %.2f초, 이벤트=%d",
                execution_time,
                len(responses),
            )
            return result

        except Exception as e:
            logger.exception("자연어 웹 테스트 실패")
            return {
                "test_id": f"nl_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "request": test_request,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def analyze_webpage_quality_natural_language(
        self, url: str
    ) -> Dict[str, Any]:
        """자연어로 웹페이지 품질 분석 (Google ADK 표준 방식)"""
        try:
            logger.info(f"자연어 품질 분석 시작: {url}")

            # 품질 분석 요청 생성
            quality_request = f"""
            {url}에 접속해서 다음 품질 분석을 수행해주세요:
            
            1. 페이지 로딩 상태 확인
            2. 주요 UI 요소들의 존재 여부 확인
            3. JavaScript 오류 확인
            4. 이미지 로딩 상태 확인
            5. 링크 상태 확인
            6. 전체적인 사용자 경험 평가
            
            각 항목별로 상세한 분석 결과를 제공해주세요.
            """

            return await self.run_web_test_natural_language(quality_request)

        except Exception as e:
            logger.exception("자연어 품질 분석 실패")
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def perform_accessibility_test(self, url: str) -> Dict[str, Any]:
        """접근성 테스트 수행 (Google ADK 표준 방식)"""
        try:
            logger.info(f"접근성 테스트 시작: {url}")

            accessibility_request = f"""
            {url}에 접속해서 다음 접근성 테스트를 수행해주세요:
            
            1. 키보드 네비게이션 가능성 확인
            2. 스크린 리더 호환성 확인
            3. 색상 대비 확인
            4. 이미지 alt 텍스트 확인
            5. 폼 라벨 연결 확인
            6. ARIA 속성 사용 확인
            
            접근성 문제점들을 식별하고 개선 방안을 제시해주세요.
            """

            return await self.run_web_test_natural_language(accessibility_request)

        except Exception as e:
            logger.exception("접근성 테스트 실패")
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def test_responsive_design(self, url: str) -> Dict[str, Any]:
        """반응형 디자인 테스트 (Google ADK 표준 방식)"""
        try:
            logger.info(f"반응형 디자인 테스트 시작: {url}")

            responsive_request = f"""
            {url}에 접속해서 다음 반응형 디자인 테스트를 수행해주세요:
            
            1. 데스크톱 뷰포트에서 레이아웃 확인
            2. 태블릿 뷰포트로 변경하여 레이아웃 확인
            3. 모바일 뷰포트로 변경하여 레이아웃 확인
            4. 각 뷰포트에서 UI 요소들의 적절한 배치 확인
            5. 터치 타겟 크기 확인
            6. 텍스트 가독성 확인
            
            반응형 디자인 문제점들을 식별하고 개선 방안을 제시해주세요.
            """

            return await self.run_web_test_natural_language(responsive_request)

        except Exception as e:
            logger.exception("반응형 디자인 테스트 실패")
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def run_comprehensive_test(self, url: str) -> Dict[str, Any]:
        """종합 테스트 실행 (Google ADK 표준 방식)"""
        try:
            logger.info(f"종합 테스트 시작: {url}")

            comprehensive_request = f"""
            {url}에 접속해서 다음 종합 테스트를 수행해주세요:
            
            **기능 테스트:**
            1. 주요 기능들이 정상 작동하는지 확인
            2. 폼 제출 및 데이터 처리 확인
            3. 네비게이션 및 링크 작동 확인
            
            **성능 테스트:**
            1. 페이지 로딩 속도 확인
            2. 이미지 및 리소스 로딩 확인
            3. JavaScript 실행 성능 확인
            
            **사용성 테스트:**
            1. 직관적인 UI/UX 확인
            2. 사용자 플로우의 자연스러움 확인
            3. 오류 처리 및 피드백 확인
            
            **기술적 품질:**
            1. 코드 품질 및 최적화 확인
            2. 보안 취약점 확인
            3. SEO 최적화 확인
            
            각 영역별로 상세한 분석과 개선 권장사항을 제공해주세요.
            """

            return await self.run_web_test_natural_language(comprehensive_request)

        except Exception as e:
            logger.exception("종합 테스트 실패")
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def close(self):
        """리소스 정리"""
        try:
            if self.mcp_toolset:
                await self.mcp_toolset.close()
            logger.info("Playwright ADK Agent (Google 표준) 리소스 정리 완료")
        except Exception as e:
            logger.exception("리소스 정리 중 오류")


# 사용 예시
async def main():
    """메인 실행 함수"""
    agent = PlaywrightADKAgentGoogleStandard()

    try:
        # 1. 기본 웹 테스트
        print("=== 기본 웹 테스트 ===")
        result = await agent.run_web_test_natural_language(
            "Google.com에 접속해서 검색창을 찾고 'Python programming'을 입력해주세요"
        )
        print(f"테스트 결과: {result['status']}")

        # 2. 품질 분석
        print("\n=== 품질 분석 ===")
        quality_result = await agent.analyze_webpage_quality_natural_language(
            "https://www.google.com"
        )
        print(f"품질 분석 결과: {quality_result['status']}")

        # 3. 접근성 테스트
        print("\n=== 접근성 테스트 ===")
        accessibility_result = await agent.perform_accessibility_test(
            "https://www.google.com"
        )
        print(f"접근성 테스트 결과: {accessibility_result['status']}")

        # 4. 반응형 디자인 테스트
        print("\n=== 반응형 디자인 테스트 ===")
        responsive_result = await agent.test_responsive_design("https://www.google.com")
        print(f"반응형 디자인 테스트 결과: {responsive_result['status']}")

        # 5. 종합 테스트
        print("\n=== 종합 테스트 ===")
        comprehensive_result = await agent.run_comprehensive_test(
            "https://www.google.com"
        )
        print(f"종합 테스트 결과: {comprehensive_result['status']}")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
