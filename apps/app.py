#!/usr/bin/env python3
"""
자동 QA 품질 개선 프로그램
Playwright MCP를 활용한 혁신적인 웹 자동화 테스트 시스템
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.auto_healing import AutoHealingSystem
from core.mcp_client import PlaywrightMCPClient
from core.quality_monitor import QualityMonitor
from core.operational_manager import OperationalManager
from core.google_adk_integration import GoogleADKIntegration
from utils.config import Config
from utils.logger import setup_logger

# 로깅 설정
logger = setup_logger(__name__)

class TestRequest(BaseModel):
    """테스트 요청 모델"""
    url: str
    test_scenarios: List[Dict[str, Any]]
    auto_healing: bool = True
    quality_checks: bool = True
    monitoring: bool = True

class TestResult(BaseModel):
    """테스트 결과 모델"""
    test_id: str
    status: str
    execution_time: float
    screenshots: List[str]
    logs: List[str]
    quality_score: float
    healing_actions: List[str]

class QAQualityRadar:
    """자동 QA 품질 개선 시스템 메인 클래스"""
    
    def __init__(self):
        self.config = Config()
        self.mcp_client = PlaywrightMCPClient()
        self.auto_healing = AutoHealingSystem()
        self.quality_monitor = QualityMonitor()
        self.operational_manager = OperationalManager()
        self.google_adk = GoogleADKIntegration()
        
        # FastAPI 앱 초기화
        self.app = FastAPI(
            title="QA Quality Radar",
            description="Playwright MCP 기반 자동 QA 품질 개선 시스템",
            version="1.0.0"
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
                "message": "QA Quality Radar 시스템이 실행 중입니다",
                "version": "1.0.0",
                "features": [
                    "Auto Healing System",
                    "MCP 기반 정보 취득",
                    "A2A/ADK 운영 관리",
                    "Google ADK 통합",
                    "분산 테스트 실행",
                    "AI 강화 분석",
                    "ML 기반 자동 복구"
                ]
            }
        
        @self.app.post("/test", response_model=TestResult)
        async def run_test(request: TestRequest, background_tasks: BackgroundTasks):
            """테스트 실행 엔드포인트"""
            try:
                test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 백그라운드에서 테스트 실행
                background_tasks.add_task(
                    self._execute_test,
                    test_id,
                    request
                )
                
                return TestResult(
                    test_id=test_id,
                    status="started",
                    execution_time=0.0,
                    screenshots=[],
                    logs=[],
                    quality_score=0.0,
                    healing_actions=[]
                )
                
            except Exception as e:
                logger.error(f"테스트 실행 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/test/{test_id}")
        async def get_test_status(test_id: str):
            """테스트 상태 조회"""
            try:
                status = await self.operational_manager.get_test_status(test_id)
                return status
            except Exception as e:
                logger.error(f"테스트 상태 조회 중 오류: {e}")
                raise HTTPException(status_code=404, detail="테스트를 찾을 수 없습니다")
        
        @self.app.get("/dashboard")
        async def get_dashboard():
            """대시보드 데이터 조회"""
            try:
                dashboard_data = await self.operational_manager.get_dashboard_data()
                return dashboard_data
            except Exception as e:
                logger.error(f"대시보드 데이터 조회 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/adk/status")
        async def get_adk_status():
            """Google ADK 상태 조회"""
            try:
                adk_status = self.google_adk.get_adk_status()
                return adk_status
            except Exception as e:
                logger.error(f"ADK 상태 조회 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/adk/initialize")
        async def initialize_adk():
            """Google ADK 초기화"""
            try:
                await self.google_adk.initialize_adk()
                return {"message": "Google ADK 초기화 완료", "status": "success"}
            except Exception as e:
                logger.error(f"ADK 초기화 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test/distributed")
        async def run_distributed_test(request: TestRequest, background_tasks: BackgroundTasks):
            """분산 테스트 실행"""
            try:
                test_id = f"distributed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 백그라운드에서 분산 테스트 실행
                background_tasks.add_task(
                    self._execute_distributed_test,
                    test_id,
                    request
                )
                
                return {
                    "test_id": test_id,
                    "status": "started",
                    "type": "distributed",
                    "message": "분산 테스트가 시작되었습니다"
                }
                
            except Exception as e:
                logger.error(f"분산 테스트 실행 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/analysis/ai-enhanced")
        async def ai_enhanced_analysis(request: TestRequest):
            """AI 강화 분석"""
            try:
                test_data = {
                    "url": request.url,
                    "scenarios": request.test_scenarios,
                    "timestamp": datetime.now().isoformat()
                }
                
                analysis_result = await self.google_adk.ai_enhanced_quality_analysis(test_data)
                return analysis_result
                
            except Exception as e:
                logger.error(f"AI 강화 분석 중 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _execute_test(self, test_id: str, request: TestRequest):
        """실제 테스트 실행 로직"""
        start_time = datetime.now()
        
        try:
            logger.info(f"테스트 {test_id} 시작: {request.url}")
            
            # 1. MCP 클라이언트를 통한 브라우저 제어
            await self.mcp_client.connect()
            
            # 2. 페이지 로드
            await self.mcp_client.navigate(request.url)
            
            # 3. Auto Healing System 활성화
            if request.auto_healing:
                await self.auto_healing.enable()
            
            # 4. 테스트 시나리오 실행
            test_results = []
            for scenario in request.test_scenarios:
                result = await self._execute_scenario(scenario)
                test_results.append(result)
            
            # 5. 품질 모니터링
            quality_score = 0.0
            if request.quality_checks:
                quality_score = await self.quality_monitor.assess_quality()
            
            # 6. 스크린샷 및 로그 수집
            screenshots = await self.mcp_client.capture_screenshots()
            logs = await self.mcp_client.get_logs()
            
            # 7. 결과 저장
            execution_time = (datetime.now() - start_time).total_seconds()
            
            test_result = TestResult(
                test_id=test_id,
                status="completed",
                execution_time=execution_time,
                screenshots=screenshots,
                logs=logs,
                quality_score=quality_score,
                healing_actions=self.auto_healing.get_healing_actions()
            )
            
            await self.operational_manager.save_test_result(test_result)
            
            logger.info(f"테스트 {test_id} 완료: {execution_time:.2f}초")
            
        except Exception as e:
            logger.error(f"테스트 {test_id} 실행 중 오류: {e}")
            await self.operational_manager.save_test_error(test_id, str(e))
        
        finally:
            await self.mcp_client.disconnect()
    
    async def _execute_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """개별 테스트 시나리오 실행"""
        try:
            action = scenario.get("action")
            selector = scenario.get("selector")
            value = scenario.get("value")
            
            if action == "click":
                await self.mcp_client.click(selector)
            elif action == "type":
                await self.mcp_client.type(selector, value)
            elif action == "wait":
                await self.mcp_client.wait_for_element(selector)
            elif action == "assert":
                result = await self.mcp_client.assert_element(selector, value)
                return {"action": action, "success": result}
            
            return {"action": action, "success": True}
            
        except Exception as e:
            logger.error(f"시나리오 실행 중 오류: {e}")
            return {"action": action, "success": False, "error": str(e)}
    
    async def _execute_distributed_test(self, test_id: str, request: TestRequest):
        """분산 테스트 실행 로직"""
        try:
            logger.info(f"분산 테스트 {test_id} 시작: {request.url}")
            
            # Google ADK를 통한 분산 테스트 실행
            test_config = {
                "url": request.url,
                "test_scenarios": request.test_scenarios,
                "auto_healing": request.auto_healing,
                "quality_checks": request.quality_checks
            }
            
            distributed_result = await self.google_adk.run_distributed_test(test_config)
            
            # 결과를 Cloud Storage에 업로드
            if self.google_adk.cloud_storage_client:
                storage_path = await self.google_adk.upload_to_cloud_storage(distributed_result)
                distributed_result["storage_path"] = storage_path
            
            # Cloud Monitoring에 메트릭 생성
            if self.google_adk.cloud_monitoring_client:
                await self.google_adk.create_cloud_monitoring_metric({
                    "metric_name": "distributed_test_quality_score",
                    "value": distributed_result.get("average_quality_score", 0),
                    "test_id": test_id
                })
            
            logger.info(f"분산 테스트 {test_id} 완료")
            
        except Exception as e:
            logger.error(f"분산 테스트 {test_id} 실행 중 오류: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """서버 실행"""
        logger.info(f"QA Quality Radar 서버 시작: http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """메인 함수"""
    try:
        radar = QAQualityRadar()
        radar.run()
    except KeyboardInterrupt:
        logger.info("서버가 중단되었습니다")
    except Exception as e:
        logger.error(f"서버 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
