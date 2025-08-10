#!/usr/bin/env python3
"""
Google ADK 표준 방식 Playwright MCP 연계 애플리케이션
자연어로 웹 브라우저를 제어하는 FastAPI 서버
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

from multi_tool_agent.playwright_adk_agent_google_standard import PlaywrightADKAgentGoogleStandard
from utils.logger import setup_logger

# 로깅 설정
logger = setup_logger(__name__)

class NaturalLanguageTestRequest(BaseModel):
    """자연어 테스트 요청 모델"""
    request: str
    user_id: Optional[str] = "default_user"

class URLTestRequest(BaseModel):
    """URL 기반 테스트 요청 모델"""
    url: str
    test_type: str  # "quality", "accessibility", "responsive", "comprehensive"
    user_id: Optional[str] = "default_user"

class TestResult(BaseModel):
    """테스트 결과 모델"""
    test_id: str
    status: str
    execution_time: float
    events_count: int
    timestamp: str
    request: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class PlaywrightADKAppGoogleStandard:
    """Google ADK 표준 방식 Playwright MCP 애플리케이션"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Google ADK 표준 방식 Playwright MCP QA 시스템",
            description="자연어로 웹 브라우저를 제어하는 QA 시스템",
            version="2.0.0"
        )
        self.agents = {}  # 사용자별 에이전트 저장
        self.test_results = []
        
        # CORS 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 라우터 설정
        self._setup_routes()
    
    def _setup_routes(self):
        """API 라우터 설정"""
        
        @self.app.get("/")
        async def root():
            """루트 엔드포인트"""
            return {
                "message": "Google ADK 표준 방식 Playwright MCP QA 시스템",
                "version": "2.0.0",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health_check():
            """헬스 체크"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agents_count": len(self.agents)
            }
        
        @self.app.post("/test/natural-language", response_model=TestResult)
        async def run_natural_language_test(request: NaturalLanguageTestRequest):
            """자연어 테스트 실행"""
            try:
                # 사용자별 에이전트 생성 또는 재사용
                if request.user_id not in self.agents:
                    self.agents[request.user_id] = PlaywrightADKAgentGoogleStandard()
                    logger.info(f"새로운 에이전트 생성: {request.user_id}")
                
                agent = self.agents[request.user_id]
                
                # 백그라운드에서 테스트 실행
                result = await agent.run_web_test_natural_language(request.request)
                
                # 결과 저장
                self.test_results.append(result)
                
                return TestResult(
                    test_id=result["test_id"],
                    status=result["status"],
                    execution_time=result["execution_time"],
                    events_count=result["events_count"],
                    timestamp=result["timestamp"],
                    request=result["request"],
                    error=result.get("error")
                )
                
            except Exception as e:
                logger.error(f"자연어 테스트 실행 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test/quality", response_model=TestResult)
        async def run_quality_analysis(request: URLTestRequest):
            """품질 분석 테스트"""
            try:
                if request.user_id not in self.agents:
                    self.agents[request.user_id] = PlaywrightADKAgentGoogleStandard()
                
                agent = self.agents[request.user_id]
                
                result = await agent.analyze_webpage_quality_natural_language(request.url)
                
                self.test_results.append(result)
                
                return TestResult(
                    test_id=result["test_id"],
                    status=result["status"],
                    execution_time=result["execution_time"],
                    events_count=result["events_count"],
                    timestamp=result["timestamp"],
                    url=request.url,
                    error=result.get("error")
                )
                
            except Exception as e:
                logger.error(f"품질 분석 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test/accessibility", response_model=TestResult)
        async def run_accessibility_test(request: URLTestRequest):
            """접근성 테스트"""
            try:
                if request.user_id not in self.agents:
                    self.agents[request.user_id] = PlaywrightADKAgentGoogleStandard()
                
                agent = self.agents[request.user_id]
                
                result = await agent.perform_accessibility_test(request.url)
                
                self.test_results.append(result)
                
                return TestResult(
                    test_id=result["test_id"],
                    status=result["status"],
                    execution_time=result["execution_time"],
                    events_count=result["events_count"],
                    timestamp=result["timestamp"],
                    url=request.url,
                    error=result.get("error")
                )
                
            except Exception as e:
                logger.error(f"접근성 테스트 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test/responsive", response_model=TestResult)
        async def run_responsive_test(request: URLTestRequest):
            """반응형 디자인 테스트"""
            try:
                if request.user_id not in self.agents:
                    self.agents[request.user_id] = PlaywrightADKAgentGoogleStandard()
                
                agent = self.agents[request.user_id]
                
                result = await agent.test_responsive_design(request.url)
                
                self.test_results.append(result)
                
                return TestResult(
                    test_id=result["test_id"],
                    status=result["status"],
                    execution_time=result["execution_time"],
                    events_count=result["events_count"],
                    timestamp=result["timestamp"],
                    url=request.url,
                    error=result.get("error")
                )
                
            except Exception as e:
                logger.error(f"반응형 디자인 테스트 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test/comprehensive", response_model=TestResult)
        async def run_comprehensive_test(request: URLTestRequest):
            """종합 테스트"""
            try:
                if request.user_id not in self.agents:
                    self.agents[request.user_id] = PlaywrightADKAgentGoogleStandard()
                
                agent = self.agents[request.user_id]
                
                result = await agent.run_comprehensive_test(request.url)
                
                self.test_results.append(result)
                
                return TestResult(
                    test_id=result["test_id"],
                    status=result["status"],
                    execution_time=result["execution_time"],
                    events_count=result["events_count"],
                    timestamp=result["timestamp"],
                    url=request.url,
                    error=result.get("error")
                )
                
            except Exception as e:
                logger.error(f"종합 테스트 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/results")
        async def get_test_results(limit: int = 10):
            """테스트 결과 조회"""
            return {
                "total_results": len(self.test_results),
                "recent_results": self.test_results[-limit:] if self.test_results else []
            }
        
        @self.app.get("/results/{test_id}")
        async def get_test_result(test_id: str):
            """특정 테스트 결과 조회"""
            for result in self.test_results:
                if result["test_id"] == test_id:
                    return result
            raise HTTPException(status_code=404, detail="Test result not found")
        
        @self.app.delete("/agents/{user_id}")
        async def cleanup_agent(user_id: str):
            """사용자 에이전트 정리"""
            try:
                if user_id in self.agents:
                    await self.agents[user_id].close()
                    del self.agents[user_id]
                    logger.info(f"에이전트 정리 완료: {user_id}")
                    return {"message": f"Agent for user {user_id} cleaned up"}
                else:
                    return {"message": f"No agent found for user {user_id}"}
            except Exception as e:
                logger.error(f"에이전트 정리 실패: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents")
        async def get_agents():
            """활성 에이전트 목록 조회"""
            return {
                "active_agents": list(self.agents.keys()),
                "agents_count": len(self.agents)
            }

def create_app():
    """애플리케이션 생성"""
    return PlaywrightADKAppGoogleStandard().app

# 직접 실행용
if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # 기존 앱과 다른 포트 사용
        log_level="info"
    ) 