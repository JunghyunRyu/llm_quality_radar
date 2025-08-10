"""
Playwright MCP 클라이언트
MCP 서버와 통신하여 웹 브라우저를 제어하는 클라이언트
"""

import asyncio
import json
import logging
import subprocess
import time
import aiohttp
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PlaywrightMCPClient:
    """Playwright MCP 클라이언트"""
    
    def __init__(self):
        self.mcp_process = None
        self.connected = False
        self.browser_context = None
        self.current_page = None
        # 기본: 공식 @playwright/mcp (3001), 대체: simple MCP (8933)
        self.base_url = "http://localhost:3001"  # 환경에 따라 8933(simple) 사용 가능
        
        # MCP 설정
        self.mcp_config = {
            "server_path": "npx",
            "server_args": ["@playwright/mcp", "--port", "3001", "--headless"],
            "timeout": 30000,
            "headless": True
        }
    
    async def connect(self):
        """MCP 서버에 연결"""
        try:
            logger.info("Playwright MCP 서버에 연결 중...")
            
            # 이미 실행 중인 서버에 연결만 시도
            # 연결 확인
            await self._wait_for_connection()
            self.connected = True
            
            # 브라우저 컨텍스트 생성
            await self._create_browser_context()
            
            logger.info("Playwright MCP 서버 연결 성공")
            
        except Exception as e:
            logger.error(f"MCP 서버 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """MCP 서버 연결 해제"""
        try:
            if self.mcp_process:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            
            self.connected = False
            logger.info("Playwright MCP 서버 연결 해제")
            
        except Exception as e:
            logger.error(f"MCP 서버 연결 해제 중 오류: {e}")
    
    async def _wait_for_connection(self):
        """MCP 서버 연결 대기"""
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # MCP 서버 상태 확인 (ping 유사)
                request_data = {
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000),
                    "method": "ping",
                    "params": {}
                }
                async with aiohttp.ClientSession() as session:
                    # 공식 MCP (3001)
                    try:
                        async with session.post(
                            f"{self.base_url}/mcp",
                            json=request_data,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream"
                            },
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                return
                    except Exception:
                        # simple MCP(8933)로 폴백
                        async with session.get(
                            "http://localhost:8933/health",
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as health:
                            if health.status == 200:
                                self.base_url = "http://localhost:8933"
                                return
            except Exception:
                pass
            
            await asyncio.sleep(1)
        
        raise Exception("MCP 서버 연결 시간 초과")
    
    async def _create_browser_context(self):
        """브라우저 컨텍스트 생성"""
        try:
            # 새 탭 생성 (브라우저 컨텍스트 역할)
            response = await self._send_mcp_request("browser_tab_new", {})
            self.browser_context = response.get("tab_id")
            
            logger.info(f"브라우저 컨텍스트 생성: {self.browser_context}")
            
        except Exception as e:
            logger.error(f"브라우저 컨텍스트 생성 실패: {e}")
            raise
    
    async def navigate(self, url: str):
        """페이지 네비게이션"""
        try:
            # 페이지 스냅샷으로 현재 상태 확인
            await self._send_mcp_request("browser_snapshot", {})
            
            # 페이지 네비게이션
            await self._send_mcp_request("browser_navigate", {
                "url": url
            })
            
            logger.info(f"페이지 네비게이션 완료: {url}")
            
        except Exception as e:
            logger.error(f"페이지 네비게이션 실패: {e}")
            raise
    
    async def click(self, selector: str):
        """요소 클릭"""
        try:
            await self._send_mcp_request("click", {
                "page_id": self.current_page,
                "selector": selector
            })
            
            logger.info(f"요소 클릭 완료: {selector}")
            
        except Exception as e:
            logger.error(f"요소 클릭 실패: {e}")
            raise
    
    async def type(self, selector: str, text: str):
        """텍스트 입력"""
        try:
            await self._send_mcp_request("type", {
                "page_id": self.current_page,
                "selector": selector,
                "text": text
            })
            
            logger.info(f"텍스트 입력 완료: {selector} -> {text}")
            
        except Exception as e:
            logger.error(f"텍스트 입력 실패: {e}")
            raise
    
    async def wait_for_element(self, selector: str, timeout: int = 10):
        """요소 대기"""
        try:
            await self._send_mcp_request("wait_for_element", {
                "page_id": self.current_page,
                "selector": selector,
                "timeout": timeout * 1000  # 밀리초 단위
            })
            
            logger.info(f"요소 대기 완료: {selector}")
            
        except Exception as e:
            logger.error(f"요소 대기 실패: {e}")
            raise
    
    async def element_exists(self, selector: str) -> bool:
        """요소 존재 여부 확인"""
        try:
            response = await self._send_mcp_request("element_exists", {
                "page_id": self.current_page,
                "selector": selector
            })
            
            return response.get("exists", False)
            
        except Exception as e:
            logger.error(f"요소 존재 확인 실패: {e}")
            return False
    
    async def element_is_clickable(self, selector: str) -> bool:
        """요소 클릭 가능 여부 확인"""
        try:
            response = await self._send_mcp_request("element_is_clickable", {
                "page_id": self.current_page,
                "selector": selector
            })
            
            return response.get("clickable", False)
            
        except Exception as e:
            logger.error(f"요소 클릭 가능 확인 실패: {e}")
            return False
    
    async def wait_for_element_to_be_clickable(self, selector: str, timeout: int = 10):
        """요소가 클릭 가능할 때까지 대기"""
        try:
            await self._send_mcp_request("wait_for_element_to_be_clickable", {
                "page_id": self.current_page,
                "selector": selector,
                "timeout": timeout * 1000
            })
            
            logger.info(f"요소 클릭 가능 대기 완료: {selector}")
            
        except Exception as e:
            logger.error(f"요소 클릭 가능 대기 실패: {e}")
            raise
    
    async def scroll_to_element(self, selector: str):
        """요소로 스크롤"""
        try:
            await self._send_mcp_request("scroll_to_element", {
                "page_id": self.current_page,
                "selector": selector
            })
            
            logger.info(f"요소로 스크롤 완료: {selector}")
            
        except Exception as e:
            logger.error(f"요소로 스크롤 실패: {e}")
            raise
    
    async def execute_javascript(self, script: str):
        """JavaScript 실행"""
        try:
            response = await self._send_mcp_request("execute_javascript", {
                "page_id": self.current_page,
                "script": script
            })
            
            logger.info(f"JavaScript 실행 완료: {script[:50]}...")
            return response.get("result")
            
        except Exception as e:
            logger.error(f"JavaScript 실행 실패: {e}")
            raise
    
    async def refresh_page(self):
        """페이지 새로고침"""
        try:
            await self._send_mcp_request("refresh_page", {
                "page_id": self.current_page
            })
            
            logger.info("페이지 새로고침 완료")
            
        except Exception as e:
            logger.error(f"페이지 새로고침 실패: {e}")
            raise
    
    async def wait_for_page_load(self):
        """페이지 로드 대기"""
        try:
            await self._send_mcp_request("wait_for_page_load", {
                "page_id": self.current_page
            })
            
            logger.info("페이지 로드 대기 완료")
            
        except Exception as e:
            logger.error(f"페이지 로드 대기 실패: {e}")
            raise
    
    async def capture_screenshots(self) -> List[str]:
        """스크린샷 캡처"""
        try:
            timestamp = int(time.time())
            screenshot_path = f"screenshots/screenshot_{timestamp}.png"
            
            # 스크린샷 디렉토리 생성
            Path("screenshots").mkdir(exist_ok=True)
            
            response = await self._send_mcp_request("capture_screenshot", {
                "page_id": self.current_page,
                "path": screenshot_path
            })
            
            logger.info(f"스크린샷 캡처 완료: {screenshot_path}")
            return [screenshot_path]
            
        except Exception as e:
            logger.error(f"스크린샷 캡처 실패: {e}")
            return []
    
    async def get_logs(self) -> List[str]:
        """콘솔 로그 수집"""
        try:
            response = await self._send_mcp_request("get_console_logs", {
                "page_id": self.current_page
            })
            
            logs = response.get("logs", [])
            logger.info(f"콘솔 로그 수집 완료: {len(logs)}개")
            return logs
            
        except Exception as e:
            logger.error(f"콘솔 로그 수집 실패: {e}")
            return []
    
    async def get_network_status(self) -> Dict[str, Any]:
        """네트워크 상태 확인"""
        try:
            response = await self._send_mcp_request("get_network_status", {
                "page_id": self.current_page
            })
            
            return response
            
        except Exception as e:
            logger.error(f"네트워크 상태 확인 실패: {e}")
            return {"online": True}
    
    async def assert_element(self, selector: str, expected_value: str) -> bool:
        """요소 검증"""
        try:
            response = await self._send_mcp_request("assert_element", {
                "page_id": self.current_page,
                "selector": selector,
                "expected_value": expected_value
            })
            
            return response.get("assertion_passed", False)
            
        except Exception as e:
            logger.error(f"요소 검증 실패: {e}")
            return False
    
    async def refresh_element_reference(self, selector: str):
        """요소 참조 새로고침"""
        try:
            await self._send_mcp_request("refresh_element_reference", {
                "page_id": self.current_page,
                "selector": selector
            })
            
            logger.info(f"요소 참조 새로고침 완료: {selector}")
            
        except Exception as e:
            logger.error(f"요소 참조 새로고침 실패: {e}")
            raise
    
    async def _send_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 서버에 JSON-RPC 2.0 요청 전송"""
        if not self.connected:
            raise Exception("MCP 서버가 연결되지 않았습니다")
        
        try:
            # JSON-RPC 2.0 요청 형식
            request_data = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": method,
                "params": params
            }
            
            # HTTP POST 요청 전송
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/mcp",
                    json=request_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"MCP 서버 오류: {response.status} - {text}")
                    
                    # 응답 타입 확인
                    content_type = response.headers.get("content-type", "")
                    
                    if "text/event-stream" in content_type:
                        # SSE 응답 처리
                        result = {}
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data = line[6:]  # 'data: ' 제거
                                if data:
                                    try:
                                        event_data = json.loads(data)
                                        if "result" in event_data:
                                            result.update(event_data["result"])
                                        elif "error" in event_data:
                                            error = event_data["error"]
                                            raise Exception(f"MCP 오류: {error.get('message', 'Unknown error')} (코드: {error.get('code', 'Unknown')})")
                                    except json.JSONDecodeError:
                                        continue
                        return result
                    else:
                        # JSON 응답 처리
                        response_data = await response.json()
                        
                        # 오류 확인
                        if "error" in response_data:
                            error = response_data["error"]
                            raise Exception(f"MCP 오류: {error.get('message', 'Unknown error')} (코드: {error.get('code', 'Unknown')})")
                        
                        return response_data.get("result", {})
            
        except Exception as e:
            logger.error(f"MCP 요청 실패 ({method}): {e}")
            raise 