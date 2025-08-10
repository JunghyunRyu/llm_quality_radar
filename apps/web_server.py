#!/usr/bin/env python3
"""
LLM Quality Radar 웹 서버
정적 파일 서빙 및 API 엔드포인트 제공
"""

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import os
import sys
import asyncio
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging

from utils.logger import setup_logger, suppress_log_messages

# .env 파일 로드 (루트 디렉토리에서)
# 현재 파일의 상위 디렉토리(프로젝트 루트)에서 .env 파일 찾기
current_dir = Path(__file__).parent
root_dir = current_dir.parent
env_file = root_dir / ".env"

if env_file.exists():
    load_dotenv(env_file)
    # 초기 로깅 준비 전이므로 print 병행
    print(f"✅ .env 파일 로드 완료: {env_file}")
else:
    print(f"⚠️ .env 파일을 찾을 수 없습니다: {env_file}")
    # 일반적인 로드도 시도
    load_dotenv()

# 환경 변수 확인 (디버깅용)
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    print(f"✅ GOOGLE_API_KEY 로드됨 (길이: {len(google_api_key)})")
else:
    print("❌ GOOGLE_API_KEY를 찾을 수 없습니다")

# 프로젝트 루트 경로 추가
sys.path.append(".")

# Playwright ADK Agent import
from multi_tool_agent.playwright_adk_agent_google_standard import (
    PlaywrightADKAgentGoogleStandard,
)

# 애플리케이션 로거 설정 (환경 변수 LOG_LEVEL, LOG_FILE 지원)
logger = setup_logger(
    "web_server", level=os.getenv("LOG_LEVEL", "INFO"), log_file=os.getenv("LOG_FILE")
)

# 노이즈 억제: ADK 경고 등 특정 문자열을 포함하는 로그 숨김
suppress_log_messages(
    substrings=[
        "auth_config or auth_config.auth_scheme is missing",
        "Will skip authentication.Using FunctionTool instead",
    ],
    logger_names=["", "google_adk"],  # root 및 ADK 네임스페이스
)

# 웹 애플리케이션 초기화
app = FastAPI(
    title="LLM Quality Radar",
    description="AI 기반 웹 품질 분석 시스템",
    version="1.0.0",
)


# API 모델 정의
class WebTestRequest(BaseModel):
    url: str
    test_type: str = "basic"  # basic, quality, accessibility, responsive, comprehensive
    custom_instruction: Optional[str] = None


class WebTestResponse(BaseModel):
    test_id: str
    status: str
    execution_time: float
    events_count: int
    result_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# 글로벌 에이전트 인스턴스 (재사용을 위해)
playwright_agent: Optional[PlaywrightADKAgentGoogleStandard] = None

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 요청/응답 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = os.urandom(4).hex()
    logger.info(
        "REQ %s %s %s from %s",
        request_id,
        request.method,
        request.url.path,
        request.client.host if request.client else "-",
    )
    try:
        response = await call_next(request)
        logger.info(
            "RES %s %s %s -> %s",
            request_id,
            request.method,
            request.url.path,
            getattr(response, "status_code", "-"),
        )
        return response
    except Exception:
        logger.exception("REQ %s 처리 중 예외", request_id)
        raise


# 정적 파일 마운트
static_dir = Path("static")
public_dir = Path("public")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
elif public_dir.exists():
    app.mount("/static", StaticFiles(directory="public"), name="static")


async def get_playwright_agent():
    """Playwright Agent 인스턴스 가져오기 (싱글톤 패턴)"""
    global playwright_agent
    if playwright_agent is None:
        logger.info("PlaywrightADKAgentGoogleStandard 인스턴스 생성")
        playwright_agent = PlaywrightADKAgentGoogleStandard()
        await playwright_agent.create_session()
        logger.info("PlaywrightADKAgentGoogleStandard 세션 준비 완료")
    return playwright_agent


