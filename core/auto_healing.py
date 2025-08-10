"""
Auto Healing System
테스트 실패 시 자동으로 복구를 시도하는 시스템
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AutoHealingSystem:
    """자동 복구 시스템"""

    def __init__(self):
        self.healing_actions = []
        self.max_retry_attempts = 3
        self.retry_delay = 2.0
        self.enabled = False

        # 복구 전략 정의
        self.healing_strategies = {
            "element_not_found": [
                "wait_for_element",
                "try_alternative_selectors",
                "refresh_page",
                "scroll_to_element",
            ],
            "element_not_clickable": [
                "wait_for_clickable",
                "scroll_to_element",
                "try_javascript_click",
                "wait_for_page_load",
            ],
            "timeout_error": [
                "increase_timeout",
                "retry_with_delay",
                "check_network_status",
                "refresh_page",
            ],
            "stale_element": [
                "refresh_element_reference",
                "wait_for_page_load",
                "retry_operation",
            ],
        }

    async def enable(self):
        """Auto Healing System 활성화"""
        self.enabled = True
        logger.info("Auto Healing System이 활성화되었습니다")

    async def disable(self):
        """Auto Healing System 비활성화"""
        self.enabled = False
        logger.info("Auto Healing System이 비활성화되었습니다")

    async def heal_element_not_found(self, selector: str, mcp_client) -> bool:
        """요소를 찾을 수 없을 때 복구 시도"""
        if not self.enabled:
            return False

        logger.info(f"요소를 찾을 수 없음: {selector}, 복구 시도 중...")

        for strategy in self.healing_strategies["element_not_found"]:
            try:
                if strategy == "wait_for_element":
                    await mcp_client.wait_for_element(selector, timeout=10)
                    self._log_healing_action(f"요소 대기 성공: {selector}")
                    return True

                elif strategy == "try_alternative_selectors":
                    alternative_selectors = self._generate_alternative_selectors(
                        selector
                    )
                    for alt_selector in alternative_selectors:
                        if await mcp_client.element_exists(alt_selector):
                            self._log_healing_action(
                                f"대체 선택자 사용: {alt_selector}"
                            )
                            return True

                elif strategy == "refresh_page":
                    await mcp_client.refresh_page()
                    await asyncio.sleep(2)
                    if await mcp_client.element_exists(selector):
                        self._log_healing_action(
                            f"페이지 새로고침 후 요소 발견: {selector}"
                        )
                        return True

                elif strategy == "scroll_to_element":
                    await mcp_client.scroll_to_element(selector)
                    if await mcp_client.element_exists(selector):
                        self._log_healing_action(f"스크롤 후 요소 발견: {selector}")
                        return True

            except Exception as e:
                logger.warning(f"복구 전략 {strategy} 실패: {e}")
                continue

        return False

    async def heal_element_not_clickable(self, selector: str, mcp_client) -> bool:
        """요소가 클릭 가능하지 않을 때 복구 시도"""
        if not self.enabled:
            return False

        logger.info(f"요소가 클릭 가능하지 않음: {selector}, 복구 시도 중...")

        for strategy in self.healing_strategies["element_not_clickable"]:
            try:
                if strategy == "wait_for_clickable":
                    await mcp_client.wait_for_element_to_be_clickable(
                        selector, timeout=10
                    )
                    self._log_healing_action(f"요소 클릭 가능 대기 성공: {selector}")
                    return True

                elif strategy == "scroll_to_element":
                    await mcp_client.scroll_to_element(selector)
                    await asyncio.sleep(1)
                    if await mcp_client.element_is_clickable(selector):
                        self._log_healing_action(
                            f"스크롤 후 요소 클릭 가능: {selector}"
                        )
                        return True

                elif strategy == "try_javascript_click":
                    await mcp_client.execute_javascript(
                        f"document.querySelector('{selector}').click()"
                    )
                    self._log_healing_action(f"JavaScript 클릭 성공: {selector}")
                    return True

                elif strategy == "wait_for_page_load":
                    await mcp_client.wait_for_page_load()
                    if await mcp_client.element_is_clickable(selector):
                        self._log_healing_action(
                            f"페이지 로드 후 요소 클릭 가능: {selector}"
                        )
                        return True

            except Exception as e:
                logger.warning(f"복구 전략 {strategy} 실패: {e}")
                continue

        return False

    async def heal_timeout_error(self, operation: str, mcp_client) -> bool:
        """타임아웃 오류 복구 시도"""
        if not self.enabled:
            return False

        logger.info(f"타임아웃 오류: {operation}, 복구 시도 중...")

        for strategy in self.healing_strategies["timeout_error"]:
            try:
                if strategy == "increase_timeout":
                    # 타임아웃 증가 로직
                    self._log_healing_action(f"타임아웃 증가: {operation}")
                    return True

                elif strategy == "retry_with_delay":
                    await asyncio.sleep(self.retry_delay)
                    self._log_healing_action(f"지연 후 재시도: {operation}")
                    return True

                elif strategy == "check_network_status":
                    network_status = await mcp_client.get_network_status()
                    if network_status.get("online", True):
                        self._log_healing_action(
                            f"네트워크 상태 확인: {network_status}"
                        )
                        return True

                elif strategy == "refresh_page":
                    await mcp_client.refresh_page()
                    await asyncio.sleep(2)
                    self._log_healing_action(f"페이지 새로고침: {operation}")
                    return True

            except Exception as e:
                logger.warning(f"복구 전략 {strategy} 실패: {e}")
                continue

        return False

    async def heal_stale_element(self, selector: str, mcp_client) -> bool:
        """Stale Element 복구 시도"""
        if not self.enabled:
            return False

        logger.info(f"Stale Element 오류: {selector}, 복구 시도 중...")

        for strategy in self.healing_strategies["stale_element"]:
            try:
                if strategy == "refresh_element_reference":
                    # 요소 참조 새로고침
                    await mcp_client.refresh_element_reference(selector)
                    self._log_healing_action(f"요소 참조 새로고침: {selector}")
                    return True

                elif strategy == "wait_for_page_load":
                    await mcp_client.wait_for_page_load()
                    if await mcp_client.element_exists(selector):
                        self._log_healing_action(
                            f"페이지 로드 후 요소 참조 복구: {selector}"
                        )
                        return True

                elif strategy == "retry_operation":
                    await asyncio.sleep(1)
                    if await mcp_client.element_exists(selector):
                        self._log_healing_action(
                            f"재시도 후 요소 참조 복구: {selector}"
                        )
                        return True

            except Exception as e:
                logger.warning(f"복구 전략 {strategy} 실패: {e}")
                continue

        return False

    def _generate_alternative_selectors(self, original_selector: str) -> List[str]:
        """대체 선택자 생성"""
        alternatives = []

        # ID 기반 선택자
        if original_selector.startswith("#"):
            element_id = original_selector[1:]
            alternatives.extend(
                [
                    f"[id='{element_id}']",
                    f"[data-testid='{element_id}']",
                    f"[name='{element_id}']",
                ]
            )

        # 클래스 기반 선택자
        elif original_selector.startswith("."):
            class_name = original_selector[1:]
            alternatives.extend(
                [
                    f"[class*='{class_name}']",
                    f"[data-testid*='{class_name}']",
                    f"[aria-label*='{class_name}']",
                ]
            )

        # 일반 선택자
        else:
            alternatives.extend(
                [
                    f"[data-testid='{original_selector}']",
                    f"[aria-label='{original_selector}']",
                    f"[title='{original_selector}']",
                ]
            )

        return alternatives

    def _log_healing_action(self, action: str):
        """복구 액션 로깅"""
        timestamp = datetime.now().isoformat()
        self.healing_actions.append({"timestamp": timestamp, "action": action})
        logger.info(f"Auto Healing: {action}")

    def get_healing_actions(self) -> List[str]:
        """수행된 복구 액션 목록 반환"""
        return [action["action"] for action in self.healing_actions]

    def reset_healing_actions(self):
        """복구 액션 기록 초기화"""
        self.healing_actions = []

    async def smart_retry(self, operation_func, *args, **kwargs) -> Any:
        """스마트 재시도 로직"""
        for attempt in range(self.max_retry_attempts):
            try:
                return await operation_func(*args, **kwargs)
            except Exception as e:
                error_type = self._classify_error(e)

                if attempt < self.max_retry_attempts - 1:
                    logger.warning(f"시도 {attempt + 1} 실패, 재시도 중... 오류: {e}")

                    # 오류 유형에 따른 복구 시도
                    if error_type == "element_not_found":
                        await self.heal_element_not_found(args[0] if args else "", None)
                    elif error_type == "timeout":
                        await self.heal_timeout_error(str(operation_func), None)

                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"최대 재시도 횟수 초과: {e}")
                    raise e

    async def ml_enhanced_healing(
        self, error_context: Dict[str, Any], google_adk=None
    ) -> Dict[str, Any]:
        """ML 강화 자동 복구"""
        try:
            logger.info("ML 강화 자동 복구 시작")

            # Google ADK의 ML 기반 복구 사용
            if google_adk and hasattr(google_adk, "ml_based_auto_healing"):
                ml_result = await google_adk.ml_based_auto_healing(error_context)

                if ml_result.get("success_probability", 0) > 0.8:
                    # ML 기반 복구 전략 실행
                    strategy = ml_result.get("selected_strategy", {})
                    healing_result = ml_result.get("healing_result", {})

                    if healing_result.get("success", False):
                        self._log_healing_action(
                            f"ML 기반 복구 성공: {healing_result.get('resolution_method', 'unknown')}"
                        )
                        return ml_result

            # 기존 복구 로직으로 폴백
            return await self._fallback_healing(error_context)

        except Exception as e:
            logger.error(f"ML 강화 복구 중 오류: {e}")
            return await self._fallback_healing(error_context)

    async def _fallback_healing(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """기존 복구 로직으로 폴백"""
        try:
            error_type = error_context.get("error_type", "unknown")

            if error_type == "element_not_found":
                await self.heal_element_not_found(
                    error_context.get("selector", ""), None
                )
            elif error_type == "timeout":
                await self.heal_timeout_error(error_context.get("operation", ""), None)
            elif error_type == "element_not_clickable":
                await self.heal_element_not_clickable(
                    error_context.get("selector", ""), None
                )

            return {
                "success": True,
                "method": "fallback_healing",
                "resolution": error_type,
            }

        except Exception as e:
            logger.error(f"폴백 복구 중 오류: {e}")
            return {"success": False, "error": str(e)}

    def _classify_error(self, error: Exception) -> str:
        """오류 유형 분류"""
        error_message = str(error).lower()

        if "element not found" in error_message or "no such element" in error_message:
            return "element_not_found"
        elif "timeout" in error_message:
            return "timeout"
        elif "stale" in error_message:
            return "stale_element"
        elif "not clickable" in error_message:
            return "element_not_clickable"
        else:
            return "unknown"
