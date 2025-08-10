#!/usr/bin/env python3
"""
자동 테스트 스위트 - 종합 웹 자동화 테스트 도구
웹 페이지 분석 -> 테스트 케이스 자동 생성 -> 자동화 스크립트 생성 -> 실행 -> 모니터링
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.mcp_client import PlaywrightMCPClient
from core.quality_monitor import QualityMonitor
from core.google_adk_integration import GoogleADKIntegration
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AutoTestSuite:
    """자동 테스트 스위트 - 종합 웹 자동화 테스트 도구"""

    def __init__(self):
        self.mcp_client = PlaywrightMCPClient()
        self.quality_monitor = QualityMonitor()
        self.google_adk = GoogleADKIntegration()
        self.page_analysis = {}
        self.generated_test_cases = []
        self.generated_scripts = []
        self.execution_results = {}

    async def run_complete_test_workflow(
        self, url: str, test_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """완전한 테스트 워크플로우 실행

        Args:
            url (str): 테스트할 웹사이트 URL
            test_type (str): 테스트 유형 (comprehensive, functional, accessibility, performance)

        Returns:
            Dict: 전체 워크플로우 결과
        """
        try:
            logger.info(f"자동 테스트 스위트 시작: {url}")
            start_time = datetime.now()

            # 1단계: 웹 페이지 접근 및 분석
            logger.info("1단계: 웹 페이지 접근 및 분석 중...")
            page_analysis = await self._analyze_webpage_with_mcp(url)

            # 2단계: 테스트 케이스 자동 생성
            logger.info("2단계: 테스트 케이스 자동 생성 중...")
            test_cases = await self._generate_test_cases_from_analysis(
                page_analysis, test_type
            )

            # 3단계: 자동화 스크립트 생성
            logger.info("3단계: 자동화 스크립트 생성 중...")
            automation_scripts = await self._generate_automation_scripts(
                test_cases, page_analysis
            )

            # 4단계: 테스트 실행
            logger.info("4단계: 테스트 실행 중...")
            execution_results = await self._execute_generated_tests(test_cases, url)

            # 5단계: 성능 모니터링 및 메트릭 측정
            logger.info("5단계: 성능 모니터링 및 메트릭 측정 중...")
            monitoring_results = await self._perform_monitoring_and_metrics(url)

            # 6단계: 종합 리포트 생성
            logger.info("6단계: 종합 리포트 생성 중...")
            final_report = await self._generate_comprehensive_report(
                page_analysis,
                test_cases,
                automation_scripts,
                execution_results,
                monitoring_results,
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "workflow_id": f"auto_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "test_type": test_type,
                "status": "completed",
                "execution_time": execution_time,
                "page_analysis": page_analysis,
                "generated_test_cases": test_cases,
                "automation_scripts": automation_scripts,
                "execution_results": execution_results,
                "monitoring_results": monitoring_results,
                "final_report": final_report,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"자동 테스트 스위트 실패: {e}")
            return {
                "workflow_id": f"auto_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "test_type": test_type,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _analyze_webpage_with_mcp(self, url: str) -> Dict[str, Any]:
        """MCP를 활용한 웹 페이지 종합 분석"""
        try:
            logger.info(f"MCP를 통한 웹 페이지 분석 시작: {url}")

            # MCP 클라이언트 연결
            await self.mcp_client.connect()

            # 페이지 로드
            await self.mcp_client.navigate(url)
            await self.mcp_client.wait_for_page_load()

            # 종합 분석 수행
            analysis_result = {
                "url": url,
                "basic_info": await self._get_basic_page_info(),
                "page_structure": await self._analyze_page_structure(),
                "interactive_elements": await self._analyze_interactive_elements(),
                "form_elements": await self._analyze_form_elements(),
                "performance_metrics": await self._collect_performance_metrics(),
                "accessibility_analysis": await self._analyze_accessibility(),
                "seo_analysis": await self._analyze_seo(),
                "network_status": await self.mcp_client.get_network_status(),
                "console_logs": await self.mcp_client.get_logs(),
                "screenshots": await self.mcp_client.capture_screenshots(),
                "analysis_timestamp": datetime.now().isoformat(),
            }

            self.page_analysis = analysis_result
            logger.info("웹 페이지 분석 완료")
            return analysis_result

        except Exception as e:
            logger.error(f"웹 페이지 분석 실패: {e}")
            raise

    async def _get_basic_page_info(self) -> Dict[str, Any]:
        """기본 페이지 정보 수집"""
        try:
            basic_info = await self.mcp_client.execute_javascript(
                """
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        viewport: {
                            width: window.innerWidth,
                            height: window.innerHeight
                        },
                        userAgent: navigator.userAgent,
                        language: navigator.language,
                        cookies: document.cookie ? document.cookie.split(';').length : 0
                    };
                }
            """
            )
            return basic_info
        except Exception as e:
            logger.error(f"기본 페이지 정보 수집 실패: {e}")
            return {}

    async def _analyze_page_structure(self) -> Dict[str, Any]:
        """페이지 구조 분석"""
        try:
            structure_script = """
            () => {
                const structure = {
                    headings: [],
                    paragraphs: [],
                    images: [],
                    links: [],
                    buttons: [],
                    inputs: [],
                    forms: [],
                    sections: [],
                    lists: []
                };
                
                // 헤딩 분석
                for (let i = 1; i <= 6; i++) {
                    const headings = document.querySelectorAll(`h${i}`);
                    headings.forEach(h => {
                        structure.headings.push({
                            level: i,
                            text: h.textContent.trim(),
                            id: h.id || null,
                            className: h.className || null,
                            selector: `h${i}${h.id ? '#' + h.id : ''}${h.className ? '.' + h.className.split(' ').join('.') : ''}`
                        });
                    });
                }
                
                // 단락 분석
                const paragraphs = document.querySelectorAll('p');
                paragraphs.forEach(p => {
                    structure.paragraphs.push({
                        text: p.textContent.trim().substring(0, 100),
                        id: p.id || null,
                        className: p.className || null,
                        selector: `p${p.id ? '#' + p.id : ''}${p.className ? '.' + p.className.split(' ').join('.') : ''}`
                    });
                });
                
                // 이미지 분석
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    structure.images.push({
                        src: img.src,
                        alt: img.alt || null,
                        id: img.id || null,
                        className: img.className || null,
                        selector: `img${img.id ? '#' + img.id : ''}${img.className ? '.' + img.className.split(' ').join('.') : ''}`,
                        width: img.naturalWidth,
                        height: img.naturalHeight
                    });
                });
                
                // 링크 분석
                const links = document.querySelectorAll('a');
                links.forEach(link => {
                    structure.links.push({
                        href: link.href,
                        text: link.textContent.trim(),
                        id: link.id || null,
                        className: link.className || null,
                        selector: `a${link.id ? '#' + link.id : ''}${link.className ? '.' + link.className.split(' ').join('.') : ''}`,
                        isExternal: link.hostname !== window.location.hostname
                    });
                });
                
                // 버튼 분석
                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                buttons.forEach(btn => {
                    structure.buttons.push({
                        text: btn.textContent.trim() || btn.value || null,
                        type: btn.type || 'button',
                        id: btn.id || null,
                        className: btn.className || null,
                        selector: `${btn.tagName.toLowerCase()}${btn.id ? '#' + btn.id : ''}${btn.className ? '.' + btn.className.split(' ').join('.') : ''}`
                    });
                });
                
                // 입력 필드 분석
                const inputs = document.querySelectorAll('input:not([type="button"]):not([type="submit"]), textarea, select');
                inputs.forEach(input => {
                    structure.inputs.push({
                        type: input.type || input.tagName.toLowerCase(),
                        name: input.name || null,
                        id: input.id || null,
                        className: input.className || null,
                        placeholder: input.placeholder || null,
                        required: input.required || false,
                        selector: `${input.tagName.toLowerCase()}${input.id ? '#' + input.id : ''}${input.name ? '[name="' + input.name + '"]' : ''}`
                    });
                });
                
                // 폼 분석
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    structure.forms.push({
                        action: form.action || null,
                        method: form.method || 'get',
                        id: form.id || null,
                        className: form.className || null,
                        selector: `form${form.id ? '#' + form.id : ''}${form.className ? '.' + form.className.split(' ').join('.') : ''}`
                    });
                });
                
                // 리스트 분석
                const lists = document.querySelectorAll('ul, ol');
                lists.forEach(list => {
                    structure.lists.push({
                        type: list.tagName.toLowerCase(),
                        id: list.id || null,
                        className: list.className || null,
                        itemCount: list.children.length,
                        selector: `${list.tagName.toLowerCase()}${list.id ? '#' + list.id : ''}${list.className ? '.' + list.className.split(' ').join('.') : ''}`
                    });
                });
                
                return structure;
            }
            """

            structure_result = await self.mcp_client.execute_javascript(
                structure_script
            )
            return structure_result

        except Exception as e:
            logger.error(f"페이지 구조 분석 실패: {e}")
            return {}

    async def _analyze_interactive_elements(self) -> Dict[str, Any]:
        """상호작용 요소 분석"""
        try:
            interactive_script = """
            () => {
                const interactive = {
                    clickable_elements: [],
                    hover_elements: [],
                    focusable_elements: [],
                    keyboard_navigation: []
                };
                
                // 클릭 가능한 요소들
                const clickables = document.querySelectorAll('a, button, input[type="button"], input[type="submit"], [onclick], [role="button"]');
                clickables.forEach(el => {
                    const selector = `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className ? '.' + el.className.split(' ').join('.') : ''}`;
                    interactive.clickable_elements.push({
                        tagName: el.tagName.toLowerCase(),
                        text: el.textContent.trim() || el.value || null,
                        selector: selector,
                        id: el.id || null,
                        className: el.className || null,
                        isVisible: el.offsetParent !== null,
                        isClickable: true,
                        position: {
                            x: el.offsetLeft,
                            y: el.offsetTop,
                            width: el.offsetWidth,
                            height: el.offsetHeight
                        }
                    });
                });
                
                // 호버 효과가 있는 요소들
                const hoverElements = document.querySelectorAll('[class*="hover"], [class*="mouse"], [style*="cursor: pointer"]');
                hoverElements.forEach(el => {
                    const selector = `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className ? '.' + el.className.split(' ').join('.') : ''}`;
                    interactive.hover_elements.push({
                        tagName: el.tagName.toLowerCase(),
                        selector: selector,
                        className: el.className || null
                    });
                });
                
                // 포커스 가능한 요소들
                const focusables = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
                focusables.forEach(el => {
                    const selector = `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className ? '.' + el.className.split(' ').join('.') : ''}`;
                    interactive.focusable_elements.push({
                        tagName: el.tagName.toLowerCase(),
                        tabIndex: el.tabIndex || 0,
                        selector: selector,
                        id: el.id || null
                    });
                });
                
                return interactive;
            }
            """

            interactive_result = await self.mcp_client.execute_javascript(
                interactive_script
            )
            return interactive_result

        except Exception as e:
            logger.error(f"상호작용 요소 분석 실패: {e}")
            return {}

    async def _analyze_form_elements(self) -> List[Dict[str, Any]]:
        """폼 요소 분석"""
        try:
            form_script = """
            () => {
                const forms = document.querySelectorAll('form');
                const formAnalysis = [];
                
                forms.forEach((form, index) => {
                    const formData = {
                        formIndex: index,
                        action: form.action || null,
                        method: form.method || 'get',
                        id: form.id || null,
                        className: form.className || null,
                        selector: `form${form.id ? '#' + form.id : ''}${form.className ? '.' + form.className.split(' ').join('.') : ''}`,
                        fields: [],
                        submitButtons: []
                    };
                    
                    // 폼 필드 분석
                    const fields = form.querySelectorAll('input, textarea, select');
                    fields.forEach(field => {
                        const selector = `${field.tagName.toLowerCase()}${field.id ? '#' + field.id : ''}${field.name ? '[name="' + field.name + '"]' : ''}`;
                        formData.fields.push({
                            type: field.type || field.tagName.toLowerCase(),
                            name: field.name || null,
                            id: field.id || null,
                            placeholder: field.placeholder || null,
                            required: field.required || false,
                            pattern: field.pattern || null,
                            minLength: field.minLength || null,
                            maxLength: field.maxLength || null,
                            selector: selector
                        });
                    });
                    
                    // 제출 버튼 분석
                    const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
                    submitButtons.forEach(btn => {
                        const selector = `${btn.tagName.toLowerCase()}${btn.id ? '#' + btn.id : ''}${btn.className ? '.' + btn.className.split(' ').join('.') : ''}`;
                        formData.submitButtons.push({
                            text: btn.textContent.trim() || btn.value || null,
                            id: btn.id || null,
                            className: btn.className || null,
                            selector: selector
                        });
                    });
                    
                    formAnalysis.push(formData);
                });
                
                return formAnalysis;
            }
            """

            form_result = await self.mcp_client.execute_javascript(form_script)
            return form_result

        except Exception as e:
            logger.error(f"폼 요소 분석 실패: {e}")
            return []

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        try:
            performance_script = """
            () => {
                const metrics = {};
                
                // Navigation Timing API
                if (window.performance && window.performance.timing) {
                    const timing = window.performance.timing;
                    metrics.navigationTiming = {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                        loadComplete: timing.loadEventEnd - timing.loadEventStart,
                        domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                        pageLoad: timing.loadEventEnd - timing.navigationStart
                    };
                }
                
                // Performance Observer (최신 브라우저)
                if (window.PerformanceObserver) {
                    const observer = new PerformanceObserver((list) => {
                        list.getEntries().forEach(entry => {
                            if (entry.entryType === 'paint') {
                                metrics[entry.name] = entry.startTime;
                            }
                        });
                    });
                    observer.observe({ entryTypes: ['paint'] });
                }
                
                // 메모리 사용량
                if (window.performance && window.performance.memory) {
                    metrics.memory = {
                        usedJSHeapSize: window.performance.memory.usedJSHeapSize,
                        totalJSHeapSize: window.performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit
                    };
                }
                
                // JavaScript 오류 수
                metrics.jsErrors = window.jsErrors || 0;
                
                // DOM 요소 수
                metrics.domElements = document.querySelectorAll('*').length;
                
                // 이미지 수
                metrics.imageCount = document.querySelectorAll('img').length;
                
                // 링크 수
                metrics.linkCount = document.querySelectorAll('a').length;
                
                return metrics;
            }
            """

            performance_result = await self.mcp_client.execute_javascript(
                performance_script
            )
            return performance_result

        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
            return {}

    async def _analyze_accessibility(self) -> Dict[str, Any]:
        """접근성 분석"""
        try:
            accessibility_script = """
            () => {
                const accessibility = {
                    altTexts: [],
                    ariaLabels: [],
                    keyboardNavigation: [],
                    colorContrast: [],
                    focusIndicators: []
                };
                
                // Alt 텍스트 분석
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    accessibility.altTexts.push({
                        src: img.src,
                        alt: img.alt || null,
                        hasAlt: !!img.alt,
                        isDecorative: img.alt === '' || img.alt === null
                    });
                });
                
                // ARIA 라벨 분석
                const ariaElements = document.querySelectorAll('[aria-label], [aria-labelledby], [aria-describedby]');
                ariaElements.forEach(el => {
                    accessibility.ariaLabels.push({
                        tagName: el.tagName.toLowerCase(),
                        ariaLabel: el.getAttribute('aria-label'),
                        ariaLabelledby: el.getAttribute('aria-labelledby'),
                        ariaDescribedby: el.getAttribute('aria-describedby'),
                        id: el.id || null
                    });
                });
                
                // 키보드 네비게이션 가능성
                const focusables = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
                accessibility.keyboardNavigation = focusables.length > 0;
                
                // 포커스 표시자 확인
                const style = getComputedStyle(document.body);
                const outline = style.outline;
                accessibility.focusIndicators.push({
                    outline: outline,
                    hasFocusStyle: outline !== 'none' && outline !== ''
                });
                
                return accessibility;
            }
            """

            accessibility_result = await self.mcp_client.execute_javascript(
                accessibility_script
            )
            return accessibility_result

        except Exception as e:
            logger.error(f"접근성 분석 실패: {e}")
            return {}

    async def _analyze_seo(self) -> Dict[str, Any]:
        """SEO 분석"""
        try:
            seo_script = """
            () => {
                const seo = {
                    metaTags: [],
                    headings: [],
                    images: [],
                    links: [],
                    structuredData: []
                };
                
                // 메타 태그 분석
                const metaTags = document.querySelectorAll('meta');
                metaTags.forEach(meta => {
                    seo.metaTags.push({
                        name: meta.getAttribute('name'),
                        content: meta.getAttribute('content'),
                        property: meta.getAttribute('property')
                    });
                });
                
                // 헤딩 구조 분석
                for (let i = 1; i <= 6; i++) {
                    const headings = document.querySelectorAll(`h${i}`);
                    headings.forEach(h => {
                        seo.headings.push({
                            level: i,
                            text: h.textContent.trim(),
                            id: h.id || null
                        });
                    });
                }
                
                // 이미지 SEO 분석
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    seo.images.push({
                        src: img.src,
                        alt: img.alt || null,
                        title: img.title || null,
                        hasAlt: !!img.alt
                    });
                });
                
                // 링크 분석
                const links = document.querySelectorAll('a');
                links.forEach(link => {
                    seo.links.push({
                        href: link.href,
                        text: link.textContent.trim(),
                        title: link.title || null,
                        rel: link.rel || null
                    });
                });
                
                // 구조화된 데이터
                const structuredData = document.querySelectorAll('script[type="application/ld+json"]');
                structuredData.forEach(script => {
                    try {
                        const data = JSON.parse(script.textContent);
                        seo.structuredData.push(data);
                    } catch (e) {
                        // JSON 파싱 실패
                    }
                });
                
                return seo;
            }
            """

            seo_result = await self.mcp_client.execute_javascript(seo_script)
            return seo_result

        except Exception as e:
            logger.error(f"SEO 분석 실패: {e}")
            return {}


if __name__ == "__main__":
    # 사용 예제
    async def main():
        auto_suite = AutoTestSuite()
        result = await auto_suite.run_complete_test_workflow("https://www.google.com")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    asyncio.run(main())
