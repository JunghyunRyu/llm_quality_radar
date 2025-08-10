#!/usr/bin/env python3
"""
Google ADK 기본 데모 - MCP 없이 기본 기능 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger

logger = setup_logger(__name__)


def simple_web_info(url: str) -> dict:
    """간단한 웹 정보 수집 도구"""
    import requests

    try:
        response = requests.get(url, timeout=10)
        return {
            "url": url,
            "status_code": response.status_code,
            "title": "웹 페이지" if response.status_code == 200 else "접속 실패",
            "content_length": len(response.content),
            "headers": dict(response.headers),
        }
    except Exception as e:
        return {"url": url, "error": str(e), "status": "failed"}


def analyze_text(text: str) -> dict:
    """텍스트 분석 도구"""
    return {
        "text": text,
        "length": len(text),
        "words": len(text.split()),
        "lines": len(text.split("\n")),
        "analysis": f"'{text[:50]}...' 텍스트를 분석했습니다.",
    }


async def test_basic_adk():
    """기본 ADK 기능 테스트"""
    try:
        print("🚀 Google ADK 기본 기능 테스트")
        print("=" * 50)

        # Google ADK 기본 import 테스트
        try:
            from google.adk.agents.llm_agent import LlmAgent
            from google.adk.tools.function_tool import FunctionTool

            print("✅ Google ADK 모듈 import 성공")
        except ImportError as e:
            print(f"❌ Google ADK 모듈 import 실패: {e}")
            return

        # 도구 생성
        web_tool = FunctionTool(simple_web_info)
        text_tool = FunctionTool(analyze_text)

        print("✅ ADK 도구 생성 완료")

        # API 키 없이는 실제 LLM 에이전트를 생성할 수 없으므로
        # 도구 기능만 테스트
        print("\n🔧 도구 기능 테스트:")

        # 웹 정보 도구 테스트
        web_result = await web_tool.run_async(
            args={"url": "https://www.example.com"}, tool_context=None
        )
        print(f"🌐 웹 정보 도구 결과: {web_result}")

        # 텍스트 분석 도구 테스트
        text_result = await text_tool.run_async(
            args={"text": "Google ADK와 Playwright MCP 통합 테스트"}, tool_context=None
        )
        print(f"📝 텍스트 분석 도구 결과: {text_result}")

        print("\n✅ 기본 ADK 기능 테스트 완료!")
        print("\n💡 다음 단계:")
        print("1. Google AI API 키 또는 Vertex AI 설정")
        print("2. Playwright MCP 패키지 문제 해결")
        print("3. 완전한 통합 테스트 실행")

    except Exception as e:
        print(f"💥 오류 발생: {e}")
        logger.error(f"ADK 테스트 실패: {e}")


if __name__ == "__main__":
    asyncio.run(test_basic_adk())