async def cleanup_playwright_agent():
    """Playwright Agent 정리"""
    global playwright_agent
    if playwright_agent:
        try:
            # 안전한 종료를 위해 타임아웃 설정
            logger.info("PlaywrightADKAgentGoogleStandard 종료 시도")
            await asyncio.wait_for(playwright_agent.close(), timeout=5.0)
            logger.info("PlaywrightADKAgentGoogleStandard 종료 완료")
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning("에이전트 정리 중 오류(무시됨): %s", e, exc_info=True)
        finally:
            playwright_agent = None


async def generate_test_summary(instruction: str, url: str, test_type: str) -> str:
    """AI로 테스트 요약 생성"""
    try:
        # 간단한 룰 기반 요약 (나중에 AI 모델로 대체 가능)
        test_type_names = {
            "basic": "기본 테스트",
            "quality": "품질 분석",
            "accessibility": "접근성 테스트",
            "responsive": "반응형 테스트",
            "comprehensive": "종합 테스트",
        }

        # URL에서 도메인 추출
        from urllib.parse import urlparse

        domain = urlparse(url).netloc or url

        test_name = test_type_names.get(test_type, "웹 테스트")
        summary = f"{domain} {test_name}"

        return summary

    except Exception as e:
        return f"{test_type} 테스트"


def parse_test_events(events: List[Any]) -> Dict[str, Any]:
    """이벤트에서 실제 내용 추출하여 구조화"""
    try:
        parsed = {
            "user_interactions": [],
            "model_responses": [],
            "tool_executions": [],
            "screenshots": [],
        }

        for event in events:
            try:
                # 1) 구조화된 이벤트 객체에서 직접 스크린샷 추출 시도
                screenshot_from_obj = extract_screenshot_from_event_obj(event)
                if screenshot_from_obj:
                    parsed["screenshots"].append(screenshot_from_obj)

                # 나머지는 문자열 기반 파싱 폴백
                event_str = str(event)

                # User Content 추출
                if "role='user'" in event_str:
                    user_content = extract_content_text(event_str)
                    if user_content:
                        parsed["user_interactions"].append(user_content)

                # Model Content 추출
                elif "role='model'" in event_str:
                    model_content = extract_content_text(event_str)
                    if model_content:
                        parsed["model_responses"].append(model_content)

                # Tool 실행 내용 추출
                if "browser_" in event_str:
                    tool_content = extract_tool_content(event_str)
                    if tool_content:
                        parsed["tool_executions"].append(tool_content)

                # 스크린샷 관련 내용 추출
                if "screenshot" in event_str.lower():
                    screenshot_info = extract_screenshot_info(event_str)
                    if screenshot_info:
                        parsed["screenshots"].append(screenshot_info)

            except Exception as e:
                continue

        return parsed

    except Exception as e:
        return {"error": str(e)}


