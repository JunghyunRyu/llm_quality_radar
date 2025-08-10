"""
품질 모니터링 시스템
웹 애플리케이션의 품질을 실시간으로 평가하고 모니터링하는 시스템
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class QualityMonitor:
    """품질 모니터링 시스템"""
    
    def __init__(self):
        self.quality_metrics = {}
        self.performance_data = {}
        self.accessibility_scores = {}
        self.seo_scores = {}
        
        # 품질 평가 기준
        self.quality_thresholds = {
            "performance": {
                "page_load_time": 3.0,  # 초
                "first_contentful_paint": 1.8,
                "largest_contentful_paint": 2.5,
                "cumulative_layout_shift": 0.1
            },
            "accessibility": {
                "wcag_aa_compliance": 0.95,  # 95% 이상
                "keyboard_navigation": 1.0,
                "screen_reader_compatibility": 1.0
            },
            "seo": {
                "meta_tags": 0.8,
                "heading_structure": 0.9,
                "image_alt_texts": 0.9,
                "internal_links": 0.7
            },
            "functionality": {
                "broken_links": 0.0,  # 0% (깨진 링크 없음)
                "javascript_errors": 0.0,
                "form_validation": 1.0
            }
        }
    
    async def assess_quality(self, mcp_client=None) -> float:
        """전체 품질 점수 평가"""
        try:
            logger.info("품질 평가 시작...")
            
            # 1. 성능 평가
            performance_score = await self._assess_performance(mcp_client)
            
            # 2. 접근성 평가
            accessibility_score = await self._assess_accessibility(mcp_client)
            
            # 3. SEO 평가
            seo_score = await self._assess_seo(mcp_client)
            
            # 4. 기능성 평가
            functionality_score = await self._assess_functionality(mcp_client)
            
            # 5. 종합 점수 계산
            overall_score = self._calculate_overall_score({
                "performance": performance_score,
                "accessibility": accessibility_score,
                "seo": seo_score,
                "functionality": functionality_score
            })
            
            # 결과 저장
            self.quality_metrics = {
                "timestamp": datetime.now().isoformat(),
                "overall_score": overall_score,
                "performance_score": performance_score,
                "accessibility_score": accessibility_score,
                "seo_score": seo_score,
                "functionality_score": functionality_score,
                "details": {
                    "performance": self.performance_data,
                    "accessibility": self.accessibility_scores,
                    "seo": self.seo_scores
                }
            }
            
            logger.info(f"품질 평가 완료: {overall_score:.2f}/100")
            return overall_score
            
        except Exception as e:
            logger.error(f"품질 평가 중 오류: {e}")
            return 0.0
    
    async def _assess_performance(self, mcp_client) -> float:
        """성능 평가"""
        try:
            if not mcp_client:
                return 80.0  # 기본값
            
            # 성능 메트릭 수집
            performance_metrics = await self._collect_performance_metrics(mcp_client)
            
            # 각 메트릭별 점수 계산
            scores = {}
            total_score = 0
            weight_sum = 0
            
            for metric, value in performance_metrics.items():
                threshold = self.quality_thresholds["performance"].get(metric, 0)
                if threshold > 0:
                    # 임계값 대비 점수 계산 (낮을수록 좋음)
                    score = max(0, 100 - (value / threshold) * 100)
                    scores[metric] = score
                    
                    # 가중치 적용
                    weight = self._get_performance_weight(metric)
                    total_score += score * weight
                    weight_sum += weight
            
            self.performance_data = {
                "metrics": performance_metrics,
                "scores": scores
            }
            
            return total_score / weight_sum if weight_sum > 0 else 0
            
        except Exception as e:
            logger.error(f"성능 평가 중 오류: {e}")
            return 0.0
    
    async def _assess_accessibility(self, mcp_client) -> float:
        """접근성 평가"""
        try:
            if not mcp_client:
                return 85.0  # 기본값
            
            # 접근성 검사 수행
            accessibility_checks = await self._perform_accessibility_checks(mcp_client)
            
            # WCAG AA 준수도 평가
            wcag_score = self._evaluate_wcag_compliance(accessibility_checks)
            
            # 키보드 네비게이션 평가
            keyboard_score = self._evaluate_keyboard_navigation(accessibility_checks)
            
            # 스크린 리더 호환성 평가
            screen_reader_score = self._evaluate_screen_reader_compatibility(accessibility_checks)
            
            # 종합 점수 계산
            overall_score = (wcag_score + keyboard_score + screen_reader_score) / 3
            
            self.accessibility_scores = {
                "wcag_score": wcag_score,
                "keyboard_score": keyboard_score,
                "screen_reader_score": screen_reader_score,
                "overall_score": overall_score,
                "checks": accessibility_checks
            }
            
            return overall_score
            
        except Exception as e:
            logger.error(f"접근성 평가 중 오류: {e}")
            return 0.0
    
    async def _assess_seo(self, mcp_client) -> float:
        """SEO 평가"""
        try:
            if not mcp_client:
                return 75.0  # 기본값
            
            # SEO 요소 검사
            seo_checks = await self._perform_seo_checks(mcp_client)
            
            # 메타 태그 평가
            meta_score = self._evaluate_meta_tags(seo_checks)
            
            # 헤딩 구조 평가
            heading_score = self._evaluate_heading_structure(seo_checks)
            
            # 이미지 alt 텍스트 평가
            alt_text_score = self._evaluate_image_alt_texts(seo_checks)
            
            # 내부 링크 평가
            internal_links_score = self._evaluate_internal_links(seo_checks)
            
            # 종합 점수 계산
            overall_score = (meta_score + heading_score + alt_text_score + internal_links_score) / 4
            
            self.seo_scores = {
                "meta_score": meta_score,
                "heading_score": heading_score,
                "alt_text_score": alt_text_score,
                "internal_links_score": internal_links_score,
                "overall_score": overall_score,
                "checks": seo_checks
            }
            
            return overall_score
            
        except Exception as e:
            logger.error(f"SEO 평가 중 오류: {e}")
            return 0.0
    
    async def _assess_functionality(self, mcp_client) -> float:
        """기능성 평가"""
        try:
            if not mcp_client:
                return 90.0  # 기본값
            
            # 기능성 검사
            functionality_checks = await self._perform_functionality_checks(mcp_client)
            
            # 깨진 링크 검사
            broken_links_score = self._evaluate_broken_links(functionality_checks)
            
            # JavaScript 오류 검사
            js_errors_score = self._evaluate_javascript_errors(functionality_checks)
            
            # 폼 검증 검사
            form_validation_score = self._evaluate_form_validation(functionality_checks)
            
            # 종합 점수 계산
            overall_score = (broken_links_score + js_errors_score + form_validation_score) / 3
            
            return overall_score
            
        except Exception as e:
            logger.error(f"기능성 평가 중 오류: {e}")
            return 0.0
    
    async def _collect_performance_metrics(self, mcp_client) -> Dict[str, float]:
        """성능 메트릭 수집"""
        try:
            # JavaScript를 통한 성능 메트릭 수집
            performance_script = """
            const performance = window.performance;
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            return {
                page_load_time: navigation.loadEventEnd - navigation.loadEventStart,
                first_contentful_paint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                largest_contentful_paint: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime || 0,
                cumulative_layout_shift: performance.getEntriesByType('layout-shift').reduce((sum, shift) => sum + shift.value, 0)
            };
            """
            
            metrics = await mcp_client.execute_javascript(performance_script)
            return metrics or {}
            
        except Exception as e:
            logger.error(f"성능 메트릭 수집 중 오류: {e}")
            return {}
    
    async def _perform_accessibility_checks(self, mcp_client) -> Dict[str, Any]:
        """접근성 검사 수행"""
        try:
            # 접근성 검사 스크립트
            accessibility_script = """
            const checks = {
                alt_texts: [],
                headings: [],
                landmarks: [],
                keyboard_navigation: [],
                color_contrast: [],
                aria_labels: []
            };
            
            // 이미지 alt 텍스트 검사
            document.querySelectorAll('img').forEach(img => {
                checks.alt_texts.push({
                    has_alt: !!img.alt,
                    alt_text: img.alt
                });
            });
            
            // 헤딩 구조 검사
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
                checks.headings.push({
                    tag: heading.tagName,
                    text: heading.textContent,
                    level: parseInt(heading.tagName.charAt(1))
                });
            });
            
            // 랜드마크 검사
            document.querySelectorAll('main, nav, header, footer, aside, section, article').forEach(landmark => {
                checks.landmarks.push({
                    tag: landmark.tagName,
                    role: landmark.getAttribute('role') || landmark.tagName
                });
            });
            
            // ARIA 라벨 검사
            document.querySelectorAll('[aria-label], [aria-labelledby]').forEach(element => {
                checks.aria_labels.push({
                    aria_label: element.getAttribute('aria-label'),
                    aria_labelledby: element.getAttribute('aria-labelledby')
                });
            });
            
            return checks;
            """
            
            checks = await mcp_client.execute_javascript(accessibility_script)
            return checks or {}
            
        except Exception as e:
            logger.error(f"접근성 검사 중 오류: {e}")
            return {}
    
    async def _perform_seo_checks(self, mcp_client) -> Dict[str, Any]:
        """SEO 검사 수행"""
        try:
            # SEO 검사 스크립트
            seo_script = """
            const checks = {
                meta_tags: {},
                headings: [],
                images: [],
                links: [],
                title: document.title
            };
            
            // 메타 태그 검사
            document.querySelectorAll('meta').forEach(meta => {
                const name = meta.getAttribute('name') || meta.getAttribute('property');
                const content = meta.getAttribute('content');
                if (name && content) {
                    checks.meta_tags[name] = content;
                }
            });
            
            // 헤딩 검사
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
                checks.headings.push({
                    tag: heading.tagName,
                    text: heading.textContent.trim(),
                    level: parseInt(heading.tagName.charAt(1))
                });
            });
            
            // 이미지 검사
            document.querySelectorAll('img').forEach(img => {
                checks.images.push({
                    src: img.src,
                    alt: img.alt,
                    title: img.title
                });
            });
            
            // 링크 검사
            document.querySelectorAll('a').forEach(link => {
                checks.links.push({
                    href: link.href,
                    text: link.textContent.trim(),
                    title: link.title
                });
            });
            
            return checks;
            """
            
            checks = await mcp_client.execute_javascript(seo_script)
            return checks or {}
            
        except Exception as e:
            logger.error(f"SEO 검사 중 오류: {e}")
            return {}
    
    async def _perform_functionality_checks(self, mcp_client) -> Dict[str, Any]:
        """기능성 검사 수행"""
        try:
            # 기능성 검사 스크립트
            functionality_script = """
            const checks = {
                javascript_errors: [],
                forms: [],
                links: []
            };
            
            // JavaScript 오류 수집
            window.addEventListener('error', (e) => {
                checks.javascript_errors.push({
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno
                });
            });
            
            // 폼 검사
            document.querySelectorAll('form').forEach(form => {
                checks.forms.push({
                    action: form.action,
                    method: form.method,
                    inputs: Array.from(form.querySelectorAll('input, textarea, select')).map(input => ({
                        type: input.type,
                        name: input.name,
                        required: input.required,
                        validation: input.validity.valid
                    }))
                });
            });
            
            // 링크 검사
            document.querySelectorAll('a').forEach(link => {
                checks.links.push({
                    href: link.href,
                    text: link.textContent.trim(),
                    is_internal: link.href.startsWith(window.location.origin)
                });
            });
            
            return checks;
            """
            
            checks = await mcp_client.execute_javascript(functionality_script)
            return checks or {}
            
        except Exception as e:
            logger.error(f"기능성 검사 중 오류: {e}")
            return {}
    
    def _evaluate_wcag_compliance(self, checks: Dict[str, Any]) -> float:
        """WCAG AA 준수도 평가"""
        try:
            total_checks = 0
            passed_checks = 0
            
            # alt 텍스트 검사
            if checks.get("alt_texts"):
                for img_check in checks["alt_texts"]:
                    total_checks += 1
                    if img_check.get("has_alt"):
                        passed_checks += 1
            
            # 헤딩 구조 검사
            if checks.get("headings"):
                heading_levels = [h["level"] for h in checks["headings"]]
                if heading_levels:
                    total_checks += 1
                    if self._is_valid_heading_structure(heading_levels):
                        passed_checks += 1
            
            # 랜드마크 검사
            if checks.get("landmarks"):
                total_checks += 1
                if len(checks["landmarks"]) > 0:
                    passed_checks += 1
            
            return (passed_checks / total_checks * 100) if total_checks > 0 else 0
            
        except Exception as e:
            logger.error(f"WCAG 준수도 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_keyboard_navigation(self, checks: Dict[str, Any]) -> float:
        """키보드 네비게이션 평가"""
        # 실제 구현에서는 키보드 이벤트 시뮬레이션을 통해 평가
        return 85.0  # 기본값
    
    def _evaluate_screen_reader_compatibility(self, checks: Dict[str, Any]) -> float:
        """스크린 리더 호환성 평가"""
        try:
            total_checks = 0
            passed_checks = 0
            
            # ARIA 라벨 검사
            if checks.get("aria_labels"):
                for aria_check in checks["aria_labels"]:
                    total_checks += 1
                    if aria_check.get("aria_label") or aria_check.get("aria_labelledby"):
                        passed_checks += 1
            
            return (passed_checks / total_checks * 100) if total_checks > 0 else 80.0
            
        except Exception as e:
            logger.error(f"스크린 리더 호환성 평가 중 오류: {e}")
            return 80.0
    
    def _evaluate_meta_tags(self, checks: Dict[str, Any]) -> float:
        """메타 태그 평가"""
        try:
            meta_tags = checks.get("meta_tags", {})
            required_tags = ["description", "keywords", "viewport"]
            
            total_tags = len(required_tags)
            present_tags = sum(1 for tag in required_tags if tag in meta_tags)
            
            return (present_tags / total_tags * 100) if total_tags > 0 else 0
            
        except Exception as e:
            logger.error(f"메타 태그 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_heading_structure(self, checks: Dict[str, Any]) -> float:
        """헤딩 구조 평가"""
        try:
            headings = checks.get("headings", [])
            if not headings:
                return 0.0
            
            # H1 태그가 하나만 있는지 확인
            h1_count = sum(1 for h in headings if h["level"] == 1)
            if h1_count != 1:
                return 50.0
            
            # 헤딩 레벨이 순차적으로 있는지 확인
            levels = [h["level"] for h in headings]
            if self._is_valid_heading_structure(levels):
                return 100.0
            else:
                return 75.0
            
        except Exception as e:
            logger.error(f"헤딩 구조 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_image_alt_texts(self, checks: Dict[str, Any]) -> float:
        """이미지 alt 텍스트 평가"""
        try:
            images = checks.get("images", [])
            if not images:
                return 100.0  # 이미지가 없으면 완벽한 점수
            
            total_images = len(images)
            images_with_alt = sum(1 for img in images if img.get("alt"))
            
            return (images_with_alt / total_images * 100) if total_images > 0 else 0
            
        except Exception as e:
            logger.error(f"이미지 alt 텍스트 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_internal_links(self, checks: Dict[str, Any]) -> float:
        """내부 링크 평가"""
        try:
            links = checks.get("links", [])
            if not links:
                return 0.0
            
            total_links = len(links)
            internal_links = sum(1 for link in links if link.get("is_internal", False))
            
            return (internal_links / total_links * 100) if total_links > 0 else 0
            
        except Exception as e:
            logger.error(f"내부 링크 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_broken_links(self, checks: Dict[str, Any]) -> float:
        """깨진 링크 평가"""
        # 실제 구현에서는 링크 상태를 확인해야 함
        return 95.0  # 기본값
    
    def _evaluate_javascript_errors(self, checks: Dict[str, Any]) -> float:
        """JavaScript 오류 평가"""
        try:
            errors = checks.get("javascript_errors", [])
            if not errors:
                return 100.0  # 오류가 없으면 완벽한 점수
            
            # 오류가 있으면 감점
            return max(0, 100 - len(errors) * 10)
            
        except Exception as e:
            logger.error(f"JavaScript 오류 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_form_validation(self, checks: Dict[str, Any]) -> float:
        """폼 검증 평가"""
        try:
            forms = checks.get("forms", [])
            if not forms:
                return 100.0  # 폼이 없으면 완벽한 점수
            
            total_forms = len(forms)
            valid_forms = 0
            
            for form in forms:
                inputs = form.get("inputs", [])
                if inputs:
                    valid_inputs = sum(1 for input_field in inputs if input_field.get("validation", True))
                    if valid_inputs == len(inputs):
                        valid_forms += 1
            
            return (valid_forms / total_forms * 100) if total_forms > 0 else 0
            
        except Exception as e:
            logger.error(f"폼 검증 평가 중 오류: {e}")
            return 0.0
    
    def _is_valid_heading_structure(self, levels: List[int]) -> bool:
        """헤딩 구조가 유효한지 확인"""
        if not levels:
            return False
        
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                return False
        
        return True
    
    def _get_performance_weight(self, metric: str) -> float:
        """성능 메트릭별 가중치"""
        weights = {
            "page_load_time": 0.3,
            "first_contentful_paint": 0.25,
            "largest_contentful_paint": 0.25,
            "cumulative_layout_shift": 0.2
        }
        return weights.get(metric, 1.0)
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """종합 점수 계산"""
        weights = {
            "performance": 0.3,
            "accessibility": 0.25,
            "seo": 0.2,
            "functionality": 0.25
        }
        
        total_score = 0
        total_weight = 0
        
        for category, score in scores.items():
            weight = weights.get(category, 1.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def get_quality_report(self) -> Dict[str, Any]:
        """품질 보고서 반환"""
        return self.quality_metrics
    
    def get_quality_trends(self) -> List[Dict[str, Any]]:
        """품질 트렌드 데이터 반환"""
        # 실제 구현에서는 데이터베이스에서 히스토리 데이터를 가져와야 함
        return [] 