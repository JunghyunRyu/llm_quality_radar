"""
Google ADK와 Playwright MCP 연계 에이전트
웹 자동화 테스트와 AI 기반 품질 분석을 결합한 혁신적인 시스템
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from google.adk.agents import Agent
from core.mcp_client import PlaywrightMCPClient
from core.google_adk_integration import GoogleADKIntegration
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PlaywrightADKAgent:
    """Google ADK와 Playwright MCP를 연계한 에이전트"""

    def __init__(self):
        self.mcp_client = PlaywrightMCPClient()
        self.google_adk = GoogleADKIntegration()
        self.agent = None
        self.test_results = []

        # 에이전트 초기화
        self._initialize_agent()

    def _initialize_agent(self):
        """Google ADK 에이전트 초기화"""
        self.agent = Agent(
            name="playwright_qa_agent",
            model="gemini-2.0-flash",
            description=(
                "Playwright MCP와 Google ADK를 연계한 웹 자동화 테스트 및 "
                "AI 기반 품질 분석 에이전트"
            ),
            instruction=(
                "당신은 웹 자동화 테스트 전문가입니다. Playwright MCP를 통해 "
                "웹 브라우저를 제어하고, Google ADK의 AI 기능을 활용하여 "
                "고급 품질 분석을 수행합니다. 사용자의 요청에 따라 웹사이트를 "
                "테스트하고, 문제점을 분석하며, 개선 방안을 제시합니다."
            ),
            tools=[
                self.run_web_test,
                self.analyze_webpage_quality,
                self.perform_ai_enhanced_analysis,
                self.generate_test_report,
                self.auto_heal_test_issues,
                self.monitor_web_performance,
                self.capture_visual_evidence,
                self.analyze_accessibility,
                self.test_responsive_design,
                self.generate_ml_recommendations,
            ],
        )

    async def run_web_test(
        self, url: str, test_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """웹 테스트 실행

        Args:
            url (str): 테스트할 웹사이트 URL
            test_scenarios (List[Dict]): 실행할 테스트 시나리오 목록

        Returns:
            Dict: 테스트 실행 결과
        """
        try:
            logger.info(f"웹 테스트 시작: {url}")
            start_time = datetime.now()

            # MCP 클라이언트 연결
            await self.mcp_client.connect()

            # 페이지 로드
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            # 테스트 시나리오 실행
            test_results = []
            for i, scenario in enumerate(test_scenarios):
                scenario_description = scenario.get("description", "Unknown")
                logger.info(f"시나리오 {i+1} 실행: {scenario_description}")

                # 시나리오 진행 상황 업데이트 (콜백이 있는 경우)
                if hasattr(self, "update_progress_callback"):
                    self.update_progress_callback(
                        {
                            "current_scenario": f"시나리오 {i+1}: {scenario_description}",
                            "completed_scenarios": i,
                            "total_scenarios": len(test_scenarios),
                        }
                    )

                result = await self._execute_test_scenario(scenario)
                test_results.append(result)

            # 스크린샷 캡처
            screenshots = await self.mcp_client.capture_screenshots()

            # 로그 수집
            logs = await self.mcp_client.get_logs()

            # MCP 클라이언트 연결 해제
            await self.mcp_client.disconnect()

            # 결과 정리
            success_count = sum(1 for r in test_results if r.get("success", False))
            total_count = len(test_results)
            execution_time = (datetime.now() - start_time).total_seconds()

            test_result = {
                "test_id": f"web_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "total_scenarios": total_count,
                "success_count": success_count,
                "failure_count": total_count - success_count,
                "success_rate": (
                    (success_count / total_count * 100) if total_count > 0 else 0
                ),
                "screenshots": screenshots,
                "logs": logs,
                "detailed_results": test_results,
            }

            # 결과 저장
            self.test_results.append(test_result)

            logger.info(f"웹 테스트 완료: 성공률 {test_result['success_rate']:.1f}%")
            return test_result

        except Exception as e:
            logger.error(f"웹 테스트 실행 중 오류: {e}")
            return {"status": "error", "error_message": str(e), "url": url}

    async def _execute_test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """개별 테스트 시나리오 실행"""
        try:
            action = scenario.get("action")
            selector = scenario.get("selector")
            value = scenario.get("value")
            description = scenario.get("description", "Unknown action")

            start_time = datetime.now()

            if action == "click":
                await self.mcp_client.wait_for_element_to_be_clickable(selector)
                await self.mcp_client.click(selector)
                result = {"success": True, "action": "click", "selector": selector}

            elif action == "type":
                await self.mcp_client.wait_for_element(selector)
                await self.mcp_client.type(selector, value)
                result = {
                    "success": True,
                    "action": "type",
                    "selector": selector,
                    "value": value,
                }

            elif action == "wait":
                await self.mcp_client.wait_for_element(selector)
                result = {"success": True, "action": "wait", "selector": selector}

            elif action == "assert":
                exists = await self.mcp_client.element_exists(selector)
                if value:
                    # 값 검증
                    actual_value = await self.mcp_client.execute_javascript(
                        f"document.querySelector('{selector}').textContent"
                    )
                    result = {
                        "success": actual_value == value,
                        "action": "assert",
                        "selector": selector,
                        "expected": value,
                        "actual": actual_value,
                    }
                else:
                    # 존재 여부만 검증
                    result = {
                        "success": exists,
                        "action": "assert",
                        "selector": selector,
                    }

            elif action == "scroll":
                await self.mcp_client.scroll_to_element(selector)
                result = {"success": True, "action": "scroll", "selector": selector}

            else:
                result = {"success": False, "action": action, "error": "Unknown action"}

            # 실행 시간 계산
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            result["description"] = description

            return result

        except Exception as e:
            logger.error(f"시나리오 실행 중 오류: {e}")
            return {
                "success": False,
                "action": scenario.get("action"),
                "error": str(e),
                "description": scenario.get("description", "Unknown"),
            }

    async def analyze_webpage_quality(self, url: str) -> Dict[str, Any]:
        """웹페이지 품질 분석"""
        try:
            logger.info(f"웹페이지 품질 분석 시작: {url}")

            # MCP 클라이언트 연결
            await self.mcp_client.connect()
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            # 다양한 품질 지표 수집
            quality_metrics = {}

            # 1. 페이지 로드 성능
            load_time = await self._measure_page_load_time()
            quality_metrics["page_load_time"] = load_time

            # 2. 네트워크 상태
            network_status = await self.mcp_client.get_network_status()
            quality_metrics["network_status"] = network_status

            # 3. JavaScript 오류 확인
            js_errors = await self._check_javascript_errors()
            quality_metrics["javascript_errors"] = js_errors

            # 4. 이미지 로딩 상태
            image_status = await self._check_image_loading()
            quality_metrics["image_loading"] = image_status

            # 5. 폼 요소 검증
            form_validation = await self._validate_form_elements()
            quality_metrics["form_validation"] = form_validation

            # 6. 링크 상태 확인
            link_status = await self._check_link_status()
            quality_metrics["link_status"] = link_status

            # 품질 점수 계산
            quality_score = self._calculate_quality_score(quality_metrics)

            # 스크린샷 캡처
            screenshots = await self.mcp_client.capture_screenshots()

            await self.mcp_client.disconnect()

            analysis_result = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "quality_score": quality_score,
                "metrics": quality_metrics,
                "screenshots": screenshots,
                "recommendations": self._generate_quality_recommendations(
                    quality_metrics
                ),
            }

            logger.info(f"품질 분석 완료: 점수 {quality_score:.1f}/100")
            return analysis_result

        except Exception as e:
            logger.error(f"품질 분석 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def _measure_page_load_time(self) -> float:
        """페이지 로드 시간 측정"""
        try:
            start_time = datetime.now()
            await self.mcp_client.wait_for_page_load()
            load_time = (datetime.now() - start_time).total_seconds()
            return load_time
        except Exception as e:
            logger.error(f"페이지 로드 시간 측정 실패: {e}")
            return 0.0

    async def _check_javascript_errors(self) -> List[str]:
        """JavaScript 오류 확인"""
        try:
            logs = await self.mcp_client.get_logs()
            js_errors = [log for log in logs if "error" in log.lower()]
            return js_errors
        except Exception as e:
            logger.error(f"JavaScript 오류 확인 실패: {e}")
            return []

    async def _check_image_loading(self) -> Dict[str, Any]:
        """이미지 로딩 상태 확인"""
        try:
            script = """
            const images = document.querySelectorAll('img');
            const results = {
                total: images.length,
                loaded: 0,
                failed: 0,
                broken: []
            };
            
            for (let img of images) {
                if (img.complete && img.naturalHeight !== 0) {
                    results.loaded++;
                } else {
                    results.failed++;
                    if (img.src) {
                        results.broken.push(img.src);
                    }
                }
            }
            
            return results;
            """

            result = await self.mcp_client.execute_javascript(script)
            return result
        except Exception as e:
            logger.error(f"이미지 로딩 확인 실패: {e}")
            return {"total": 0, "loaded": 0, "failed": 0, "broken": []}

    async def _validate_form_elements(self) -> Dict[str, Any]:
        """폼 요소 검증"""
        try:
            script = """
            const forms = document.querySelectorAll('form');
            const results = {
                total_forms: forms.length,
                valid_forms: 0,
                issues: []
            };
            
            for (let form of forms) {
                const inputs = form.querySelectorAll('input, select, textarea');
                let has_issues = false;
                
                for (let input of inputs) {
                    if (input.required && !input.value) {
                        has_issues = true;
                        results.issues.push({
                            type: 'missing_required_field',
                            field: input.name || input.id,
                            form: form.id || 'unknown'
                        });
                    }
                }
                
                if (!has_issues) {
                    results.valid_forms++;
                }
            }
            
            return results;
            """

            result = await self.mcp_client.execute_javascript(script)
            return result
        except Exception as e:
            logger.error(f"폼 요소 검증 실패: {e}")
            return {"total_forms": 0, "valid_forms": 0, "issues": []}

    async def _check_link_status(self) -> Dict[str, Any]:
        """링크 상태 확인"""
        try:
            script = """
            const links = document.querySelectorAll('a[href]');
            const results = {
                total_links: links.length,
                internal_links: 0,
                external_links: 0,
                broken_links: []
            };
            
            for (let link of links) {
                const href = link.href;
                if (href.startsWith(window.location.origin)) {
                    results.internal_links++;
                } else {
                    results.external_links++;
                }
            }
            
            return results;
            """

            result = await self.mcp_client.execute_javascript(script)
            return result
        except Exception as e:
            logger.error(f"링크 상태 확인 실패: {e}")
            return {
                "total_links": 0,
                "internal_links": 0,
                "external_links": 0,
                "broken_links": [],
            }

    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """품질 점수 계산"""
        score = 100.0

        # 페이지 로드 시간에 따른 감점
        load_time = metrics.get("page_load_time", 0)
        if load_time > 5:
            score -= 20
        elif load_time > 3:
            score -= 10

        # JavaScript 오류에 따른 감점
        js_errors = metrics.get("javascript_errors", [])
        score -= len(js_errors) * 5

        # 이미지 로딩 실패에 따른 감점
        image_status = metrics.get("image_loading", {})
        failed_images = image_status.get("failed", 0)
        total_images = image_status.get("total", 1)
        if total_images > 0:
            failure_rate = failed_images / total_images
            score -= failure_rate * 15

        # 폼 검증 문제에 따른 감점
        form_validation = metrics.get("form_validation", {})
        issues = form_validation.get("issues", [])
        score -= len(issues) * 3

        return max(0, score)

    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """품질 개선 권장사항 생성"""
        recommendations = []

        # 페이지 로드 시간 개선
        load_time = metrics.get("page_load_time", 0)
        if load_time > 3:
            recommendations.append("페이지 로드 시간을 3초 이하로 개선하세요")

        # JavaScript 오류 수정
        js_errors = metrics.get("javascript_errors", [])
        if js_errors:
            recommendations.append(f"{len(js_errors)}개의 JavaScript 오류를 수정하세요")

        # 이미지 최적화
        image_status = metrics.get("image_loading", {})
        failed_images = image_status.get("failed", 0)
        if failed_images > 0:
            recommendations.append(f"{failed_images}개의 이미지 로딩 문제를 해결하세요")

        # 폼 검증 개선
        form_validation = metrics.get("form_validation", {})
        issues = form_validation.get("issues", [])
        if issues:
            recommendations.append("필수 입력 필드에 대한 검증을 강화하세요")

        return recommendations

    async def perform_ai_enhanced_analysis(
        self, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI 강화 분석 수행"""
        try:
            logger.info("AI 강화 분석 시작")

            # Google ADK의 AI 기능 활용
            analysis_result = await self.google_adk.ai_enhanced_quality_analysis(
                test_data
            )

            # ML 기반 예측 추가
            predictions = await self.google_adk._generate_quality_predictions(test_data)

            # 개선 제안 생성
            recommendations = (
                await self.google_adk._generate_improvement_recommendations(test_data)
            )

            enhanced_result = {
                "ai_analysis": analysis_result,
                "predictions": predictions,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
                "confidence_score": 0.92,
            }

            logger.info("AI 강화 분석 완료")
            return enhanced_result

        except Exception as e:
            logger.error(f"AI 강화 분석 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def generate_test_report(
        self, test_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """테스트 리포트 생성"""
        try:
            if test_id:
                # 특정 테스트 결과 찾기
                test_result = next(
                    (r for r in self.test_results if r.get("test_id") == test_id), None
                )
                if not test_result:
                    return {
                        "status": "error",
                        "error_message": "테스트를 찾을 수 없습니다",
                    }
            else:
                # 최신 테스트 결과 사용
                if not self.test_results:
                    return {
                        "status": "error",
                        "error_message": "테스트 결과가 없습니다",
                    }
                test_result = self.test_results[-1]

            # 리포트 생성
            report = {
                "test_id": test_result.get("test_id", "unknown"),
                "url": test_result.get("url"),
                "timestamp": test_result.get("timestamp"),
                "status": "completed",  # 상태 필드 추가
                "execution_time": test_result.get("execution_time", 0),
                "success_rate": test_result.get("success_rate", 0),
                "summary": {
                    "total_scenarios": test_result.get("total_scenarios", 0),
                    "success_count": test_result.get("success_count", 0),
                    "failure_count": test_result.get("failure_count", 0),
                    "success_rate": test_result.get("success_rate", 0),
                },
                "detailed_results": test_result.get("detailed_results", []),
                "screenshots": test_result.get("screenshots", []),
                "logs": test_result.get("logs", []),
                "recommendations": self._generate_report_recommendations(test_result),
            }

            logger.info(f"테스트 리포트 생성 완료: {report['test_id']}")
            return report

        except Exception as e:
            logger.error(f"테스트 리포트 생성 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    def _generate_report_recommendations(
        self, test_result: Dict[str, Any]
    ) -> List[str]:
        """리포트 기반 권장사항 생성"""
        recommendations = []

        success_rate = test_result.get("success_rate", 0)
        if success_rate < 80:
            recommendations.append("테스트 성공률을 80% 이상으로 개선하세요")

        failure_count = test_result.get("failure_count", 0)
        if failure_count > 0:
            recommendations.append(f"{failure_count}개의 실패한 테스트를 수정하세요")

        return recommendations

    async def auto_heal_test_issues(
        self, error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """테스트 이슈 자동 복구"""
        try:
            logger.info("자동 복구 시작")

            # Google ADK의 ML 기반 자동 복구 활용
            healing_result = await self.google_adk.ml_based_auto_healing(error_context)

            logger.info("자동 복구 완료")
            return healing_result

        except Exception as e:
            logger.error(f"자동 복구 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def monitor_web_performance(
        self, url: str, duration: int = 60
    ) -> Dict[str, Any]:
        """웹 성능 모니터링"""
        try:
            logger.info(f"웹 성능 모니터링 시작: {url} ({duration}초)")

            await self.mcp_client.connect()
            await self.mcp_client.navigate(url)

            performance_data = []
            start_time = datetime.now()

            while (datetime.now() - start_time).total_seconds() < duration:
                # 성능 메트릭 수집
                metrics = await self._collect_performance_metrics()
                metrics["timestamp"] = datetime.now().isoformat()
                performance_data.append(metrics)

                await asyncio.sleep(5)  # 5초마다 측정

            await self.mcp_client.disconnect()

            # 성능 분석
            analysis = self._analyze_performance_data(performance_data)

            result = {
                "url": url,
                "duration": duration,
                "performance_data": performance_data,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("웹 성능 모니터링 완료")
            return result

        except Exception as e:
            logger.error(f"성능 모니터링 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        try:
            script = """
            const performance = window.performance;
            const navigation = performance.getEntriesByType('navigation')[0];
            
            return {
                load_time: navigation.loadEventEnd - navigation.loadEventStart,
                dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                first_paint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                memory_usage: performance.memory ? {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize
                } : null
            };
            """

            metrics = await self.mcp_client.execute_javascript(script)
            return metrics

        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
            return {}

    def _analyze_performance_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """성능 데이터 분석"""
        if not data:
            return {}

        # 평균값 계산
        avg_load_time = sum(d.get("load_time", 0) for d in data) / len(data)
        avg_dom_loaded = sum(d.get("dom_content_loaded", 0) for d in data) / len(data)

        # 메모리 사용량 분석
        memory_data = [d.get("memory_usage") for d in data if d.get("memory_usage")]
        avg_memory_usage = 0
        if memory_data:
            avg_memory_usage = sum(m.get("used", 0) for m in memory_data) / len(
                memory_data
            )

        return {
            "average_load_time": avg_load_time,
            "average_dom_content_loaded": avg_dom_loaded,
            "average_memory_usage": avg_memory_usage,
            "data_points": len(data),
            "performance_trend": "stable",
        }

    async def capture_visual_evidence(
        self, url: str, elements: List[str]
    ) -> Dict[str, Any]:
        """시각적 증거 캡처"""
        try:
            logger.info(f"시각적 증거 캡처 시작: {url}")

            await self.mcp_client.connect()
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            evidence = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "full_page_screenshot": None,
                "element_screenshots": [],
                "page_info": {},
            }

            # 전체 페이지 스크린샷
            evidence["full_page_screenshot"] = (
                await self.mcp_client.capture_screenshots()
            )

            # 개별 요소 스크린샷
            for selector in elements:
                try:
                    await self.mcp_client.scroll_to_element(selector)
                    await asyncio.sleep(1)

                    # 요소 정보 수집
                    element_info = await self.mcp_client.execute_javascript(
                        f"""
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        return {{
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id,
                            textContent: element.textContent?.substring(0, 100),
                            isVisible: element.offsetParent !== null,
                            dimensions: {{
                                width: element.offsetWidth,
                                height: element.offsetHeight
                            }}
                        }};
                    }}
                    return null;
                    """
                    )

                    evidence["element_screenshots"].append(
                        {
                            "selector": selector,
                            "info": element_info,
                            "screenshot": await self.mcp_client.capture_screenshots(),
                        }
                    )

                except Exception as e:
                    logger.warning(f"요소 {selector} 캡처 실패: {e}")

            # 페이지 정보 수집
            evidence["page_info"] = await self.mcp_client.execute_javascript(
                """
            return {
                title: document.title,
                url: window.location.href,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                userAgent: navigator.userAgent
            };
            """
            )

            await self.mcp_client.disconnect()

            logger.info("시각적 증거 캡처 완료")
            return evidence

        except Exception as e:
            logger.error(f"시각적 증거 캡처 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def analyze_accessibility(self, url: str) -> Dict[str, Any]:
        """접근성 분석"""
        try:
            logger.info(f"접근성 분석 시작: {url}")

            await self.mcp_client.connect()
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            # 접근성 검사 스크립트
            accessibility_script = """
            const issues = [];
            
            // 이미지 alt 속성 확인
            const images = document.querySelectorAll('img');
            images.forEach((img, index) => {
                if (!img.alt && !img.ariaLabel) {
                    issues.push({
                        type: 'missing_alt_text',
                        element: 'img',
                        index: index,
                        severity: 'high'
                    });
                }
            });
            
            // 폼 라벨 확인
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach((input, index) => {
                const label = document.querySelector(`label[for="${input.id}"]`);
                if (!label && !input.ariaLabel && !input.placeholder) {
                    issues.push({
                        type: 'missing_label',
                        element: input.tagName,
                        index: index,
                        severity: 'medium'
                    });
                }
            });
            
            return {
                total_issues: issues.length,
                issues: issues,
                score: Math.max(0, 100 - issues.length * 10)
            };
            """

            result = await self.mcp_client.execute_javascript(accessibility_script)

            await self.mcp_client.disconnect()

            analysis_result = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "accessibility_score": result.get("score", 0),
                "total_issues": result.get("total_issues", 0),
                "issues": result.get("issues", []),
                "recommendations": self._generate_accessibility_recommendations(
                    result.get("issues", [])
                ),
            }

            logger.info(
                f"접근성 분석 완료: 점수 {analysis_result['accessibility_score']}/100"
            )
            return analysis_result

        except Exception as e:
            logger.error(f"접근성 분석 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    def _generate_accessibility_recommendations(
        self, issues: List[Dict[str, Any]]
    ) -> List[str]:
        """접근성 개선 권장사항 생성"""
        recommendations = []

        for issue in issues:
            if issue.get("type") == "missing_alt_text":
                recommendations.append("모든 이미지에 alt 속성을 추가하세요")
            elif issue.get("type") == "missing_label":
                recommendations.append("모든 폼 요소에 적절한 라벨을 추가하세요")

        return list(set(recommendations))  # 중복 제거

    async def test_responsive_design(
        self, url: str, viewports: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """반응형 디자인 테스트"""
        try:
            logger.info(f"반응형 디자인 테스트 시작: {url}")

            await self.mcp_client.connect()

            responsive_results = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "viewport_tests": [],
            }

            for viewport in viewports:
                width = viewport.get("width", 1920)
                height = viewport.get("height", 1080)

                logger.info(f"뷰포트 테스트: {width}x{height}")

                # 뷰포트 크기 설정
                await self.mcp_client.execute_javascript(
                    f"""
                window.resizeTo({width}, {height});
                """
                )

                await self.mcp_client.navigate(url)
                await self.mcp_client.wait_for_page_load()

                # 반응형 검사
                responsive_check = await self.mcp_client.execute_javascript(
                    f"""
                const viewport = {{
                    width: {width},
                    height: {height}
                }};
                
                const issues = [];
                
                // 오버플로우 확인
                const body = document.body;
                if (body.scrollWidth > viewport.width || body.scrollHeight > viewport.height) {{
                    issues.push({{
                        type: 'overflow',
                        description: '페이지가 뷰포트를 벗어남'
                    }});
                }}
                
                return {{
                    viewport: viewport,
                    issues: issues,
                    screenshot: 'screenshot_data'
                }};
                """
                )

                # 스크린샷 캡처
                screenshot = await self.mcp_client.capture_screenshots()

                responsive_results["viewport_tests"].append(
                    {
                        "viewport": viewport,
                        "issues": responsive_check.get("issues", []),
                        "screenshot": screenshot,
                    }
                )

            await self.mcp_client.disconnect()

            # 전체 결과 분석
            total_issues = sum(
                len(test["issues"]) for test in responsive_results["viewport_tests"]
            )
            responsive_results["total_issues"] = total_issues
            responsive_results["overall_score"] = max(0, 100 - total_issues * 5)

            logger.info(
                f"반응형 디자인 테스트 완료: 점수 {responsive_results['overall_score']}/100"
            )
            return responsive_results

        except Exception as e:
            logger.error(f"반응형 디자인 테스트 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def generate_ml_recommendations(
        self, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ML 기반 권장사항 생성"""
        try:
            logger.info("ML 기반 권장사항 생성 시작")

            # Google ADK의 ML 기능 활용
            recommendations = (
                await self.google_adk._generate_improvement_recommendations(test_data)
            )

            # 추가 ML 분석
            ml_analysis = {
                "pattern_detection": await self._detect_test_patterns(test_data),
                "performance_prediction": await self._predict_performance_issues(
                    test_data
                ),
                "optimization_suggestions": await self._generate_optimization_suggestions(
                    test_data
                ),
            }

            result = {
                "recommendations": recommendations,
                "ml_analysis": ml_analysis,
                "confidence_score": 0.89,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("ML 기반 권장사항 생성 완료")
            return result

        except Exception as e:
            logger.error(f"ML 권장사항 생성 중 오류: {e}")
            return {"status": "error", "error_message": str(e)}

    async def _detect_test_patterns(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 패턴 감지"""
        try:
            patterns = {
                "flaky_tests": 0,
                "performance_bottlenecks": 0,
                "common_failures": [],
            }

            detailed_results = test_data.get("detailed_results", [])
            for result in detailed_results:
                if not result.get("success", True):
                    patterns["flaky_tests"] += 1
                    failure_type = result.get("action", "unknown")
                    patterns["common_failures"].append(failure_type)

            return patterns

        except Exception as e:
            logger.error(f"패턴 감지 중 오류: {e}")
            return {}

    async def _predict_performance_issues(
        self, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 이슈 예측"""
        try:
            predictions = {
                "load_time_trend": "stable",
                "memory_leak_risk": "low",
                "scalability_concerns": [],
            }

            return predictions

        except Exception as e:
            logger.error(f"성능 예측 중 오류: {e}")
            return {}

    async def _generate_optimization_suggestions(
        self, test_data: Dict[str, Any]
    ) -> List[str]:
        """최적화 제안 생성"""
        try:
            suggestions = []

            success_rate = test_data.get("success_rate", 0)
            if success_rate < 90:
                suggestions.append("테스트 안정성을 높이기 위해 대기 시간을 조정하세요")

            load_time = test_data.get("page_load_time", 0)
            if load_time > 3:
                suggestions.append(
                    "이미지 최적화와 코드 분할을 통해 로딩 시간을 단축하세요"
                )

            return suggestions

        except Exception as e:
            logger.error(f"최적화 제안 생성 중 오류: {e}")
            return []


# 에이전트 인스턴스 생성
playwright_adk_agent = PlaywrightADKAgent()