def extract_screenshot_from_event_obj(event: Any) -> Optional[Dict[str, Any]]:
    """이벤트 객체에서 스크린샷 데이터(베이스64/파일경로)를 직접 추출.
    Google ADK + MCP의 함수 응답 구조를 고려하여 일반적인 경로를 우선 탐색하고,
    실패 시 안전하게 None을 반환한다.
    """
    try:
        # ADK 이벤트는 대개 content.parts[...].function_response.response.result.content 형태를 가진다.
        parts = getattr(event, "parts", None)
        if parts and isinstance(parts, (list, tuple)):
            for part in parts:
                function_response = getattr(part, "function_response", None)
                if not function_response:
                    continue
                response = getattr(function_response, "response", None)

                # response가 dict이거나 객체일 수 있음
                result = None
                if isinstance(response, dict):
                    result = response.get("result")
                else:
                    result = getattr(response, "result", None)

                contents = None
                if isinstance(result, dict):
                    contents = result.get("content")
                else:
                    contents = getattr(result, "content", None)

                if contents and isinstance(contents, (list, tuple)):
                    for item in contents:
                        # 1) inline_data(mime_type, data)
                        inline_data = getattr(item, "inline_data", None)
                        if inline_data:
                            mime = (
                                getattr(inline_data, "mime_type", "image/png")
                                or "image/png"
                            )
                            data = getattr(inline_data, "data", None)
                            if isinstance(data, str) and len(data) > 100:
                                return {
                                    "status": "captured",
                                    "description": "페이지 스크린샷",
                                    "image_data": f"data:{mime};base64,{data}",
                                }

                        # 2) file_data(file_uri)
                        file_data = getattr(item, "file_data", None)
                        if file_data:
                            file_uri = getattr(file_data, "file_uri", None) or getattr(
                                file_data, "uri", None
                            )
                            if isinstance(file_uri, str) and file_uri:
                                return {
                                    "status": "captured",
                                    "description": "페이지 스크린샷 파일",
                                    "file_path": file_uri,
                                }

                        # 3) text 안에 data URL이 들어있는 경우
                        text_value = getattr(item, "text", None)
                        if isinstance(text_value, str) and "data:image" in text_value:
                            import re

                            m = re.search(
                                r"(data:image/[^;]+;base64,[A-Za-z0-9+/=]+)", text_value
                            )
                            if m:
                                return {
                                    "status": "captured",
                                    "description": "페이지 스크린샷",
                                    "image_data": m.group(1),
                                }

        return None
    except Exception:
        return None


def extract_content_text(event_str: str) -> Optional[str]:
    """이벤트 문자열에서 실제 텍스트 내용 추출"""
    try:
        # text= 패턴으로 텍스트 추출
        import re

        text_match = re.search(r'text="""(.+?)"""', event_str, re.DOTALL)
        if text_match:
            return text_match.group(1).strip()

        text_match = re.search(r'text="(.+?)"', event_str)
        if text_match:
            return text_match.group(1).strip()

        return None
    except:
        return None


def extract_tool_content(event_str: str) -> Optional[str]:
    """툴 실행 내용 추출"""
    try:
        import re

        # browser_ 함수 호출 패턴 추출
        tool_match = re.search(r"(browser_\w+\.run\([^)]+\))", event_str)
        if tool_match:
            return tool_match.group(1)
        return None
    except:
        return None


