# Google ADK와 Playwright MCP 통합 가이드

이 가이드는 Google Agent Development Kit (ADK)와 Playwright MCP를 연계하여 웹 자동화 테스트를 수행하는 샘플 환경을 구성하는 방법을 설명합니다.

## 🌟 주요 기능

- **Google ADK LLM Agent**: Gemini 모델을 활용한 지능형 웹 테스트 에이전트
- **Playwright MCP 통합**: 웹 브라우저 자동화를 위한 MCP 도구 연계
- **자연어 명령**: 한국어로 웹 테스트 시나리오를 명령할 수 있음
- **실시간 분석**: 웹페이지 구조 분석, 스크린샷, 접근성 검토
- **포괄적 테스트**: 네비게이션, 폼 상호작용, 접근성 분석 등

## 🔧 시스템 요구사항

### 필수 소프트웨어
- **Python 3.10+**: Google ADK 실행을 위해 필요
- **Node.js 18+**: Playwright MCP 서버 실행을 위해 필요
- **Git**: 소스 코드 관리

### API 키 (둘 중 하나 필요)
1. **Google AI Studio API Key** (개발/테스트용)
   - https://aistudio.google.com/ 에서 생성
2. **Google Cloud Vertex AI** (운영용)
   - Google Cloud 프로젝트와 서비스 계정 필요

## 📦 설치 및 설정

### 1. 환경 설정 스크립트 실행

```bash
# 자동 설정 스크립트 실행
python setup_adk_playwright.py
```

### 2. API 키 설정

`.env` 파일을 생성하고 다음 중 하나를 설정:

#### 옵션 A: Google AI Studio (간단, 개발용)
```bash
# Google AI Studio API 키 사용
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-google-ai-studio-api-key
```

#### 옵션 B: Vertex AI (운영용)
```bash
# Vertex AI 사용
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 3. 수동 의존성 설치 (필요시)

```bash
# Python 패키지 설치
pip install -r requirements.txt

# Playwright MCP 확인 (자동 설치됨)
npx @playwright/mcp@latest --help
```

## 🚀 사용 방법

### 1. 간단한 데모 실행

```bash
# 기본 데모 실행
python run_adk_playwright_demo.py
```

### 2. 전체 테스트 스위트 실행

```bash
# 포괄적인 테스트 실행
python test_adk_playwright_mcp.py
```

### 3. ADK Web UI 사용

```bash
# ADK 웹 인터페이스 시작
cd multi_tool_agent
adk web
```

그 후 브라우저에서 http://localhost:8000 접속

## 🧪 테스트 시나리오

### 1. 기본 웹 탐색 테스트
- Google 홈페이지 접속
- 검색 수행
- 스크린샷 촬영
- 페이지 구조 분석

### 2. 폼 상호작용 테스트
- Example.com 접속
- 상호작용 가능한 요소 식별
- 폼 요소 분석

### 3. 접근성 분석 테스트
- GitHub 사이트 분석
- 접근성 트리 검토
- 개선점 제안

## 📁 프로젝트 구조

```
llm_quality_radar/
├── config/
│   └── adk_config.py              # ADK 설정 관리
├── multi_tool_agent/
│   ├── __init__.py
│   └── adk_playwright_mcp_agent.py # 메인 에이전트
├── utils/
│   └── logger.py                  # 로깅 유틸리티
├── core/                          # 기존 핵심 모듈들
├── test_adk_playwright_mcp.py     # 전체 테스트 스위트
├── run_adk_playwright_demo.py     # 간단한 데모
├── setup_adk_playwright.py       # 환경 설정 스크립트
├── requirements.txt               # Python 의존성
├── .env.example                   # 환경 설정 예시
└── README_ADK_PLAYWRIGHT_MCP.md   # 이 문서
```

## 💡 핵심 구성 요소

### 1. ADKPlaywrightMCPAgent 클래스
- Google ADK LLM Agent와 Playwright MCP 통합
- MCPToolset을 통한 브라우저 도구 제공
- 자연어 명령 처리

### 2. 사용 가능한 Playwright MCP 도구들
- `browser_navigate`: 웹사이트 이동
- `browser_snapshot`: 페이지 구조 분석
- `browser_click`: 요소 클릭
- `browser_type`: 텍스트 입력
- `browser_take_screenshot`: 스크린샷 촬영
- `browser_wait_for`: 대기
- `browser_close`: 브라우저 종료

### 3. 설정 관리
- 환경별 설정 분리
- API 키 보안 관리
- 브라우저 옵션 설정

## 🔍 주요 웹 검색 참고 자료

이 샘플은 다음 자료들을 참고하여 구성되었습니다:

1. **Google ADK MCP 문서**: https://google.github.io/adk-docs/tools/mcp-tools/
2. **Playwright MCP 서버**: https://www.npmjs.com/package/@playwright/mcp
3. **Model Context Protocol**: https://modelcontextprotocol.io/docs/concepts/architecture
4. **Medium 블로그 포스트**: ADK와 MCP 통합 방법론

## 🛠️ 문제 해결

### 일반적인 오류들

1. **API 키 오류**
   ```
   AuthError: Invalid API key
   ```
   - `.env` 파일의 API 키 확인
   - Google AI Studio 또는 Vertex AI 설정 확인

2. **Node.js 오류**
   ```
   FileNotFoundError: node
   ```
   - Node.js 설치: https://nodejs.org/

3. **MCP 서버 연결 오류**
   ```
   MCPError: Failed to connect
   ```
   - Playwright MCP 패키지 설치 확인
   - 방화벽 설정 확인

### 디버깅 팁

1. **로그 레벨 조정**
   ```bash
   export LOG_LEVEL=DEBUG
   ```

2. **헤드리스 모드 해제** (브라우저 창 보기)
   ```bash
   # .env 파일에서
   PLAYWRIGHT_MCP_HEADLESS=false
   ```

## 🤝 기여 방법

1. 이슈 리포트: 버그나 개선사항 제안
2. 풀 리퀘스트: 코드 개선 기여
3. 문서 개선: 가이드나 예제 추가

## 📄 라이선스

이 프로젝트는 오픈소스 라이선스를 따릅니다.

## 🙋‍♂️ 도움말

문제가 발생하거나 질문이 있으시면:

1. 이 README의 문제 해결 섹션 확인
2. GitHub Issues에 문제 리포트
3. 로그 파일과 함께 상세한 오류 내용 공유

---

**Happy Testing with Google ADK & Playwright MCP! 🎉**