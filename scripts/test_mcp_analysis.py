#!/usr/bin/env python3
"""
로컬 MCP 서버(@playwright/mcp: http://localhost:3001)와 연동하여
웹 페이지 분석 및 자동 테스트 케이스 생성이 정상 동작하는지 빠르게 검증하는 스크립트.

사용법:
  python scripts/test_mcp_analysis.py https://www.google.com
"""

import asyncio
import json
import sys
from typing import Any, Dict

from apps.auto_test_suite_extension import AutoTestSuiteExtension


async def main(url: str) -> None:
    suite = AutoTestSuiteExtension()

    print(f"[1/3] MCP 분석 시작: {url}")
    analysis: Dict[str, Any] = await suite._analyze_webpage_with_mcp(url)
    title = (analysis.get("basic_info") or {}).get("title", "")
    num_links = len((analysis.get("page_structure") or {}).get("links", []))
    print(json.dumps({
        "title": title,
        "links": num_links,
        "has_forms": bool(analysis.get("form_elements")),
    }, ensure_ascii=False))

    print("[2/3] 테스트 케이스 자동 생성")
    test_cases = await suite._generate_test_cases_from_analysis(analysis, "comprehensive")
    print(json.dumps({
        "generated_cases": len(test_cases),
        "sample_case": (test_cases[0] if test_cases else None)
    }, ensure_ascii=False, indent=2))

    print("[3/3] 생성된 테스트 일부 실행(드라이런)")
    # 실 실행 경로는 환경에 따라 제한될 수 있어, 여기서는 첫 케이스만 시도
    if test_cases:
        partial = await suite._execute_generated_tests(test_cases[:1], url)
        print(json.dumps({
            "partial_execution_keys": list(partial.keys())
        }, ensure_ascii=False))
    else:
        print("생성된 케이스가 없어 실행을 스킵합니다.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    asyncio.run(main(target))