def extract_screenshot_info(event_str: str) -> Optional[Dict[str, Any]]:
    """스크린샷 정보 추출 (강화된 버전)"""
    try:
        import re

        # 스크린샷 관련 키워드 확장
        screenshot_keywords = [
            "screenshot",
            "take_screenshot",
            "capture",
            "image",
            "스크린샷",
            "캡처",
        ]
        has_screenshot = any(
            keyword in event_str.lower() for keyword in screenshot_keywords
        )

        if has_screenshot:
            print(f"🔍 스크린샷 관련 이벤트 발견: {event_str[:200]}...")  # 디버깅

            screenshot_info = {
                "status": "captured",
                "description": "페이지 스크린샷을 촬영했습니다",
                "raw_event": event_str[:500],  # 디버깅용
            }

            # 더 강화된 base64 데이터 추출 패턴
            patterns = [
                r"data:image/[^;]*;base64,([A-Za-z0-9+/=]+)",
                r'"data:image/[^"]*"',  # 전체 data URL
                r'"([A-Za-z0-9+/=]{200,})"',  # 매우 긴 base64 문자열
                r"base64[,:\s]*([A-Za-z0-9+/=]{100,})",
                r'image[^"]*"([A-Za-z0-9+/=]{100,})"',
                r"\/9j\/[A-Za-z0-9+/=]+",  # JPEG base64 시작 패턴
                r"iVBORw0KGgo[A-Za-z0-9+/=]+",  # PNG base64 시작 패턴
                r'result[^"]*"([A-Za-z0-9+/=]{100,})"',
            ]

            for i, pattern in enumerate(patterns):
                match = re.search(pattern, event_str, re.DOTALL)
                if match:
                    if "data:image" in match.group(0):
                        # 완전한 data URL인 경우
                        screenshot_info["image_data"] = match.group(0).strip('"')
                        print(
                            f"✅ 패턴 {i+1}로 완전한 data URL 추출 성공: {len(match.group(0))}자"
                        )
                    else:
                        # base64 데이터만 있는 경우
                        data = match.group(1) if match.groups() else match.group(0)
                        if len(data) > 100:
                            screenshot_info["image_data"] = (
                                f"data:image/png;base64,{data}"
                            )
                            print(
                                f"✅ 패턴 {i+1}로 base64 데이터 추출 성공: {len(data)}자"
                            )
                    break

            # 파일 경로 추출 (확장)
            file_patterns = [
                r'screenshot[^"]*\.(?:png|jpg|jpeg)',
                r'[^"\s]*\.(?:png|jpg|jpeg)',
                r'file[^"]*\.(?:png|jpg|jpeg)',
                r'path[^"]*\.(?:png|jpg|jpeg)',
            ]

            for pattern in file_patterns:
                file_match = re.search(pattern, event_str, re.IGNORECASE)
                if file_match:
                    screenshot_info["file_path"] = file_match.group(0)
                    print(f"🗂️ 파일 경로 발견: {file_match.group(0)}")
                    break

            # 아무것도 추출되지 않은 경우 기본 이미지 제공
            if (
                "image_data" not in screenshot_info
                and "file_path" not in screenshot_info
            ):
                print("⚠️ 스크린샷 데이터를 추출하지 못했습니다")
                # 기본 placeholder 이미지 (작은 투명 PNG)
                placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                screenshot_info["image_data"] = f"data:image/png;base64,{placeholder}"
                screenshot_info["description"] = (
                    "스크린샷 데이터를 추출할 수 없었습니다"
                )

            return screenshot_info

        return None

    except Exception as e:
        print(f"❌ 스크린샷 추출 중 오류: {e}")
        return None


def structure_ai_responses(responses: List[str]) -> List[Dict[str, Any]]:
    """AI 응답을 질문-답변 형태로 구조화"""
    try:
        structured = []

        for response in responses:
            if not response:
                continue

            # 긴 텍스트를 의미있는 섹션으로 분할
            sections = split_into_sections(response)

            for section in sections:
                if len(section.strip()) > 50:  # 너무 짧은 섹션은 제외
                    qa_item = create_qa_item(section)
                    if qa_item:
                        structured.append(qa_item)

        return structured

    except Exception as e:
        return [{"question": "분석 결과", "answer": str(responses), "type": "text"}]


def split_into_sections(text: str) -> List[str]:
    """텍스트를 의미있는 섹션으로 분할"""
    try:
        import re

        # 기술적 내용 필터링
        text = filter_technical_content(text)

        # 문장 단위로 분할하고 짧게 유지
        sentences = re.split(r"[.!?]\s+", text)
        sections = []

        current_section = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 문장이 너무 길면 더 작은 단위로 분할하되, 내용 유지
            if len(sentence) > 150:
                # 콜론이나 세미콜론으로 분할 시도
                sub_sentences = re.split(r"[:\;]\s*", sentence)
                for sub in sub_sentences:
                    sub = sub.strip()
                    if len(sub) > 30:  # 충분한 내용이 있는 경우만
                        if len(current_section) + len(sub) < 200:
                            current_section += sub + ". "
                        else:
                            if current_section.strip():
                                sections.append(current_section.strip())
                            current_section = sub + ". "
            else:
                if len(sentence) > 30:  # 의미있는 길이의 문장만
                    if len(current_section) + len(sentence) < 200:
                        current_section += sentence + ". "
                    else:
                        if current_section.strip():
                            sections.append(current_section.strip())
                        current_section = sentence + ". "

        if current_section.strip():
            sections.append(current_section.strip())

        return sections[:6]  # 최대 6개로 늘림

    except:
        return [text]


