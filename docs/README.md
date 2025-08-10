# LLM Quality Radar - Google ADK & Playwright MCP 연계 시스템

## 개요

LLM Quality Radar는 Google Application Development Kit (ADK)와 Playwright Model Context Protocol (MCP)를 연계한 혁신적인 웹 자동화 테스트 및 AI 기반 품질 분석 시스템입니다.

## 주요 기능

### 🔧 웹 자동화 테스트
- **Playwright MCP 기반 브라우저 제어**: 안정적이고 빠른 웹 자동화
- **다양한 테스트 시나리오**: 클릭, 입력, 대기, 검증 등
- **스크린샷 캡처**: 테스트 과정의 시각적 증거 수집
- **로그 수집**: 상세한 테스트 실행 로그

### 🤖 AI 기반 품질 분석
- **Google ADK 통합**: Gemini 2.0 Flash 모델 활용
- **자동 품질 점수 계산**: 페이지 로드 시간, JavaScript 오류, 이미지 로딩 등
- **ML 기반 권장사항**: 머신러닝을 통한 개선 제안
- **패턴 감지**: 반복적인 문제점 자동 식별

### 🎯 고급 테스트 기능
- **접근성 테스트**: WCAG 가이드라인 준수 확인
- **반응형 디자인 테스트**: 다양한 뷰포트에서의 동작 확인
- **성능 모니터링**: 실시간 성능 메트릭 수집
- **자동 복구 시스템**: ML 기반 오류 자동 해결

### 📊 종합 분석 및 리포트
- **통합 테스트 리포트**: 모든 테스트 결과를 하나로 통합
- **시각적 증거 캡처**: 요소별 스크린샷 및 페이지 정보
- **권장사항 생성**: 개선을 위한 구체적인 제안
- **트렌드 분석**: 시간에 따른 품질 변화 추적

## 프로젝트 구조

```
llm_quality_radar/
├── 📁 apps/                    # 메인 애플리케이션 파일들
│   ├── app.py                  # 메인 Flask 애플리케이션
│   ├── auto_test_api.py        # FastAPI 기반 테스트 API
│   ├── auto_test_suite.py      # 핵심 자동 테스트 스위트
│   ├── auto_test_suite_extension.py  # 테스트 스위트 확장
│   ├── check_status.py         # 시스템 상태 체크
│   ├── real_time_monitor.py    # 실시간 모니터링
│   └── web_server.py          # 웹 서버
├── 📁 core/                   # 핵심 기능 모듈들
│   ├── auto_healing.py        # 자동 복구 시스템
│   ├── google_adk_integration.py  # Google ADK 통합
│   ├── mcp_client.py         # MCP 클라이언트
│   ├── operational_manager.py # 운영 관리자
│   └── quality_monitor.py    # 품질 모니터
├── 📁 demos/                 # 데모 및 실행 스크립트들
│   ├── playwright_adk_app.py # Playwright ADK 앱
│   ├── playwright_adk_app_google_standard.py
│   ├── run_adk_playwright_demo.py
│   ├── run_playwright_mcp_demo.py
│   ├── run_system.py         # 시스템 실행
│   └── simple_adk_demo.py    # 간단한 데모
├── 📁 docs/                  # 문서 파일들
│   ├── README.md            # 메인 문서
│   ├── README_ADK_PLAYWRIGHT_MCP.md
│   ├── README_AUTO_TEST_SUITE.md
│   ├── README_FIREBASE_DEPLOYMENT.md
│   ├── FINAL_DEMO_RESULTS.md
│   ├── SETUP_SUMMARY.md
│   ├── install_complete.md
│   ├── 프로젝트_개요_및_실행가이드.md
│   └── 프로젝트_발전방향_및_로드맵.md
├── 📁 scripts/              # 배포 및 설정 스크립트들
│   ├── deploy.ps1          # Windows 배포 스크립트
│   ├── deploy.sh           # Linux/Mac 배포 스크립트
│   └── setup_adk_playwright.py  # ADK Playwright 설정
├── 📁 servers/              # 서버 관련 파일들
│   ├── playwright_mcp_server.js  # Playwright MCP 서버
│   └── simple_mcp_server.js     # 간단한 MCP 서버
├── 📁 multi_tool_agent/     # 멀티툴 에이전트
├── 📁 functions/            # Firebase Cloud Functions
├── 📁 public/              # 정적 웹 리소스
├── 📁 config/              # 설정 파일들
├── 📁 utils/               # 유틸리티 함수들
├── package.json           # Node.js 의존성
├── requirements.txt       # Python 의존성
└── firebase.json         # Firebase 설정
```

