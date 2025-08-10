#!/usr/bin/env python3
"""
HTTP 기반 Playwright MCP 서버를 사용한 데모
GitHub 공식 예제 기반 통합 테스트
"""

import asyncio
import subprocess
import time
import sys
import os
import signal
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from multi_tool_agent.adk_playwright_mcp_agent import ADKPlaywrightMCPAgent
from config.adk_config import adk_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PlaywrightMCPDemo:
    """HTTP 기반 Playwright MCP 데모"""

    def __init__(self):
        self.mcp_server_process = None
        self.agent = None

    async def start_mcp_server(self):
        """MCP 서버 시작"""
        try:
            print("🎭 Playwright MCP HTTP 서버 시작 중...")

            # Node.js 의존성 설치
            print("📦 Node.js 의존성 설치 중...")
            install_result = subprocess.run(
                ["npm", "install", "@playwright/mcp", "@modelcontextprotocol/sdk"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if install_result.returncode != 0:
                print(f"⚠️ 의존성 설치 경고: {install_result.stderr}")
            else:
                print("✅ Node.js 의존성 설치 완료")

            # MCP 서버 시작
            self.mcp_server_process = subprocess.Popen(
                ["node", "playwright_mcp_server.js"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # 서버 시작 대기
            print("⏳ MCP 서버 시작 대기 중...")
            await asyncio.sleep(5)

            # 서버 상태 확인
            if self.mcp_server_process.poll() is None:
                print("✅ MCP 서버 시작 성공")

                # Health check
                try:
                    import requests

                    response = requests.get("http://localhost:8932/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Health check 성공: {response.json()}")
                    else:
                        print(f"⚠️ Health check 응답: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ Health check 실패: {e}")

                return True
            else:
                stderr_output = self.mcp_server_process.stderr.read()
                print(f"❌ MCP 서버 시작 실패: {stderr_output}")
                return False

        except Exception as e:
            print(f"❌ MCP 서버 시작 오류: {e}")
            return False

    async def setup_adk_agent(self):
        """ADK 에이전트 설정"""
        try:
            print("🤖 Google ADK 에이전트 초기화 중...")

            # 설정 확인
            validation = adk_config.validate_config()
            print(f"📋 설정 상태: {validation}")

            if not any(validation.values()):
                print("⚠️ API 키가 설정되지 않았습니다. 데모용으로 진행합니다.")

            # 에이전트 생성
            self.agent = ADKPlaywrightMCPAgent()
            await self.agent._initialize_agent()

            print("✅ ADK 에이전트 초기화 완료")
            return True

        except Exception as e:
            print(f"❌ ADK 에이전트 초기화 실패: {e}")
            logger.error(f"에이전트 초기화 오류: {e}")
            return False

    async def run_demo_scenarios(self):
        """데모 시나리오 실행"""
        try:
            print("\n🧪 데모 시나리오 실행 시작")
            print("=" * 50)

            scenarios = [
                {
                    "name": "기본 웹 탐색",
                    "query": """
Example.com (https://www.example.com)으로 이동해서 
다음 작업을 수행해주세요:

1. 페이지로 이동
2. 페이지 스크린샷 촬영 
3. 페이지 구조 분석
4. 브라우저 종료

각 단계를 자세히 설명해주세요.
""",
                },
                {
                    "name": "다중 탭 관리",
                    "query": """
다음 작업을 수행해주세요:

1. 새 탭 열기
2. Google.com으로 이동
3. 탭 목록 확인
4. 탭 전환 테스트
5. 모든 탭 닫기

각 과정을 상세히 보고해주세요.
""",
                },
            ]

            results = []

            for i, scenario in enumerate(scenarios, 1):
                print(f"\n📋 시나리오 {i}: {scenario['name']}")
                print("-" * 30)

                try:
                    result = await self.agent.run_test_scenario(scenario["query"])
                    results.append(
                        {
                            "scenario": scenario["name"],
                            "status": result.get("status", "unknown"),
                            "result": result,
                        }
                    )

                    print(f"✅ 시나리오 {i} 완료: {result.get('status', 'unknown')}")

                except Exception as e:
                    print(f"❌ 시나리오 {i} 실패: {e}")
                    results.append(
                        {
                            "scenario": scenario["name"],
                            "status": "failed",
                            "error": str(e),
                        }
                    )

                # 시나리오 간 대기
                await asyncio.sleep(2)

            print(f"\n📊 데모 완료! 총 {len(results)}개 시나리오 실행")
            for result in results:
                status_emoji = "✅" if result["status"] == "completed" else "❌"
                print(f"  {status_emoji} {result['scenario']}: {result['status']}")

            return results

        except Exception as e:
            print(f"❌ 데모 시나리오 실행 실패: {e}")
            return []

    async def cleanup(self):
        """리소스 정리"""
        try:
            print("\n🧹 리소스 정리 중...")

            # ADK 에이전트 정리
            if self.agent:
                await self.agent.cleanup()
                print("✅ ADK 에이전트 정리 완료")

            # MCP 서버 종료
            if self.mcp_server_process and self.mcp_server_process.poll() is None:
                print("🛑 MCP 서버 종료 중...")
                self.mcp_server_process.terminate()

                # 강제 종료 대기
                try:
                    self.mcp_server_process.wait(timeout=5)
                    print("✅ MCP 서버 정상 종료")
                except subprocess.TimeoutExpired:
                    print("⚠️ MCP 서버 강제 종료")
                    self.mcp_server_process.kill()

            print("✅ 모든 리소스 정리 완료")

        except Exception as e:
            print(f"⚠️ 정리 중 오류: {e}")


async def main():
    """메인 데모 함수"""
    demo = PlaywrightMCPDemo()

    try:
        print("🚀 HTTP 기반 Playwright MCP 데모 시작")
        print("=" * 60)

        # MCP 서버 시작
        if not await demo.start_mcp_server():
            print("❌ MCP 서버 시작 실패. 데모를 종료합니다.")
            return

        # ADK 에이전트 설정
        if not await demo.setup_adk_agent():
            print("❌ ADK 에이전트 설정 실패. 데모를 종료합니다.")
            return

        # 데모 시나리오 실행
        results = await demo.run_demo_scenarios()

        print(f"\n🎉 데모 완료! {len(results)}개 시나리오 실행됨")

    except KeyboardInterrupt:
        print("\n⏹️ 사용자가 데모를 중단했습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    # Node.js 확인
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("❌ Node.js가 필요합니다. https://nodejs.org/에서 설치하세요.")
        sys.exit(1)

    # 데모 실행
    asyncio.run(main())