def filter_technical_content(text: str) -> str:
    """기술적 내용 필터링"""
    try:
        import re

        # 필터링할 패턴들 (기술적 내용 제거)
        filter_patterns = [
            r"현재 API에는.*?없습니다",
            r"API 제한.*?있습니다",
            r"링크 클릭 후.*?어려울 수 있습니다",
            r"이 점을 감안하고.*?분석.*?습니다",
            r"browser_.*?\)",
            r"스냅샷.*?찍으면.*?있습니다",
            r"제한 사항.*?어려울 수 있습니다",
            r"\*\*\d+단계:.*?\*\*",  # **1단계: 웹사이트 접속** 같은 내용
            r"다음 단계를 따르겠습니다",
            r"함수를 사용하여",
            r"`.*?`",  # 백틱으로 감싼 코드
            r"먼저.*?함수를.*?습니다",
            r"이제.*?함수를.*?습니다",
            r"진행하겠습니다",
            r"분석을 진행하겠습니다",
            r"캡처합니다",
            r"사용합니다",
            r"검색창에.*?입력하고.*?검색합니다",
            r"클릭하여.*?확인합니다",
            r"버튼을 클릭하여",
            r"이동하는지 확인합니다",
            r"로드되는지 확인합니다",
            r"Playwright.*?입력하고",
            r"네이버 웹사이트에 성공적으로 접속했습니다",
            r"네이버 홈페이지의 주요 기능들을 살펴보고",
            r"각 기능이 정상적으로 작동하는지 확인합니다",
        ]

        for pattern in filter_patterns:
            text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

        # 연속된 공백 정리
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    except:
        return text


def create_qa_item(section: str) -> Optional[Dict[str, Any]]:
    """섹션을 질문-답변 형태로 변환"""
    try:
        import re

        # 더 구체적인 키워드 기반 질문 생성
        keywords_map = {
            "검색": "🔍 검색 기능은 어떤가요?",
            "링크": "🔗 주요 링크들이 잘 작동하나요?",
            "메일": "📧 메일 서비스 접근은 어떤가요?",
            "뉴스": "📰 뉴스 기능은 어떤가요?",
            "로딩": "⚡ 페이지 로딩은 빠른가요?",
            "성능": "🚀 전체적인 성능은 어떤가요?",
            "디자인": "🎨 디자인과 UI는 어떤가요?",
            "접근성": "♿ 접근성은 좋은가요?",
            "오류": "❌ 발견된 문제점이 있나요?",
            "기능": "⚙️ 주요 기능들이 잘 작동하나요?",
            "사용성": "👆 사용하기 편한가요?",
            "품질": "✨ 전체적인 품질은 어떤가요?",
            "SEO": "📈 SEO 최적화는 어떤가요?",
            "모바일": "📱 모바일에서도 잘 보이나요?",
            "보안": "🔒 보안은 안전한가요?",
        }

        question = "📋 분석 결과"
        for keyword, q in keywords_map.items():
            if keyword in section:
                question = q
                break

        # 답변 정리 (원래 길이 유지)
        answer = section.strip()

        # 너무 길면 적당히 자르되, 충분한 내용 유지
        if len(answer) > 200:
            # 첫 두 문장 정도 사용
            sentences = answer.split(".")
            if len(sentences) >= 2:
                answer = sentences[0] + ". " + sentences[1] + "."
            else:
                answer = answer[:200] + "..."

        # 코드 블록 감지
        if "```" in section or "browser_" in section:
            return {"question": "🛠️ 실행된 테스트", "answer": answer, "type": "code"}

        return {"question": question, "answer": answer, "type": "text"}

    except:
        return None


@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse("static/index.html")


@app.get("/dashboard")
async def dashboard():
    """대시보드 페이지"""
    return FileResponse("static/dashboard.html")


@app.get("/api/status")
async def get_status():
    """시스템 상태 확인"""
    return {
        "status": "running",
        "version": "1.0.0",
        "features": [
            "웹 자동화 테스트",
            "AI 기반 품질 분석",
            "실시간 모니터링",
            "접근성 테스트",
            "반응형 디자인 테스트",
        ],
    }


