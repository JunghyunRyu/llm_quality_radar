#!/usr/bin/env python3
"""
Google ADK와 Playwright MCP 데모 실행 스크립트
간단한 시연을 위한 스크립트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from multi_tool_agent.adk_playwright_mcp_agent import ADKPlaywrightMCPAgent
from config.adk_config import adk_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def run_simple_demo():
    """간단한 데모 실행"""
    try:
        print("🚀 Google ADK Playwright MCP 데모 시작")
        print("=" * 50)

        # 설정 확인
        validation = adk_config.validate_config()
        print("📋 환경 설정:")
        for key, value in validation.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}")

        if not any(validation.values()):
            print("\n❌ API 설정이 필요합니다.")
            print("💡 .env 파일에 다음 중 하나를 설정하세요:")
            print("GOOGLE_API_KEY=your-api-key  # 또는")
            print("GOOGLE_CLOUD_PROJECT=your-project (Vertex AI 사용시)")
            return

        # 에이전트 초기화
        print("\n🔧 에이전트 초기화 중...")
        agent = ADKPlaywrightMCPAgent()
        await agent._initialize_agent()

        # 간단한 테스트
        print("\n🌐 웹 테스트 실행...")
        result = await agent.run_test_scenario(
            "Example.com (https://www.example.com)으로 이동해서 페이지 정보를 분석해주세요."
        )

        print("\n✅ 테스트 완료!")
        print(f"결과: {result.get('status', 'unknown')}")

        # 정리
        await agent.cleanup()

    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        logger.error(f"데모 실행 실패: {e}")


if __name__ == "__main__":
    asyncio.run(run_simple_demo())
