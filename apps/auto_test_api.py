#!/usr/bin/env python3
"""
자동 테스트 스위트 API - FastAPI 기반 웹 인터페이스
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from apps.auto_test_suite_extension import AutoTestSuiteExtension
from utils.logger import setup_logger

logger = setup_logger(__name__)


# Pydantic 모델 정의
class AutoTestRequest(BaseModel):
    """자동 테스트 요청 모델"""

    url: str
    test_type: str = (
        "comprehensive"  # comprehensive, functional, accessibility, performance
    )
    include_monitoring: bool = True
    generate_scripts: bool = True


class TestResult(BaseModel):
    """테스트 결과 모델"""

    workflow_id: str
    url: str
    test_type: str
    status: str
    execution_time: float
    summary: Dict[str, Any]
    recommendations: List[str]
    generated_files: List[Dict[str, str]]


class AutoTestAPI:
    """자동 테스트 스위트 API"""

    def __init__(self):
        self.auto_suite = AutoTestSuiteExtension()
        self.active_workflows = {}  # 진행 중인 워크플로우 추적

        # FastAPI 앱 초기화
        self.app = FastAPI(
            title="자동 테스트 스위트 API",
            description="웹 페이지 분석부터 테스트 케이스 자동 생성, 스크립트 생성, 실행, 모니터링까지 종합적인 웹 자동화 테스트 도구",
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
                "message": "자동 테스트 스위트 API가 실행 중입니다",
                "version": "1.0.0",
                "features": [
                    "웹 페이지 자동 분석",
                    "테스트 케이스 자동 생성",
                    "Playwright 자동화 스크립트 생성",
                    "테스트 자동 실행",
                    "성능 모니터링 및 메트릭 측정",
                    "종합 리포트 생성",
                    "개선 권장사항 제공",
                ],
            }

        @self.app.post("/test/auto", response_model=TestResult)
        async def run_auto_test(
            request: AutoTestRequest, background_tasks: BackgroundTasks
        ):
            """자동 테스트 워크플로우 실행"""
            try:
                workflow_id = (
                    f"auto_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                # 초기 응답 반환
                initial_response = TestResult(
                    workflow_id=workflow_id,
                    url=request.url,
                    test_type=request.test_type,
                    status="started",
                    execution_time=0.0,
                    summary={},
                    recommendations=[],
                    generated_files=[],
                )

                # 백그라운드에서 워크플로우 실행
                background_tasks.add_task(
                    self._execute_workflow_background, workflow_id, request
                )

                return initial_response

            except Exception as e:
                logger.error(f"자동 테스트 시작 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/test/status/{workflow_id}")
        async def get_test_status(workflow_id: str):
            """테스트 워크플로우 상태 조회"""
            try:
                if workflow_id in self.active_workflows:
                    return self.active_workflows[workflow_id]
                else:
                    raise HTTPException(
                        status_code=404, detail="워크플로우를 찾을 수 없습니다"
                    )

            except Exception as e:
                logger.error(f"워크플로우 상태 조회 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/test/results/{workflow_id}")
        async def get_test_results(workflow_id: str):
            """테스트 결과 조회"""
            try:
                if workflow_id in self.active_workflows:
                    workflow_data = self.active_workflows[workflow_id]
                    if workflow_data.get("status") == "completed":
                        return workflow_data
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail="워크플로우가 아직 완료되지 않았습니다",
                        )
                else:
                    raise HTTPException(
                        status_code=404, detail="워크플로우를 찾을 수 없습니다"
                    )

            except Exception as e:
                logger.error(f"테스트 결과 조회 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/analyze")
        async def analyze_webpage_only(request: AutoTestRequest):
            """웹 페이지 분석만 수행"""
            try:
                logger.info(f"웹 페이지 분석 시작: {request.url}")

                # 웹 페이지 분석 수행
                page_analysis = await self.auto_suite._analyze_webpage_with_mcp(
                    request.url
                )

                return {
                    "status": "completed",
                    "url": request.url,
                    "analysis": page_analysis,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"웹 페이지 분석 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/generate-cases")
        async def generate_test_cases_only(request: AutoTestRequest):
            """테스트 케이스 생성만 수행"""
            try:
                logger.info(f"테스트 케이스 생성 시작: {request.url}")

                # 웹 페이지 분석
                page_analysis = await self.auto_suite._analyze_webpage_with_mcp(
                    request.url
                )

                # 테스트 케이스 생성
                test_cases = await self.auto_suite._generate_test_cases_from_analysis(
                    page_analysis, request.test_type
                )

                return {
                    "status": "completed",
                    "url": request.url,
                    "test_type": request.test_type,
                    "test_cases": test_cases,
                    "total_cases": len(test_cases),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"테스트 케이스 생성 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/generate-scripts")
        async def generate_scripts_only(request: AutoTestRequest):
            """자동화 스크립트 생성만 수행"""
            try:
                logger.info(f"자동화 스크립트 생성 시작: {request.url}")

                # 웹 페이지 분석
                page_analysis = await self.auto_suite._analyze_webpage_with_mcp(
                    request.url
                )

                # 테스트 케이스 생성
                test_cases = await self.auto_suite._generate_test_cases_from_analysis(
                    page_analysis, request.test_type
                )

                # 자동화 스크립트 생성
                automation_scripts = await self.auto_suite._generate_automation_scripts(
                    test_cases, page_analysis
                )

                return {
                    "status": "completed",
                    "url": request.url,
                    "test_type": request.test_type,
                    "test_cases": test_cases,
                    "automation_scripts": automation_scripts,
                    "total_scripts": len(automation_scripts),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"자동화 스크립트 생성 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/test/monitor")
        async def monitor_performance_only(request: AutoTestRequest):
            """성능 모니터링만 수행"""
            try:
                logger.info(f"성능 모니터링 시작: {request.url}")

                # 성능 모니터링 수행
                monitoring_results = (
                    await self.auto_suite._perform_monitoring_and_metrics(request.url)
                )

                return {
                    "status": "completed",
                    "url": request.url,
                    "monitoring_results": monitoring_results,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"성능 모니터링 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/test/list")
        async def list_workflows():
            """워크플로우 목록 조회"""
            try:
                workflows = []
                for workflow_id, workflow_data in self.active_workflows.items():
                    workflows.append(
                        {
                            "workflow_id": workflow_id,
                            "url": workflow_data.get("url"),
                            "test_type": workflow_data.get("test_type"),
                            "status": workflow_data.get("status"),
                            "start_time": workflow_data.get("start_time"),
                            "execution_time": workflow_data.get("execution_time", 0),
                        }
                    )

                return {"total_workflows": len(workflows), "workflows": workflows}

            except Exception as e:
                logger.error(f"워크플로우 목록 조회 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/test/clear")
        async def clear_workflows():
            """완료된 워크플로우 정리"""
            try:
                completed_workflows = []
                for workflow_id, workflow_data in list(self.active_workflows.items()):
                    if workflow_data.get("status") in ["completed", "failed"]:
                        completed_workflows.append(workflow_id)
                        del self.active_workflows[workflow_id]

                return {
                    "message": f"{len(completed_workflows)}개의 완료된 워크플로우가 정리되었습니다",
                    "cleared_workflows": completed_workflows,
                }

            except Exception as e:
                logger.error(f"워크플로우 정리 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def _execute_workflow_background(
        self, workflow_id: str, request: AutoTestRequest
    ):
        """백그라운드에서 워크플로우 실행"""
        try:
            start_time = datetime.now()

            # 워크플로우 상태 초기화
            self.active_workflows[workflow_id] = {
                "workflow_id": workflow_id,
                "url": request.url,
                "test_type": request.test_type,
                "status": "running",
                "start_time": start_time.isoformat(),
                "current_step": "워크플로우 시작",
                "progress": 0,
            }

            # 1단계: 웹 페이지 분석
            self.active_workflows[workflow_id].update(
                {"current_step": "웹 페이지 분석 중", "progress": 10}
            )
            page_analysis = await self.auto_suite._analyze_webpage_with_mcp(request.url)

            # 2단계: 테스트 케이스 생성
            self.active_workflows[workflow_id].update(
                {"current_step": "테스트 케이스 생성 중", "progress": 30}
            )
            test_cases = await self.auto_suite._generate_test_cases_from_analysis(
                page_analysis, request.test_type
            )

            # 3단계: 자동화 스크립트 생성
            self.active_workflows[workflow_id].update(
                {"current_step": "자동화 스크립트 생성 중", "progress": 50}
            )
            automation_scripts = await self.auto_suite._generate_automation_scripts(
                test_cases, page_analysis
            )

            # 4단계: 테스트 실행
            self.active_workflows[workflow_id].update(
                {"current_step": "테스트 실행 중", "progress": 70}
            )
            execution_results = await self.auto_suite._execute_generated_tests(
                test_cases, request.url
            )

            # 5단계: 성능 모니터링
            monitoring_results = {}
            if request.include_monitoring:
                self.active_workflows[workflow_id].update(
                    {"current_step": "성능 모니터링 중", "progress": 85}
                )
                monitoring_results = (
                    await self.auto_suite._perform_monitoring_and_metrics(request.url)
                )

            # 6단계: 종합 리포트 생성
            self.active_workflows[workflow_id].update(
                {"current_step": "종합 리포트 생성 중", "progress": 95}
            )
            final_report = await self.auto_suite._generate_comprehensive_report(
                page_analysis,
                test_cases,
                automation_scripts,
                execution_results,
                monitoring_results,
            )

            # 워크플로우 완료
            execution_time = (datetime.now() - start_time).total_seconds()

            self.active_workflows[workflow_id].update(
                {
                    "status": "completed",
                    "current_step": "완료",
                    "progress": 100,
                    "execution_time": execution_time,
                    "page_analysis": page_analysis,
                    "generated_test_cases": test_cases,
                    "automation_scripts": automation_scripts,
                    "execution_results": execution_results,
                    "monitoring_results": monitoring_results,
                    "final_report": final_report,
                    "completion_time": datetime.now().isoformat(),
                }
            )

            logger.info(f"워크플로우 {workflow_id} 완료: {execution_time:.2f}초")

        except Exception as e:
            logger.error(f"워크플로우 {workflow_id} 실패: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            self.active_workflows[workflow_id].update(
                {
                    "status": "failed",
                    "current_step": "오류 발생",
                    "progress": 0,
                    "execution_time": execution_time,
                    "error": str(e),
                    "completion_time": datetime.now().isoformat(),
                }
            )

    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """API 서버 실행"""
        uvicorn.run(self.app, host=host, port=port)


def main():
    """메인 함수"""
    api = AutoTestAPI()
    api.run()


if __name__ == "__main__":
    main()
