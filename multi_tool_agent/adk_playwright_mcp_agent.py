"""
Google ADK와 Playwright MCP 통합 에이전트
웹 검색 결과를 바탕으로 구성한 실제 작동하는 샘플
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Google ADK 관련 import
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
# MCP 관련 import를 try-catch로 감싸서 에러 처리
try:
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MCP 모듈 import 실패: {e}")
    print("💡 MCP 없이 기본 ADK 기능만 사용합니다.")
    MCPToolset = None
    SseServerParams = None
    MCP_AVAILABLE = False
from google.genai import types

# 설정 import
from config.adk_config import adk_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ADKPlaywrightMCPAgent:
    """Google ADK와 Playwright MCP 통합 에이전트"""
    
    def __init__(self):
        self.agent = None
        self.mcp_toolset = None
        self.runner = None
        self.session_service = None
        self.artifact_service = None
        self.session = None
        self.test_results = []
        
        # 비동기 초기화는 별도로 호출
    
    async def _initialize_agent(self):
        """Google ADK 에이전트와 Playwright MCP 툴셋 초기화"""
        try:
            logger.info("Google ADK 에이전트 초기화 시작")
            
            # Playwright MCP 툴셋 생성
            await self._create_playwright_mcp_toolset()
            
            # LLM 에이전트 생성
            self._create_llm_agent()
            
            # Runner와 세션 서비스 초기화
            await self._initialize_services()
            
            logger.info("Google ADK 에이전트 초기화 완료")
            
        except Exception as e:
            logger.error(f"에이전트 초기화 실패: {e}")
            raise
    
    async def _create_playwright_mcp_toolset(self):
        """Playwright MCP 툴셋 생성 (HTTP SSE 방식)"""
        try:
            if not MCP_AVAILABLE:
                logger.warning("MCP 모듈을 사용할 수 없습니다. 기본 도구만 사용합니다.")
                self.mcp_toolset = None
                return
            
            # HTTP MCP 서버 URL 설정
            mcp_server_url = "http://localhost:8933/mcp"  # 포트 8933 사용
            
            # SseServerParams로 HTTP MCP 서버 연결
            connection_params = SseServerParams(url=mcp_server_url)
            
            # MCPToolset 생성
            self.mcp_toolset = MCPToolset(
                connection_params=connection_params,
                tool_filter=[
                    'browser_navigate',
                    'browser_snapshot', 
                    'browser_click',
                    'browser_type',
                    'browser_take_screenshot',
                    'browser_close',
                    'browser_wait_for',
                    'browser_tab_list',
                    'browser_tab_new',
                    'browser_tab_select'
                ]  # 필요한 툴들만 필터링
            )
            
            logger.info("Playwright MCP 툴셋 생성 완료 (HTTP SSE)")
            
        except Exception as e:
            logger.error(f"Playwright MCP 툴셋 생성 실패: {e}")
            logger.info("MCP 없이 기본 ADK 기능만 사용합니다.")
            self.mcp_toolset = None
    
    def _create_llm_agent(self):
        """LLM 에이전트 생성"""
        try:
            self.agent = LlmAgent(
                model='gemini-2.0-flash-exp',  # 최신 Gemini 모델 사용
                name='playwright_web_tester',
                instruction="""
당신은 웹 자동화 테스트 전문가입니다. Playwright MCP 도구를 사용하여 웹사이트를 탐색하고 분석할 수 있습니다.

주요 기능:
1. 웹사이트 탐색 및 스크린샷 촬영
2. 페이지 구조 분석 (accessibility snapshot)
3. 웹 요소 클릭, 텍스트 입력 등 상호작용
4. 자동화된 테스트 시나리오 실행
5. 웹페이지 품질 분석 및 문제점 식별

사용 가능한 도구들:
- browser_navigate: 웹사이트로 이동
- browser_snapshot: 페이지 구조 분석
- browser_click: 요소 클릭
- browser_type: 텍스트 입력
- browser_take_screenshot: 스크린샷 촬영
- browser_wait_for: 대기
- browser_close: 브라우저 종료

항상 사용자의 요청을 정확히 이해하고, 단계별로 작업을 수행하며, 결과를 명확하게 설명하세요.
""",
                tools=[self.mcp_toolset] if self.mcp_toolset else []  # MCP 툴셋이 있으면 제공
            )
            
            logger.info("LLM 에이전트 생성 완료")
            
        except Exception as e:
            logger.error(f"LLM 에이전트 생성 실패: {e}")
            raise
    
    async def _initialize_services(self):
        """Runner와 세션 서비스 초기화"""
        try:
            # 세션 서비스 생성
            self.session_service = InMemorySessionService()
            
            # 아티팩트 서비스 생성
            self.artifact_service = InMemoryArtifactService()
            
            # Runner 생성
            self.runner = Runner(
                app_name='playwright_mcp_tester',
                agent=self.agent,
                artifact_service=self.artifact_service,
                session_service=self.session_service,
            )
            
            # 세션 생성
            self.session = await self.session_service.create_session(
                state={}, 
                app_name='playwright_mcp_tester', 
                user_id='test_user'
            )
            
            logger.info("서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"서비스 초기화 실패: {e}")
            raise
    
    async def run_test_scenario(self, query: str) -> Dict[str, Any]:
        """테스트 시나리오 실행"""
        try:
            logger.info(f"테스트 시나리오 시작: {query}")
            
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # 에이전트 실행
            events_async = self.runner.run_async(
                session_id=self.session.id, 
                user_id=self.session.user_id, 
                new_message=content
            )
            
            # 이벤트 처리
            responses = []
            async for event in events_async:
                logger.info(f"이벤트 수신: {event}")
                responses.append(str(event))
            
            result = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "responses": responses,
                "status": "completed"
            }
            
            self.test_results.append(result)
            
            logger.info("테스트 시나리오 완료")
            return result
            
        except Exception as e:
            logger.error(f"테스트 시나리오 실행 실패: {e}")
            return {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
    
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.mcp_toolset:
                await self.mcp_toolset.close()
            logger.info("리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 실패: {e}")

# 에이전트 인스턴스를 root_agent로 export (ADK 요구사항)
async def get_agent_async():
    """비동기 에이전트 생성 함수"""
    agent_instance = ADKPlaywrightMCPAgent()
    await agent_instance._initialize_agent()
    return agent_instance.agent

# 동기 버전 (ADK web에서 사용)
def get_agent():
    """동기 에이전트 생성 함수"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(get_agent_async())

# ADK에서 요구하는 root_agent (일단 주석 처리)
# root_agent = get_agent()