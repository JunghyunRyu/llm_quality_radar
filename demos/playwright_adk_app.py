#!/usr/bin/env python3
"""
Google ADK와 Playwright MCP 연계 애플리케이션
웹 자동화 테스트와 AI 기반 품질 분석을 결합한 혁신적인 시스템
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from multi_tool_agent.playwright_adk_agent import PlaywrightADKAgent
from utils.logger import setup_logger

# 로깅 설정
logger = setup_logger(__name__)


class WebTestRequest(BaseModel):
    """웹 테스트 요청 모델"""

    url: str
    test_scenarios: List[Dict[str, Any]]
    auto_healing: bool = True
    quality_analysis: bool = True
    performance_monitoring: bool = False
    accessibility_testing: bool = False
    responsive_testing: bool = False


class QualityAnalysisRequest(BaseModel):
    """품질 분석 요청 모델"""

    url: str
    include_ai_analysis: bool = True
    include_ml_recommendations: bool = True


class TestResult(BaseModel):
    """테스트 결과 모델"""

    test_id: str
    url: str
    status: str
    execution_time: float
    success_rate: float
    screenshots: List[str]
    logs: List[str]
    quality_score: Optional[float]
    recommendations: List[str]


class PlaywrightADKApp:
    """Google ADK와 Playwright MCP 연계 애플리케이션"""

    def __init__(self):
        self.agent = PlaywrightADKAgent()
        self.test_status = {}  # 테스트 상태 추적

        # FastAPI 앱 초기화
        self.app = FastAPI(
            title="Playwright ADK 연계 시스템",
            description="Google ADK와 Playwright MCP를 연계한 웹 자동화 테스트 및 AI 기반 품질 분석 시스템",
            version="1.0.0",
        )
        self._setup_routes()
        self._setup_middleware()

    def _setup_middleware(self):
        """미들웨어 설정"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """API 라우트 설정"""

        @self.app.get("/")
        async def root():
            return {
                "message": "Google ADK와 Playwright MCP 연계 시스템이 실행 중입니다",
                "version": "1.0.0",
                "features": [
                    "웹 자동화 테스트",
                    "AI 기반 품질 분석",
                    "성능 모니터링",
                    "접근성 테스트",
                    "반응형 디자인 테스트",
                    "ML 기반 권장사항",
                    "자동 복구 시스템",
                ],
            }

        @self.app.post("/test/web", response_model=TestResult)
        async def run_web_test(
            request: WebTestRequest, background_tasks: BackgroundTasks
        ):
            """웹 테스트 실행"""
            try:
                test_id = f"web_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # 초기 테스트 상태 설정
                self.test_status[test_id] = {
                    "test_id": test_id,
                    "url": request.url,
                    "status": "started",
                    "current_step": "테스트 초기화 중",
                    "progress": 0,
                    "start_time": datetime.now().isoformat(),
                    "total_scenarios": len(request.test_scenarios),
                    "completed_scenarios": 0,
                    "current_scenario": None,
                }

                # 백그라운드에서 테스트 실행
                background_tasks.add_task(self._execute_web_test, test_id, request)

                return TestResult(
                    test_id=test_id,
                    url=request.url,
                    status="started",
                    execution_time=0.0,
                    success_rate=0.0,
                    screenshots=[],
                    logs=[],
                    quality_score=None,
                    recommendations=[],
                )

            except Exception as e:
                logger.error(f"웹 테스트 실행 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/analyze/quality")
        async def analyze_webpage_quality(request: QualityAnalysisRequest):
            """웹페이지 품질 분석"""
            try:
                logger.info(f"품질 분석 시작: {request.url}")

                # 품질 분석 실행
                quality_result = await self.agent.analyze_webpage_quality(request.url)

                # AI 강화 분석 (요청된 경우)
                ai_analysis = None
                if request.include_ai_analysis:
                    ai_analysis = await self.agent.perform_ai_enhanced_analysis(
                        quality_result
                    )

                # ML 권장사항 (요청된 경우)
                ml_recommendations = None
                if request.include_ml_recommendations:
                    ml_recommendations = await self.agent.generate_ml_recommendations(
                        quality_result
                    )

                return {
                    "url": request.url,
                    "timestamp": datetime.now().isoformat(),
                    "quality_analysis": quality_result,
                    "ai_analysis": ai_analysis,
                    "ml_recommendations": ml_recommendations,
                }

            except Exception as e:
                logger.error(f"품질 분석 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/accessibility")
        async def test_accessibility(url: str):
            """접근성 테스트"""
            try:
                logger.info(f"접근성 테스트 시작: {url}")

                accessibility_result = await self.agent.analyze_accessibility(url)

                return {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "accessibility_result": accessibility_result,
                }

            except Exception as e:
                logger.error(f"접근성 테스트 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/responsive")
        async def test_responsive_design(url: str, viewports: List[Dict[str, int]]):
            """반응형 디자인 테스트"""
            try:
                logger.info(f"반응형 디자인 테스트 시작: {url}")

                responsive_result = await self.agent.test_responsive_design(
                    url, viewports
                )

                return {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "responsive_result": responsive_result,
                }

            except Exception as e:
                logger.error(f"반응형 디자인 테스트 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/monitor/performance")
        async def monitor_performance(url: str, duration: int = 60):
            """성능 모니터링"""
            try:
                logger.info(f"성능 모니터링 시작: {url} ({duration}초)")

                performance_result = await self.agent.monitor_web_performance(
                    url, duration
                )

                return {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "performance_result": performance_result,
                }

            except Exception as e:
                logger.error(f"성능 모니터링 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/capture/evidence")
        async def capture_visual_evidence(url: str, elements: List[str]):
            """시각적 증거 캡처"""
            try:
                logger.info(f"시각적 증거 캡처 시작: {url}")

                evidence_result = await self.agent.capture_visual_evidence(
                    url, elements
                )

                return {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "evidence_result": evidence_result,
                }

            except Exception as e:
                logger.error(f"시각적 증거 캡처 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/heal/issues")
        async def auto_heal_issues(error_context: Dict[str, Any]):
            """자동 복구"""
            try:
                logger.info("자동 복구 시작")

                healing_result = await self.agent.auto_heal_test_issues(error_context)

                return {
                    "timestamp": datetime.now().isoformat(),
                    "healing_result": healing_result,
                }

            except Exception as e:
                logger.error(f"자동 복구 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/report/{test_id}")
        async def get_test_report(test_id: str):
            """테스트 리포트 조회"""
            try:
                # 현재 테스트 상태 확인
                if test_id in self.test_status:
                    current_status = self.test_status[test_id]

                    # 테스트가 진행 중인 경우
                    if current_status["status"] in ["started", "running"]:
                        return {
                            "test_id": test_id,
                            "url": current_status["url"],
                            "status": current_status["status"],
                            "current_step": current_status["current_step"],
                            "progress": current_status["progress"],
                            "total_scenarios": current_status["total_scenarios"],
                            "completed_scenarios": current_status[
                                "completed_scenarios"
                            ],
                            "current_scenario": current_status["current_scenario"],
                            "start_time": current_status["start_time"],
                        }
                    elif current_status["status"] == "completed":
                        # 완료된 테스트는 test_status에서 제거하고 리포트 반환
                        del self.test_status[test_id]
                        report = await self.agent.generate_test_report(test_id)
                        return report
                    elif current_status["status"] == "error":
                        # 오류가 발생한 테스트는 test_status에서 제거
                        error_info = current_status.get(
                            "error_message", "Unknown error"
                        )
                        del self.test_status[test_id]
                        return {
                            "test_id": test_id,
                            "status": "error",
                            "error_message": error_info,
                        }

                # test_status에 없는 경우 에이전트에서 리포트 생성 시도
                report = await self.agent.generate_test_report(test_id)
                return report

            except Exception as e:
                logger.error(f"테스트 리포트 조회 중 오류: {e}")
                raise HTTPException(
                    status_code=404, detail="테스트 리포트를 찾을 수 없습니다"
                )

        @self.app.get("/status")
        async def get_system_status():
            """시스템 상태 조회"""
            try:
                return {
                    "status": "running",
                    "timestamp": datetime.now().isoformat(),
                    "agent_status": "active",
                    "mcp_client_status": (
                        "connected"
                        if self.agent.mcp_client.connected
                        else "disconnected"
                    ),
                    "google_adk_status": self.agent.google_adk.get_adk_status(),
                }

            except Exception as e:
                logger.error(f"시스템 상태 조회 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/initialize")
        async def initialize_system():
            """시스템 초기화"""
            try:
                logger.info("시스템 초기화 시작")

                # Google ADK 초기화
                await self.agent.google_adk.initialize_adk()

                return {
                    "message": "시스템 초기화 완료",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                }

            except Exception as e:
                logger.error(f"시스템 초기화 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def _execute_web_test(self, test_id: str, request: WebTestRequest):
        """웹 테스트 실행 로직"""
        start_time = datetime.now()

        try:
            logger.info(f"웹 테스트 {test_id} 시작: {request.url}")

            # 테스트 상태 업데이트
            if test_id in self.test_status:
                self.test_status[test_id].update(
                    {
                        "status": "running",
                        "current_step": "웹 테스트 실행 중",
                        "progress": 10,
                    }
                )

            # 1. 기본 웹 테스트 실행
            test_result = await self.agent.run_web_test(
                request.url, request.test_scenarios
            )

            # 2. 품질 분석 (요청된 경우)
            quality_result = None
            if request.quality_analysis:
                if test_id in self.test_status:
                    self.test_status[test_id].update(
                        {"current_step": "품질 분석 중", "progress": 30}
                    )
                quality_result = await self.agent.analyze_webpage_quality(request.url)

            # 3. 성능 모니터링 (요청된 경우)
            performance_result = None
            if request.performance_monitoring:
                if test_id in self.test_status:
                    self.test_status[test_id].update(
                        {"current_step": "성능 모니터링 중", "progress": 50}
                    )
                performance_result = await self.agent.monitor_web_performance(
                    request.url, 60
                )

            # 4. 접근성 테스트 (요청된 경우)
            accessibility_result = None
            if request.accessibility_testing:
                if test_id in self.test_status:
                    self.test_status[test_id].update(
                        {"current_step": "접근성 테스트 중", "progress": 60}
                    )
                accessibility_result = await self.agent.analyze_accessibility(
                    request.url
                )

            # 5. 반응형 테스트 (요청된 경우)
            responsive_result = None
            if request.responsive_testing:
                if test_id in self.test_status:
                    self.test_status[test_id].update(
                        {"current_step": "반응형 테스트 중", "progress": 70}
                    )
                default_viewports = [
                    {"width": 1920, "height": 1080},  # 데스크톱
                    {"width": 768, "height": 1024},  # 태블릿
                    {"width": 375, "height": 667},  # 모바일
                ]
                responsive_result = await self.agent.test_responsive_design(
                    request.url, default_viewports
                )

            # 6. 자동 복구 (요청된 경우)
            healing_actions = []
            if request.auto_healing and test_result.get("failure_count", 0) > 0:
                if test_id in self.test_status:
                    self.test_status[test_id].update(
                        {"current_step": "자동 복구 중", "progress": 80}
                    )
                # 실패한 테스트에 대한 자동 복구 시도
                for result in test_result.get("detailed_results", []):
                    if not result.get("success", True):
                        error_context = {
                            "action": result.get("action"),
                            "selector": result.get("selector"),
                            "error": result.get("error"),
                            "url": request.url,
                        }
                        healing_result = await self.agent.auto_heal_test_issues(
                            error_context
                        )
                        healing_actions.append(healing_result)

            # 7. 결과 통합
            execution_time = (datetime.now() - start_time).total_seconds()

            # 테스트 완료 상태 업데이트
            if test_id in self.test_status:
                self.test_status[test_id].update(
                    {
                        "status": "completed",
                        "current_step": "테스트 완료",
                        "progress": 100,
                        "completed_scenarios": test_result.get("total_scenarios", 0),
                    }
                )

            final_result = {
                "test_id": test_id,
                "url": request.url,
                "status": "completed",
                "execution_time": execution_time,
                "success_rate": test_result.get("success_rate", 0),
                "screenshots": test_result.get("screenshots", []),
                "logs": test_result.get("logs", []),
                "quality_score": (
                    quality_result.get("quality_score") if quality_result else None
                ),
                "recommendations": self._combine_recommendations(
                    test_result, quality_result, accessibility_result, responsive_result
                ),
                "detailed_results": {
                    "test_result": test_result,
                    "quality_result": quality_result,
                    "performance_result": performance_result,
                    "accessibility_result": accessibility_result,
                    "responsive_result": responsive_result,
                    "healing_actions": healing_actions,
                },
            }

            # 결과 저장
            self.agent.test_results.append(final_result)

            logger.info(f"웹 테스트 {test_id} 완료: {execution_time:.2f}초")

        except Exception as e:
            logger.error(f"웹 테스트 {test_id} 실행 중 오류: {e}")

            # 테스트 상태를 오류로 업데이트
            if test_id in self.test_status:
                self.test_status[test_id].update(
                    {
                        "status": "error",
                        "current_step": "테스트 오류",
                        "error_message": str(e),
                    }
                )

            error_result = {
                "test_id": test_id,
                "url": request.url,
                "status": "error",
                "error_message": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
            }
            self.agent.test_results.append(error_result)

    def _combine_recommendations(self, *results) -> List[str]:
        """여러 결과에서 권장사항 통합"""
        recommendations = []

        for result in results:
            if result and isinstance(result, dict):
                # 테스트 결과에서 권장사항
                if "recommendations" in result:
                    recommendations.extend(result["recommendations"])

                # 품질 분석 결과에서 권장사항
                if "quality_score" in result and result.get("quality_score", 100) < 80:
                    recommendations.append("전반적인 웹페이지 품질을 개선하세요")

                # 접근성 결과에서 권장사항
                if (
                    "accessibility_score" in result
                    and result.get("accessibility_score", 100) < 80
                ):
                    recommendations.append("접근성을 개선하세요")

                # 반응형 결과에서 권장사항
                if "overall_score" in result and result.get("overall_score", 100) < 80:
                    recommendations.append("반응형 디자인을 개선하세요")

        return list(set(recommendations))  # 중복 제거

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """서버 실행"""
        logger.info(f"Playwright ADK 연계 시스템 시작: http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """메인 함수"""
    try:
        app = PlaywrightADKApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("서버가 중단되었습니다")
    except Exception as e:
        logger.error(f"서버 실행 중 오류: {e}")


if __name__ == "__main__":
    main()