## 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Playwright     │    │   Google ADK    │
│   (Main Server) │◄──►│     MCP         │◄──►│   Integration   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Agent    │    │  Browser        │    │  AI/ML Models   │
│   (ADK Agent)   │    │  Control        │    │  (Gemini 2.0)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Google Cloud 설정 (선택사항)

Google ADK 기능을 사용하려면:

```bash
# Google Cloud SDK 설치
# https://cloud.google.com/sdk/docs/install

# 프로젝트 설정
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### 3. Playwright MCP 설정

```bash
# Playwright MCP 설치
npm install -g @playwright/mcp

# 브라우저 설치
npx playwright install
```

## 사용법

### 1. 서버 시작

```bash
# 메인 시스템 실행
python demos/run_system.py

# 또는 개별 데모 실행
python demos/playwright_adk_app.py

# FastAPI 기반 테스트 API 서버
python apps/auto_test_api.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. API 엔드포인트

#### 웹 테스트 실행
```bash
curl -X POST "http://localhost:8000/test/web" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_scenarios": [
      {
        "action": "click",
        "selector": "button.login",
        "description": "로그인 버튼 클릭"
      }
    ],
    "quality_analysis": true,
    "accessibility_testing": true
  }'
```

#### 품질 분석
```bash
curl -X POST "http://localhost:8000/analyze/quality" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "include_ai_analysis": true,
    "include_ml_recommendations": true
  }'
```

#### 접근성 테스트
```bash
curl -X POST "http://localhost:8000/test/accessibility" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

### 3. 테스트 실행

```bash
python test_playwright_adk.py
```

## API 문서

서버 실행 후 `http://localhost:8000/docs`에서 자동 생성된 API 문서를 확인할 수 있습니다.

### 주요 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 시스템 상태 확인 |
| `/test/web` | POST | 웹 자동화 테스트 실행 |
| `/analyze/quality` | POST | 웹페이지 품질 분석 |
| `/test/accessibility` | POST | 접근성 테스트 |
| `/test/responsive` | POST | 반응형 디자인 테스트 |
| `/monitor/performance` | POST | 성능 모니터링 |
| `/capture/evidence` | POST | 시각적 증거 캡처 |
| `/heal/issues` | POST | 자동 복구 |
| `/report/{test_id}` | GET | 테스트 리포트 조회 |
| `/status` | GET | 시스템 상태 조회 |
| `/initialize` | POST | 시스템 초기화 |

## 테스트 시나리오 예제

### 기본 웹 테스트
```python
test_scenarios = [
    {
        "action": "wait",
        "selector": "body",
        "description": "페이지 로드 대기"
    },
    {
        "action": "click",
        "selector": "a[href*='about']",
        "description": "About 링크 클릭"
    },
    {
        "action": "assert",
        "selector": "h1",
        "value": "About",
        "description": "페이지 제목 확인"
    }
]
```

### 폼 테스트
```python
test_scenarios = [
    {
        "action": "type",
        "selector": "input[name='username']",
        "value": "testuser",
        "description": "사용자명 입력"
    },
    {
        "action": "type",
        "selector": "input[name='password']",
        "value": "testpass",
        "description": "비밀번호 입력"
    },
    {
        "action": "click",
        "selector": "button[type='submit']",
        "description": "로그인 버튼 클릭"
    }
]
```

## 품질 분석 메트릭