@app.get("/api/features")
async def get_features():
    """주요 기능 목록"""
    return {
        "features": [
            {
                "id": "ai-analysis",
                "title": "AI 기반 품질 분석",
                "description": "Gemini 2.0 Flash 모델을 활용한 지능형 웹페이지 품질 분석",
                "icon": "fas fa-robot",
                "status": "available",
            },
            {
                "id": "automation",
                "title": "자동화 테스트",
                "description": "Playwright MCP 기반의 안정적이고 빠른 웹 자동화 테스트",
                "icon": "fas fa-cogs",
                "status": "available",
            },
            {
                "id": "monitoring",
                "title": "실시간 모니터링",
                "description": "웹 애플리케이션의 성능과 품질을 실시간으로 모니터링",
                "icon": "fas fa-chart-line",
                "status": "available",
            },
            {
                "id": "accessibility",
                "title": "접근성 테스트",
                "description": "WCAG 가이드라인을 준수하는 접근성 테스트",
                "icon": "fas fa-universal-access",
                "status": "available",
            },
            {
                "id": "responsive",
                "title": "반응형 테스트",
                "description": "다양한 디바이스와 뷰포트에서의 반응형 디자인 테스트",
                "icon": "fas fa-mobile-alt",
                "status": "available",
            },
            {
                "id": "auto-healing",
                "title": "자동 복구",
                "description": "ML 기반 자동 복구 시스템으로 테스트 실패 시 지능적으로 문제 해결",
                "icon": "fas fa-magic",
                "status": "development",
            },
        ]
    }


@app.get("/api/demo")
async def get_demo_info():
    """데모 정보"""
    return {
        "demo_urls": [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
        ],
        "test_scenarios": [
            {
                "name": "기본 페이지 로드 테스트",
                "description": "페이지 로딩 및 기본 요소 확인",
                "scenarios": [
                    {
                        "action": "wait",
                        "selector": "body",
                        "description": "페이지 로드 대기",
                    },
                    {
                        "action": "assert",
                        "selector": "title",
                        "description": "페이지 제목 확인",
                    },
                ],
            },
            {
                "name": "검색 기능 테스트",
                "description": "검색 입력 및 결과 확인",
                "scenarios": [
                    {
                        "action": "wait",
                        "selector": "input[name='q']",
                        "description": "검색 입력창 대기",
                    },
                    {
                        "action": "type",
                        "selector": "input[name='q']",
                        "value": "test",
                        "description": "검색어 입력",
                    },
                    {
                        "action": "click",
                        "selector": "input[type='submit']",
                        "description": "검색 버튼 클릭",
                    },
                ],
            },
        ],
    }


