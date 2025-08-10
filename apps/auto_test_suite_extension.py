#!/usr/bin/env python3
"""
자동 테스트 스위트 확장 - 테스트 케이스 생성, 스크립트 생성, 실행, 모니터링
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from apps.auto_test_suite import AutoTestSuite
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AutoTestSuiteExtension(AutoTestSuite):
    """자동 테스트 스위트 확장 클래스"""

    async def _generate_test_cases_from_analysis(
        self, page_analysis: Dict[str, Any], test_type: str
    ) -> List[Dict[str, Any]]:
        """분석 결과를 바탕으로 테스트 케이스 자동 생성"""
        try:
            logger.info("분석 결과를 바탕으로 테스트 케이스 생성 시작")

            test_cases = []

            # 1. 기본 페이지 로드 테스트
            test_cases.append(
                {
                    "id": "page_load_test",
                    "name": "페이지 로드 테스트",
                    "description": "페이지가 정상적으로 로드되는지 확인",
                    "type": "functional",
                    "priority": "high",
                    "steps": [
                        {
                            "action": "navigate",
                            "target": "page",
                            "description": "페이지 접근",
                        },
                        {
                            "action": "wait_for_page_load",
                            "description": "페이지 로드 완료 대기",
                        },
                        {
                            "action": "assert_title",
                            "expected_value": page_analysis.get("basic_info", {}).get(
                                "title", ""
                            ),
                            "description": "페이지 제목 확인",
                        },
                    ],
                }
            )

            # 2. 상호작용 요소 테스트
            interactive_elements = page_analysis.get("interactive_elements", {}).get(
                "clickable_elements", []
            )
            for i, element in enumerate(interactive_elements[:5]):  # 상위 5개만
                if element.get("isVisible") and element.get("isClickable"):
                    test_cases.append(
                        {
                            "id": f"click_test_{i}",
                            "name": f"클릭 테스트 - {element.get('text', 'Unknown')}",
                            "description": f"요소 '{element.get('text', 'Unknown')}' 클릭 가능성 확인",
                            "type": "functional",
                            "priority": "medium",
                            "steps": [
                                {
                                    "action": "wait_for_element",
                                    "selector": element.get("selector"),
                                    "description": f"요소 대기: {element.get('selector')}",
                                },
                                {
                                    "action": "click",
                                    "selector": element.get("selector"),
                                    "description": f"요소 클릭: {element.get('selector')}",
                                },
                            ],
                        }
                    )

            # 3. 폼 테스트
            form_elements = page_analysis.get("form_elements", [])
            for i, form in enumerate(form_elements):
                if form.get("fields"):
                    test_cases.append(
                        {
                            "id": f"form_test_{i}",
                            "name": f"폼 테스트 - 폼 {i+1}",
                            "description": f"폼 {i+1}의 입력 필드 테스트",
                            "type": "functional",
                            "priority": "high",
                            "steps": self._generate_form_test_steps(form),
                        }
                    )

            # 4. 링크 테스트
            links = page_analysis.get("page_structure", {}).get("links", [])
            for i, link in enumerate(links[:3]):  # 상위 3개만
                test_cases.append(
                    {
                        "id": f"link_test_{i}",
                        "name": f"링크 테스트 - {link.get('text', 'Unknown')}",
                        "description": f"링크 '{link.get('text', 'Unknown')}' 클릭 테스트",
                        "type": "functional",
                        "priority": "medium",
                        "steps": [
                            {
                                "action": "click",
                                "selector": link.get("selector"),
                                "description": f"링크 클릭: {link.get('text')}",
                            },
                            {
                                "action": "wait_for_page_load",
                                "description": "페이지 로드 대기",
                            },
                        ],
                    }
                )

            # 5. 접근성 테스트 (test_type이 accessibility인 경우)
            if test_type in ["comprehensive", "accessibility"]:
                accessibility_tests = self._generate_accessibility_test_cases(
                    page_analysis
                )
                test_cases.extend(accessibility_tests)

            # 6. 성능 테스트 (test_type이 performance인 경우)
            if test_type in ["comprehensive", "performance"]:
                performance_tests = self._generate_performance_test_cases(page_analysis)
                test_cases.extend(performance_tests)

            self.generated_test_cases = test_cases
            logger.info(f"테스트 케이스 생성 완료: {len(test_cases)}개")
            return test_cases

        except Exception as e:
            logger.error(f"테스트 케이스 생성 실패: {e}")
            return []

    def _generate_form_test_steps(self, form: Dict[str, Any]) -> List[Dict[str, Any]]:
        """폼 테스트 스텝 생성"""
        steps = []

        # 각 입력 필드에 대한 테스트 스텝
        for field in form.get("fields", []):
            if field.get("type") in ["text", "email", "password"]:
                steps.append(
                    {
                        "action": "type",
                        "selector": field.get("selector"),
                        "value": self._get_test_value(field.get("type")),
                        "description": f"입력 필드 '{field.get('name')}'에 테스트 값 입력",
                    }
                )

        # 제출 버튼 클릭
        if form.get("submitButtons"):
            steps.append(
                {
                    "action": "click",
                    "selector": form["submitButtons"][0].get("selector"),
                    "description": "폼 제출",
                }
            )

        return steps

    def _generate_accessibility_test_cases(
        self, page_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """접근성 테스트 케이스 생성"""
        test_cases = []

        # Alt 텍스트 테스트
        images = page_analysis.get("page_structure", {}).get("images", [])
        if images:
            test_cases.append(
                {
                    "id": "accessibility_alt_text_test",
                    "name": "접근성 - Alt 텍스트 테스트",
                    "description": "이미지의 Alt 텍스트 존재 여부 확인",
                    "type": "accessibility",
                    "priority": "high",
                    "steps": [
                        {
                            "action": "check_alt_text",
                            "target": "images",
                            "description": "모든 이미지의 Alt 텍스트 확인",
                        }
                    ],
                }
            )

        # 키보드 네비게이션 테스트
        focusable_elements = page_analysis.get("interactive_elements", {}).get(
            "focusable_elements", []
        )
        if focusable_elements:
            test_cases.append(
                {
                    "id": "accessibility_keyboard_test",
                    "name": "접근성 - 키보드 네비게이션 테스트",
                    "description": "키보드로 모든 상호작용 요소에 접근 가능한지 확인",
                    "type": "accessibility",
                    "priority": "high",
                    "steps": [
                        {
                            "action": "keyboard_navigation",
                            "target": "focusable_elements",
                            "description": "Tab 키를 사용한 네비게이션 테스트",
                        }
                    ],
                }
            )

        return test_cases

    def _generate_performance_test_cases(
        self, page_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """성능 테스트 케이스 생성"""
        test_cases = []

        # 페이지 로드 시간 테스트
        test_cases.append(
            {
                "id": "performance_load_time_test",
                "name": "성능 - 페이지 로드 시간 테스트",
                "description": "페이지 로드 시간이 기준값 이내인지 확인",
                "type": "performance",
                "priority": "high",
                "steps": [
                    {
                        "action": "measure_load_time",
                        "target": "page",
                        "threshold": 3000,  # 3초
                        "description": "페이지 로드 시간 측정",
                    }
                ],
            }
        )

        return test_cases

    def _get_test_value(self, field_type: str) -> str:
        """필드 타입에 따른 테스트 값 생성"""
        test_values = {
            "text": "테스트 텍스트",
            "email": "test@example.com",
            "password": "testpass123",
            "number": "123",
            "tel": "010-1234-5678",
            "url": "https://example.com",
        }
        return test_values.get(field_type, "테스트 값")

    async def _generate_automation_scripts(
        self, test_cases: List[Dict[str, Any]], page_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Playwright 자동화 스크립트 생성"""
        try:
            logger.info("자동화 스크립트 생성 시작")

            scripts = []

            # Python Playwright 스크립트 생성
            python_script = self._generate_python_playwright_script(
                test_cases, page_analysis
            )
            scripts.append(
                {
                    "id": "python_playwright_script",
                    "name": "Python Playwright 자동화 스크립트",
                    "language": "python",
                    "content": python_script,
                    "filename": "generated_test_script.py",
                }
            )

            # JSON 테스트 데이터 생성
            json_data = self._generate_json_test_data(test_cases, page_analysis)
            scripts.append(
                {
                    "id": "json_test_data",
                    "name": "JSON 테스트 데이터",
                    "language": "json",
                    "content": json_data,
                    "filename": "test_data.json",
                }
            )

            self.generated_scripts = scripts
            logger.info(f"자동화 스크립트 생성 완료: {len(scripts)}개")
            return scripts

        except Exception as e:
            logger.error(f"자동화 스크립트 생성 실패: {e}")
            return []

    def _generate_python_playwright_script(
        self, test_cases: List[Dict[str, Any]], page_analysis: Dict[str, Any]
    ) -> str:
        """Python Playwright 스크립트 생성"""
        script_content = f'''#!/usr/bin/env python3
"""
자동 생성된 Playwright 테스트 스크립트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
URL: {page_analysis.get('url', 'Unknown')}
"""

import asyncio
from playwright.async_api import async_playwright
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoGeneratedTest:
    """자동 생성된 테스트 클래스"""
    
    def __init__(self, url: str):
        self.url = url
        self.results = []
        
    async def run_all_tests(self):
        """모든 테스트 실행"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                logger.info(f"테스트 시작: {{self.url}}")
                
                # 페이지 로드
                await page.goto(self.url)
                await page.wait_for_load_state('networkidle')
                
                # 테스트 케이스 실행
                test_cases = {json.dumps(test_cases, ensure_ascii=False, indent=2)}
                for test_case in test_cases:
                    await self._execute_test_case(page, test_case)
                
                # 결과 출력
                self._print_results()
                
            except Exception as e:
                logger.error(f"테스트 실행 중 오류: {{e}}")
            finally:
                await browser.close()
    
    async def _execute_test_case(self, page, test_case):
        """개별 테스트 케이스 실행"""
        test_id = test_case.get('id')
        test_name = test_case.get('name')
        
        logger.info(f"테스트 실행: {{test_name}}")
        start_time = datetime.now()
        
        try:
            for step in test_case.get('steps', []):
                await self._execute_step(page, step)
            
            # 성공 결과 기록
            execution_time = (datetime.now() - start_time).total_seconds()
            self.results.append({{
                'test_id': test_id,
                'test_name': test_name,
                'status': 'passed',
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }})
            
            logger.info(f"테스트 성공: {{test_name}} ({{execution_time:.2f}}초)")
            
        except Exception as e:
            # 실패 결과 기록
            execution_time = (datetime.now() - start_time).total_seconds()
            self.results.append({{
                'test_id': test_id,
                'test_name': test_name,
                'status': 'failed',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }})
            
            logger.error(f"테스트 실패: {{test_name}}: {{e}}")
    
    async def _execute_step(self, page, step):
        """테스트 스텝 실행"""
        action = step.get('action')
        target = step.get('target')
        selector = step.get('selector')
        value = step.get('value')
        description = step.get('description', '')
        
        logger.info(f"스텝 실행: {{description}}")
        
        if action == 'navigate':
            await page.goto(self.url)
            await page.wait_for_load_state('networkidle')
            
        elif action == 'wait_for_page_load':
            await page.wait_for_load_state('networkidle')
                
        elif action == 'wait_for_element':
            if selector:
                await page.wait_for_selector(selector)
                
        elif action == 'click':
            if selector:
                await page.click(selector)
                
        elif action == 'type':
            if selector and value:
                await page.fill(selector, value)
                
        elif action == 'assert_title':
            expected_title = step.get('expected_value', '')
            actual_title = await page.title()
            assert actual_title == expected_title, f"제목 불일치: 예상={{expected_title}}, 실제={{actual_title}}"
                
        elif action == 'check_alt_text':
            images = await page.query_selector_all('img')
            for img in images:
                alt = await img.get_attribute('alt')
                if not alt:
                    logger.warning("Alt 텍스트가 없는 이미지 발견")
                    
        elif action == 'keyboard_navigation':
            focusable_elements = await page.query_selector_all('a, button, input, textarea, select')
            for element in focusable_elements:
                await element.focus()
                await page.wait_for_timeout(100)
                
        elif action == 'measure_load_time':
            start_time = datetime.now()
            await page.reload()
            await page.wait_for_load_state('networkidle')
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            threshold = step.get('threshold', 3000)
            assert load_time <= threshold, f"페이지 로드 시간이 너무 깁니다: {{load_time}}ms"
    
    def _print_results(self):
        """테스트 결과 출력"""
        print("\\n=== 테스트 결과 ===")
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {{total_tests}}")
        print(f"성공: {{passed_tests}}")
        print(f"실패: {{failed_tests}}")
        print(f"성공률: {{(passed_tests/total_tests*100):.1f}}%")
        
        print("\\n상세 결과:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            print(f"{{status_icon}} {{result['test_name']}} ({{result['execution_time']:.2f}}초)")

async def main():
    """메인 함수"""
    url = "{page_analysis.get('url', 'https://example.com')}"
    test = AutoGeneratedTest(url)
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
'''
        return script_content

    def _generate_json_test_data(
        self, test_cases: List[Dict[str, Any]], page_analysis: Dict[str, Any]
    ) -> str:
        """JSON 테스트 데이터 생성"""
        test_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "url": page_analysis.get("url"),
                "total_test_cases": len(test_cases),
            },
            "test_cases": test_cases,
            "page_analysis": page_analysis,
        }

        return json.dumps(test_data, ensure_ascii=False, indent=2)

    async def _execute_generated_tests(
        self, test_cases: List[Dict[str, Any]], url: str
    ) -> Dict[str, Any]:
        """생성된 테스트 케이스 실행"""
        try:
            logger.info("생성된 테스트 케이스 실행 시작")

            # MCP 클라이언트가 이미 연결되어 있다면 재사용, 아니면 새로 연결
            if not self.mcp_client.connected:
                await self.mcp_client.connect()

            # 페이지 로드
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            execution_results = []

            # 각 테스트 케이스 실행
            for test_case in test_cases:
                test_result = await self._execute_test_case_with_mcp(test_case)
                execution_results.append(test_result)

            # 연결 해제
            await self.mcp_client.disconnect()

            logger.info(f"테스트 케이스 실행 완료: {len(execution_results)}개")
            return {
                "total_tests": len(execution_results),
                "passed_tests": len(
                    [r for r in execution_results if r.get("status") == "passed"]
                ),
                "failed_tests": len(
                    [r for r in execution_results if r.get("status") == "failed"]
                ),
                "results": execution_results,
            }

        except Exception as e:
            logger.error(f"테스트 케이스 실행 실패: {e}")
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error": str(e),
                "results": [],
            }

    async def _execute_test_case_with_mcp(
        self, test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """MCP를 사용한 개별 테스트 케이스 실행"""
        test_id = test_case.get("id")
        test_name = test_case.get("name")
        start_time = datetime.now()

        try:
            logger.info(f"테스트 케이스 실행: {test_name}")

            for step in test_case.get("steps", []):
                await self._execute_step_with_mcp(step)

            # 성공 결과
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "test_id": test_id,
                "test_name": test_name,
                "status": "passed",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            # 실패 결과
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                "test_id": test_id,
                "test_name": test_name,
                "status": "failed",
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

    async def _execute_step_with_mcp(self, step: Dict[str, Any]):
        """MCP를 사용한 테스트 스텝 실행"""
        action = step.get("action")
        selector = step.get("selector")
        value = step.get("value")
        description = step.get("description", "")

        logger.info(f"스텝 실행: {description}")

        if action == "navigate":
            # 이미 페이지가 로드되어 있으므로 스킵
            pass

        elif action == "wait_for_page_load":
            await self.mcp_client.wait_for_page_load()

        elif action == "wait_for_element":
            if selector:
                await self.mcp_client.wait_for_element(selector)

        elif action == "click":
            if selector:
                await self.mcp_client.click(selector)

        elif action == "type":
            if selector and value:
                await self.mcp_client.type(selector, value)

        elif action == "assert_title":
            expected_title = step.get("expected_value", "")
            actual_title = await self.mcp_client.execute_javascript(
                "() => document.title"
            )
            if actual_title != expected_title:
                raise Exception(
                    f"제목 불일치: 예상={expected_title}, 실제={actual_title}"
                )

        elif action == "check_alt_text":
            images_without_alt = await self.mcp_client.execute_javascript(
                """
                () => {
                    const images = document.querySelectorAll('img');
                    const withoutAlt = [];
                    images.forEach(img => {
                        if (!img.alt) {
                            withoutAlt.push(img.src);
                        }
                    });
                    return withoutAlt;
                }
            """
            )
            if images_without_alt:
                logger.warning(
                    f"Alt 텍스트가 없는 이미지 {len(images_without_alt)}개 발견"
                )

        elif action == "keyboard_navigation":
            focusable_count = await self.mcp_client.execute_javascript(
                """
                () => {
                    const focusables = document.querySelectorAll('a, button, input, textarea, select');
                    return focusables.length;
                }
            """
            )
            logger.info(f"포커스 가능한 요소 {focusable_count}개 발견")

        elif action == "measure_load_time":
            start_time = datetime.now()
            await self.mcp_client.refresh_page()
            await self.mcp_client.wait_for_page_load()
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            threshold = step.get("threshold", 3000)
            if load_time > threshold:
                raise Exception(f"페이지 로드 시간이 너무 깁니다: {load_time}ms")

    async def _perform_monitoring_and_metrics(self, url: str) -> Dict[str, Any]:
        """성능 모니터링 및 메트릭 측정"""
        try:
            logger.info("성능 모니터링 및 메트릭 측정 시작")

            # MCP 클라이언트 연결
            if not self.mcp_client.connected:
                await self.mcp_client.connect()

            # 페이지 로드
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            # 성능 메트릭 수집
            performance_metrics = await self._collect_detailed_performance_metrics()

            # 메모리 사용량 모니터링
            memory_metrics = await self._monitor_memory_usage()

            # 네트워크 상태 모니터링
            network_metrics = await self._monitor_network_status()

            # JavaScript 오류 모니터링
            js_error_metrics = await self._monitor_javascript_errors()

            monitoring_results = {
                "performance_metrics": performance_metrics,
                "memory_metrics": memory_metrics,
                "network_metrics": network_metrics,
                "js_error_metrics": js_error_metrics,
                "monitoring_timestamp": datetime.now().isoformat(),
            }

            logger.info("성능 모니터링 및 메트릭 측정 완료")
            return monitoring_results

        except Exception as e:
            logger.error(f"성능 모니터링 및 메트릭 측정 실패: {e}")
            return {"error": str(e)}

    async def _collect_detailed_performance_metrics(self) -> Dict[str, Any]:
        """상세 성능 메트릭 수집"""
        try:
            detailed_metrics = await self.mcp_client.execute_javascript(
                """
                () => {
                    const metrics = {};
                    
                    // Navigation Timing API
                    if (window.performance && window.performance.timing) {
                        const timing = window.performance.timing;
                        metrics.navigationTiming = {
                            domContentLoaded: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                            loadComplete: timing.loadEventEnd - timing.loadEventStart,
                            domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                            pageLoad: timing.loadEventEnd - timing.navigationStart,
                            firstPaint: timing.responseStart - timing.navigationStart,
                            firstContentfulPaint: timing.domContentLoadedEventEnd - timing.navigationStart
                        };
                    }
                    
                    // Performance Observer
                    if (window.PerformanceObserver) {
                        const paintMetrics = {};
                        const observer = new PerformanceObserver((list) => {
                            list.getEntries().forEach(entry => {
                                if (entry.entryType === 'paint') {
                                    paintMetrics[entry.name] = entry.startTime;
                                }
                            });
                        });
                        observer.observe({ entryTypes: ['paint'] });
                        metrics.paintMetrics = paintMetrics;
                    }
                    
                    // 메모리 사용량
                    if (window.performance && window.performance.memory) {
                        metrics.memory = {
                            usedJSHeapSize: window.performance.memory.usedJSHeapSize,
                            totalJSHeapSize: window.performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit
                        };
                    }
                    
                    // DOM 요소 수
                    metrics.domElements = document.querySelectorAll('*').length;
                    
                    // 이미지 수
                    metrics.imageCount = document.querySelectorAll('img').length;
                    
                    // 링크 수
                    metrics.linkCount = document.querySelectorAll('a').length;
                    
                    // 스크립트 수
                    metrics.scriptCount = document.querySelectorAll('script').length;
                    
                    // 스타일시트 수
                    metrics.stylesheetCount = document.querySelectorAll('link[rel="stylesheet"]').length;
                    
                    return metrics;
                }
            """
            )

            return detailed_metrics

        except Exception as e:
            logger.error(f"상세 성능 메트릭 수집 실패: {e}")
            return {}

    async def _monitor_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 모니터링"""
        try:
            memory_metrics = await self.mcp_client.execute_javascript(
                """
                () => {
                    if (window.performance && window.performance.memory) {
                        const memory = window.performance.memory;
                        return {
                            usedJSHeapSize: memory.usedJSHeapSize,
                            totalJSHeapSize: memory.totalJSHeapSize,
                            jsHeapSizeLimit: memory.jsHeapSizeLimit,
                            heapUsagePercentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
                        };
                    }
                    return null;
                }
            """
            )

            return memory_metrics or {}

        except Exception as e:
            logger.error(f"메모리 사용량 모니터링 실패: {e}")
            return {}

    async def _monitor_network_status(self) -> Dict[str, Any]:
        """네트워크 상태 모니터링"""
        try:
            network_metrics = await self.mcp_client.execute_javascript(
                """
                () => {
                    return {
                        online: navigator.onLine,
                        connectionType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
                        downlink: navigator.connection ? navigator.connection.downlink : null,
                        rtt: navigator.connection ? navigator.connection.rtt : null
                    };
                }
            """
            )

            return network_metrics

        except Exception as e:
            logger.error(f"네트워크 상태 모니터링 실패: {e}")
            return {}

    async def _monitor_javascript_errors(self) -> Dict[str, Any]:
        """JavaScript 오류 모니터링"""
        try:
            js_error_metrics = await self.mcp_client.execute_javascript(
                """
                () => {
                    return {
                        errorCount: window.jsErrors || 0,
                        consoleErrors: window.consoleErrors || [],
                        unhandledRejections: window.unhandledRejections || []
                    };
                }
            """
            )

            return js_error_metrics

        except Exception as e:
            logger.error(f"JavaScript 오류 모니터링 실패: {e}")
            return {}

    async def _generate_comprehensive_report(
        self,
        page_analysis: Dict[str, Any],
        test_cases: List[Dict[str, Any]],
        automation_scripts: List[Dict[str, Any]],
        execution_results: Dict[str, Any],
        monitoring_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """종합 리포트 생성"""
        try:
            total_tests = execution_results.get("total_tests", 0)
            passed_tests = execution_results.get("passed_tests", 0)
            failed_tests = execution_results.get("failed_tests", 0)

            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            report = {
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "generated_scripts": len(automation_scripts),
                },
                "page_analysis_summary": {
                    "url": page_analysis.get("url"),
                    "title": page_analysis.get("basic_info", {}).get("title"),
                    "total_elements": self._count_total_elements(page_analysis),
                    "interactive_elements": len(
                        page_analysis.get("interactive_elements", {}).get(
                            "clickable_elements", []
                        )
                    ),
                    "forms": len(page_analysis.get("form_elements", [])),
                    "images": len(
                        page_analysis.get("page_structure", {}).get("images", [])
                    ),
                },
                "test_cases_summary": {
                    "functional_tests": len(
                        [tc for tc in test_cases if tc.get("type") == "functional"]
                    ),
                    "accessibility_tests": len(
                        [tc for tc in test_cases if tc.get("type") == "accessibility"]
                    ),
                    "performance_tests": len(
                        [tc for tc in test_cases if tc.get("type") == "performance"]
                    ),
                },
                "performance_summary": {
                    "load_time": monitoring_results.get("performance_metrics", {})
                    .get("navigationTiming", {})
                    .get("pageLoad"),
                    "memory_usage": monitoring_results.get("memory_metrics", {}).get(
                        "heapUsagePercentage"
                    ),
                    "dom_elements": monitoring_results.get(
                        "performance_metrics", {}
                    ).get("domElements"),
                },
                "recommendations": self._generate_recommendations(
                    page_analysis, execution_results, monitoring_results
                ),
                "generated_files": [
                    {
                        "name": script.get("name"),
                        "filename": script.get("filename"),
                        "language": script.get("language"),
                    }
                    for script in automation_scripts
                ],
            }

            return report

        except Exception as e:
            logger.error(f"종합 리포트 생성 실패: {e}")
            return {"error": str(e)}

    def _count_total_elements(self, page_analysis: Dict[str, Any]) -> int:
        """페이지 요소 총 개수 계산"""
        page_structure = page_analysis.get("page_structure", {})
        total = 0
        for element_type in [
            "headings",
            "paragraphs",
            "images",
            "links",
            "buttons",
            "inputs",
        ]:
            total += len(page_structure.get(element_type, []))
        return total

    def _generate_recommendations(
        self,
        page_analysis: Dict[str, Any],
        execution_results: Dict[str, Any],
        monitoring_results: Dict[str, Any],
    ) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []

        # 성공률 기반 권장사항
        success_rate = (
            execution_results.get("passed_tests", 0)
            / max(execution_results.get("total_tests", 1), 1)
            * 100
        )
        if success_rate < 80:
            recommendations.append(
                "테스트 성공률이 낮습니다. 페이지 요소의 선택자를 개선하거나 대기 시간을 늘려보세요."
            )

        # 접근성 기반 권장사항
        images = page_analysis.get("page_structure", {}).get("images", [])
        images_without_alt = [img for img in images if not img.get("alt")]
        if images_without_alt:
            recommendations.append(
                f"Alt 텍스트가 없는 이미지가 {len(images_without_alt)}개 있습니다. 접근성을 위해 Alt 텍스트를 추가하세요."
            )

        # 성능 기반 권장사항
        performance_metrics = monitoring_results.get("performance_metrics", {})
        load_time = performance_metrics.get("navigationTiming", {}).get("pageLoad")
        if load_time and load_time > 3000:
            recommendations.append(
                f"페이지 로드 시간이 {load_time}ms로 느립니다. 성능 최적화를 고려하세요."
            )

        memory_usage = monitoring_results.get("memory_metrics", {}).get(
            "heapUsagePercentage"
        )
        if memory_usage and memory_usage > 80:
            recommendations.append(
                f"메모리 사용량이 {memory_usage:.1f}%로 높습니다. 메모리 누수를 확인하세요."
            )

        # 폼 기반 권장사항
        forms = page_analysis.get("form_elements", [])
        for form in forms:
            fields = form.get("fields", [])
            required_fields = [field for field in fields if field.get("required")]
            if not required_fields:
                recommendations.append(
                    "폼에 필수 필드 표시가 없습니다. 사용자 경험을 위해 필수 필드를 명확히 표시하세요."
                )

        return recommendations


# 사용 예제
async def main():
    """메인 함수"""
    auto_suite = AutoTestSuiteExtension()

    # 완전한 테스트 워크플로우 실행
    result = await auto_suite.run_complete_test_workflow(
        url="https://www.google.com", test_type="comprehensive"
    )

    print("=== 자동 테스트 스위트 결과 ===")
    print(f"워크플로우 ID: {result['workflow_id']}")
    print(f"상태: {result['status']}")
    print(f"실행 시간: {result['execution_time']:.2f}초")

    if result["status"] == "completed":
        summary = result["final_report"]["summary"]
        print(f"총 테스트: {summary['total_tests']}")
        print(f"성공: {summary['passed_tests']}")
        print(f"실패: {summary['failed_tests']}")
        print(f"성공률: {summary['success_rate']:.1f}%")

        performance = result["final_report"]["performance_summary"]
        print(f"페이지 로드 시간: {performance.get('load_time', 'N/A')}ms")
        print(f"메모리 사용량: {performance.get('memory_usage', 'N/A')}%")
        print(f"DOM 요소 수: {performance.get('dom_elements', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
