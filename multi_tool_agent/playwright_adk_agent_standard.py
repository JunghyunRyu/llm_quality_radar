"""
Google ADK 표준 MCPToolset을 사용한 Playwright MCP 연계 에이전트
웹 자동화 테스트와 AI 기반 품질 분석을 결합한 혁신적인 시스템
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PlaywrightADKAgentStandard:
    """Google ADK 표준 MCPToolset을 사용한 Playwright MCP 연계 에이전트"""

    def __init__(self):
        self.agent = None
        self.mcp_toolset = None
        self.test_results = []

        # 에이전트 초기화
        self._initialize_agent()

    def _initialize_agent(self):
        """Google ADK 에이전트 초기화 (표준 MCPToolset 사용)"""
        # Playwright MCP 서버 설정
        self.mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx", args=["@playwright/mcp", "--headless"]
                )
            ),
            tool_filter=[
                "browser_install",
                "browser_tab_new",
                "browser_navigate",
                "browser_snapshot",
                "click",
                "type",
                "wait_for_element",
                "element_exists",
                "element_is_clickable",
                "scroll_to_element",
                "execute_javascript",
                "refresh_page",
                "wait_for_page_load",
                "capture_screenshots",
                "get_logs",
                "get_network_status",
                "assert_element",
            ],
        )

        # Google ADK LlmAgent 초기화
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="playwright_qa_agent_standard",
            instruction=(
                "당신은 웹 자동화 테스트 전문가입니다. Playwright MCP를 통해 "
                "웹 브라우저를 제어하고, Google ADK의 AI 기능을 활용하여 "
                "고급 품질 분석을 수행합니다. 사용자의 요청에 따라 웹사이트를 "
                "테스트하고, 문제점을 분석하며, 개선 방안을 제시합니다."
            ),
            tools=[self.mcp_toolset],
        )

    async def run_web_test(
        self, url: str, test_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """웹 테스트 실행 (표준 MCPToolset 사용)

        Args:
            url (str): 테스트할 웹사이트 URL
            test_scenarios (List[Dict]): 실행할 테스트 시나리오 목록

        Returns:
            Dict: 테스트 실행 결과
        """
        try:
            logger.info(f"웹 테스트 시작 (표준 방식): {url}")
            start_time = datetime.now()

            # MCPToolset에서 도구 목록 가져오기
            tools = await self.mcp_toolset.get_tools()
            logger.info(f"사용 가능한 도구 수: {len(tools)}")

            # 도구 이름으로 매핑
            tool_map = {tool.name: tool for tool in tools}

            # 브라우저 설치 확인
            if "browser_install" in tool_map:
                await tool_map["browser_install"].run({})
                logger.info("브라우저 설치 확인 완료")

            # 새 탭 생성
            tab_id = None
            if "browser_tab_new" in tool_map:
                tab_result = await tool_map["browser_tab_new"].run({})
                tab_id = tab_result.get("tab_id")
                logger.info(f"새 탭 생성 완료: {tab_id}")

            # 페이지 네비게이션
            if "browser_navigate" in tool_map:
                await tool_map["browser_navigate"].run({"url": url})
                logger.info(f"페이지 네비게이션 완료: {url}")

            # 페이지 로드 대기
            if "wait_for_page_load" in tool_map:
                await tool_map["wait_for_page_load"].run({})
                logger.info("페이지 로드 대기 완료")

            # 테스트 시나리오 실행
            test_results = []
            for i, scenario in enumerate(test_scenarios):
                scenario_description = scenario.get("description", "Unknown")
                logger.info(f"시나리오 {i+1} 실행: {scenario_description}")

                result = await self._execute_test_scenario_standard(scenario, tool_map)
                test_results.append(result)

            # 스크린샷 캡처
            screenshots_result = {}
            if "capture_screenshots" in tool_map:
                screenshots_result = await tool_map["capture_screenshots"].run({})
                logger.info("스크린샷 캡처 완료")

            # 로그 수집
            logs_result = {}
            if "get_logs" in tool_map:
                logs_result = await tool_map["get_logs"].run({})
                logger.info("로그 수집 완료")

            # 결과 정리
            success_count = sum(1 for r in test_results if r.get("success", False))
            total_count = len(test_results)
            execution_time = (datetime.now() - start_time).total_seconds()

            test_result = {
                "test_id": f"web_test_standard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "status": "completed",
                "execution_time": execution_time,
                "success_rate": success_count / total_count if total_count > 0 else 0,
                "total_scenarios": total_count,
                "successful_scenarios": success_count,
                "failed_scenarios": total_count - success_count,
                "test_results": test_results,
                "screenshots": screenshots_result.get("screenshots", []),
                "logs": logs_result.get("logs", []),
                "timestamp": datetime.now().isoformat(),
            }

            self.test_results.append(test_result)
            logger.info(f"웹 테스트 완료 (표준 방식): {execution_time:.2f}초")

            return test_result

        except Exception as e:
            logger.error(f"웹 테스트 실패 (표준 방식): {e}")
            return {
                "test_id": f"web_test_standard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _execute_test_scenario_standard(
        self, scenario: Dict[str, Any], tool_map: Dict
    ) -> Dict[str, Any]:
        """테스트 시나리오 실행 (표준 MCPToolset 사용)"""
        try:
            action = scenario.get("action")
            selector = scenario.get("selector")
            description = scenario.get("description", "Unknown")

            logger.info(f"시나리오 실행: {action} - {selector}")

            if action == "wait":
                # 요소 대기
                if "wait_for_element" in tool_map:
                    await tool_map["wait_for_element"].run(
                        {"selector": selector, "timeout": scenario.get("timeout", 10)}
                    )
                return {"success": True, "action": action, "description": description}

            elif action == "click":
                # 요소 클릭
                if "click" in tool_map:
                    await tool_map["click"].run({"selector": selector})
                return {"success": True, "action": action, "description": description}

            elif action == "type":
                # 텍스트 입력
                text = scenario.get("text", "")
                if "type" in tool_map:
                    await tool_map["type"].run({"selector": selector, "text": text})
                return {"success": True, "action": action, "description": description}

            elif action == "assert":
                # 요소 검증
                expected_value = scenario.get("value", "")
                if "assert_element" in tool_map:
                    result = await tool_map["assert_element"].run(
                        {"selector": selector, "expected_value": expected_value}
                    )
                    return {
                        "success": result.get("success", False),
                        "action": action,
                        "description": description,
                        "actual_value": result.get("actual_value"),
                    }
                else:
                    return {
                        "success": False,
                        "action": action,
                        "description": description,
                        "error": "assert_element tool not available",
                    }

            else:
                logger.warning(f"지원하지 않는 액션: {action}")
                return {
                    "success": False,
                    "action": action,
                    "description": description,
                    "error": "Unsupported action",
                }

        except Exception as e:
            logger.error(f"시나리오 실행 실패: {e}")
            return {
                "success": False,
                "action": scenario.get("action"),
                "description": scenario.get("description"),
                "error": str(e),
            }

    async def analyze_webpage_quality(self, url: str) -> Dict[str, Any]:
        """웹페이지 품질 분석 (표준 MCPToolset 사용)"""
        try:
            logger.info(f"웹페이지 품질 분석 시작: {url}")

            # MCPToolset에서 도구 목록 가져오기
            tools = await self.mcp_toolset.get_tools()
            tool_map = {tool.name: tool for tool in tools}

            # 페이지 네비게이션
            if "browser_navigate" in tool_map:
                await tool_map["browser_navigate"].run({"url": url})

            if "wait_for_page_load" in tool_map:
                await tool_map["wait_for_page_load"].run({})

            # 페이지 스냅샷으로 현재 상태 확인
            snapshot = {}
            if "browser_snapshot" in tool_map:
                snapshot = await tool_map["browser_snapshot"].run({})

            # 네트워크 상태 확인
            network_status = {}
            if "get_network_status" in tool_map:
                network_status = await tool_map["get_network_status"].run({})

            # 로그 확인
            logs = []
            if "get_logs" in tool_map:
                logs_result = await tool_map["get_logs"].run({})
                logs = logs_result.get("logs", [])

            # 품질 점수 계산
            quality_score = self._calculate_quality_score_standard(
                {"snapshot": snapshot, "network_status": network_status, "logs": logs}
            )

            return {
                "url": url,
                "quality_score": quality_score,
                "snapshot": snapshot,
                "network_status": network_status,
                "logs": logs,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"웹페이지 품질 분석 실패: {e}")
            return {
                "url": url,
                "quality_score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _calculate_quality_score_standard(self, metrics: Dict[str, Any]) -> float:
        """품질 점수 계산 (표준 방식)"""
        score = 100.0

        # 로그 오류 감점
        logs = metrics.get("logs", [])
        error_count = len(
            [log for log in logs if "error" in log.get("level", "").lower()]
        )
        score -= error_count * 5

        # 네트워크 상태 감점
        network_status = metrics.get("network_status", {})
        if network_status.get("failed_requests", 0) > 0:
            score -= network_status["failed_requests"] * 2

        return max(0.0, score)

    async def close(self):
        """리소스 정리"""
        try:
            if self.mcp_toolset:
                await self.mcp_toolset.close()
            logger.info("Playwright ADK Agent (표준) 리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")


# 사용 예시
async def main():
    """메인 실행 함수"""
    agent = PlaywrightADKAgentStandard()

    # 테스트 시나리오 정의
    test_scenarios = [
        {"action": "wait", "selector": "body", "description": "페이지 로드 대기"},
        {
            "action": "click",
            "selector": "a[href*='about']",
            "description": "About 링크 클릭",
        },
        {"action": "wait", "selector": "h1", "description": "제목 요소 대기"},
    ]

    try:
        # 웹 테스트 실행
        result = await agent.run_web_test("https://www.google.com", test_scenarios)
        print(f"테스트 결과: {result}")

        # 품질 분석
        quality_result = await agent.analyze_webpage_quality("https://www.google.com")
        print(f"품질 분석 결과: {quality_result}")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