@app.post("/api/test/run", response_model=WebTestResponse)
async def run_web_test(request: WebTestRequest):
    """웹 테스트 실행"""
    try:
        # Playwright Agent 가져오기
        agent = await get_playwright_agent()

        # 테스트 타입에 따른 명령어 생성
        if request.custom_instruction:
            instruction = request.custom_instruction
        else:
            test_instructions = {
                "basic": f"{request.url}에 접속해서 페이지가 로드되는지 확인하고 스크린샷을 찍어주세요.",
                "quality": f"{request.url}에 접속해서 페이지 품질을 분석해주세요. 로딩 속도, UI 요소, 에러 여부를 확인해주세요.",
                "accessibility": f"{request.url}에 접속해서 접근성 테스트를 수행해주세요. 키보드 네비게이션, 스크린 리더 호환성, 색상 대비를 확인해주세요.",
                "responsive": f"{request.url}에 접속해서 반응형 디자인을 테스트해주세요. 데스크톱, 태블릿, 모바일 뷰포트에서 확인해주세요.",
                "comprehensive": f"{request.url}에 접속해서 종합적인 품질 분석을 수행해주세요. 기능, 성능, 사용성, 기술적 품질을 모두 확인해주세요.",
            }
            instruction = test_instructions.get(
                request.test_type, test_instructions["basic"]
            )

        logger.info(
            "/api/test/run 요청: url=%s type=%s custom=%s",
            request.url,
            request.test_type,
            bool(request.custom_instruction),
        )
        logger.debug("생성된 지시문: %s", instruction)

        # 테스트 실행 (30초 타임아웃)
        import asyncio

        try:
            result = await asyncio.wait_for(
                agent.run_web_test_natural_language(instruction), timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning(
                "테스트 타임아웃: url=%s type=%s", request.url, request.test_type
            )
            raise HTTPException(
                status_code=408,
                detail="테스트 실행 시간이 30초를 초과했습니다. 더 간단한 테스트를 시도해보세요.",
            )

        # AI로 테스트 요약 생성
        test_summary = await generate_test_summary(
            instruction, request.url, request.test_type
        )

        # 이벤트에서 실제 내용 추출
        parsed_results = parse_test_events(result.get("events", []))

        logger.info(
            "테스트 완료: id=%s status=%s time=%.2fs events=%d screenshots=%d",
            result.get("test_id"),
            result.get("status"),
            result.get("execution_time", 0.0),
            result.get("events_count", 0),
            len(parsed_results.get("screenshots", [])),
        )

        # AI 응답을 Q&A 형태로 구조화
        structured_qa = structure_ai_responses(
            parsed_results.get("model_responses", [])
        )

        return WebTestResponse(
            test_id=result.get("test_id", "unknown"),
            status=result.get("status", "unknown"),
            execution_time=result.get("execution_time", 0.0),
            events_count=result.get("events_count", 0),
            result_summary={
                "url": request.url,
                "test_type": request.test_type,
                "test_summary": test_summary,
                "instruction": instruction,
                "parsed_results": parsed_results,
                "structured_qa": structured_qa,
                "raw_events": result.get("events", []),
            },
        )

    except Exception as e:
        logger.exception(
            "/api/test/run 처리 실패: url=%s type=%s", request.url, request.test_type
        )
        return WebTestResponse(
            test_id="error",
            status="failed",
            execution_time=0.0,
            events_count=0,
            error=str(e),
        )


@app.get("/api/test/types")
async def get_test_types():
    """사용 가능한 테스트 타입 목록"""
    return {
        "test_types": [
            {
                "id": "basic",
                "name": "기본 테스트",
                "description": "페이지 로딩 및 기본 요소 확인",
                "icon": "fas fa-play-circle",
            },
            {
                "id": "quality",
                "name": "품질 분석",
                "description": "웹페이지 전반적인 품질 분석",
                "icon": "fas fa-search",
            },
            {
                "id": "accessibility",
                "name": "접근성 테스트",
                "description": "WCAG 가이드라인 기반 접근성 테스트",
                "icon": "fas fa-universal-access",
            },
            {
                "id": "responsive",
                "name": "반응형 테스트",
                "description": "다양한 디바이스에서의 반응형 디자인 테스트",
                "icon": "fas fa-mobile-alt",
            },
            {
                "id": "comprehensive",
                "name": "종합 테스트",
                "description": "모든 영역을 포함한 종합적인 품질 테스트",
                "icon": "fas fa-cogs",
            },
        ]
    }


@app.delete("/api/test/cleanup")
async def cleanup_test_agent():
    """테스트 에이전트 정리"""
    try:
        await cleanup_playwright_agent()
        return {"status": "success", "message": "테스트 에이전트가 정리되었습니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """메인 함수"""
    # static 디렉토리가 없으면 생성
    if not os.path.exists("static"):
        os.makedirs("static")
        logger.info("static 디렉토리를 생성했습니다.")

    # 서버 실행
    logger.info("웹 서버 시작: 0.0.0.0:8080, reload=%s", True)
    uvicorn.run(
        "web_server:app", host="0.0.0.0", port=8080, reload=True, log_level="info"
    )


if __name__ == "__main__":
    main()