### 자동 계산되는 품질 지표
- **페이지 로드 시간**: 3초 이하 권장
- **JavaScript 오류**: 콘솔 오류 수
- **이미지 로딩**: 실패한 이미지 비율
- **폼 검증**: 필수 필드 누락 여부
- **링크 상태**: 내부/외부 링크 분석

### AI 강화 분석
- **패턴 감지**: 반복적인 문제점 식별
- **성능 예측**: 향후 성능 변화 예측
- **개선 제안**: 구체적인 개선 방안 제시

## 자동 복구 시스템

### ML 기반 오류 해결
- **요소 찾기 실패**: 대체 선택자 자동 시도
- **타이밍 이슈**: 동적 대기 시간 조정
- **네트워크 문제**: 재시도 로직 적용
- **브라우저 호환성**: 크로스 브라우저 대응

## 성능 모니터링

### 실시간 메트릭
- **First Paint (FP)**: 첫 번째 픽셀 렌더링 시간
- **First Contentful Paint (FCP)**: 첫 번째 콘텐츠 렌더링 시간
- **DOM Content Loaded**: DOM 로드 완료 시간
- **Memory Usage**: JavaScript 힙 메모리 사용량

## 접근성 테스트

### WCAG 가이드라인 검사
- **Alt 텍스트**: 이미지 대체 텍스트 확인
- **폼 라벨**: 입력 필드 라벨 연결 확인
- **키보드 네비게이션**: Tab 키 이동 가능성
- **색상 대비**: 텍스트 가독성 확인

## 반응형 디자인 테스트

### 뷰포트별 테스트
- **데스크톱**: 1920x1080
- **태블릿**: 768x1024
- **모바일**: 375x667

### 검사 항목
- **오버플로우**: 뷰포트 벗어남 여부
- **터치 타겟**: 모바일에서 터치 가능한 크기
- **레이아웃**: 반응형 그리드 시스템

## 로깅 및 모니터링

### 구조화된 로깅
```python
# 로그 레벨별 분류
- INFO: 일반적인 작업 진행 상황
- WARNING: 주의가 필요한 상황
- ERROR: 오류 발생
- DEBUG: 상세한 디버깅 정보
```

### Cloud Logging 통합 (Google ADK)
- **구조화된 로그**: JSON 형태로 정리된 로그
- **실시간 모니터링**: Cloud Monitoring 연동
- **알림 설정**: 임계값 기반 알림

## 확장 가능성

### 플러그인 시스템
- **커스텀 테스트**: 사용자 정의 테스트 시나리오
- **외부 도구 연동**: 기존 QA 도구와의 통합
- **CI/CD 파이프라인**: 자동화된 테스트 실행

### 클라우드 확장
- **분산 테스트**: 여러 인스턴스에서 병렬 실행
- **Auto Scaling**: 부하에 따른 자동 확장
- **글로벌 테스트**: 지역별 성능 측정

## 문제 해결

### 일반적인 문제

#### MCP 연결 실패
```bash
# Playwright MCP 재설치
npm uninstall -g @playwright/mcp
npm install -g @playwright/mcp

# 브라우저 재설치
npx playwright install
```

#### Google ADK 초기화 실패
```bash
# 인증 확인
gcloud auth list

# 프로젝트 설정 확인
gcloud config get-value project
```

#### 메모리 부족
```bash
# 브라우저 인스턴스 수 제한
export PLAYWRIGHT_MAX_INSTANCES=2
```

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 라이선스

MIT License

## 지원

- **문서**: [API 문서](http://localhost:8000/docs)
- **이슈**: GitHub Issues
- **토론**: GitHub Discussions

## 변경 로그

### v1.0.0
- Google ADK와 Playwright MCP 연계 시스템 출시
- 웹 자동화 테스트 기능
- AI 기반 품질 분석
- 접근성 및 반응형 테스트
- 자동 복구 시스템
- 성능 모니터링
- 종합 리포트 생성

---

**LLM Quality Radar** - 웹 품질을 AI로 혁신하세요! 🚀 