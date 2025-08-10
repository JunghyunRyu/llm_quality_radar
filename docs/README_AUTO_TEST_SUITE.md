# 자동 테스트 스위트 (Auto Test Suite)

## 🚀 개요

자동 테스트 스위트는 웹 페이지 분석부터 테스트 케이스 자동 생성, 자동화 스크립트 생성, 실행, 모니터링까지 모든 과정을 자동화하는 종합적인 웹 자동화 테스트 도구입니다.

## ✨ 주요 기능

### 🔍 **웹 페이지 자동 분석**
- **페이지 구조 분석**: 헤딩, 단락, 이미지, 링크, 버튼, 폼 등 모든 요소 자동 감지
- **상호작용 요소 분석**: 클릭 가능한 요소, 호버 효과, 포커스 가능한 요소 식별
- **성능 메트릭 수집**: 페이지 로드 시간, 메모리 사용량, DOM 요소 수 등
- **접근성 분석**: Alt 텍스트, ARIA 라벨, 키보드 네비게이션 등
- **SEO 분석**: 메타 태그, 헤딩 구조, 이미지 최적화 등

### 🧪 **테스트 케이스 자동 생성**
- **기능 테스트**: 페이지 로드, 클릭, 입력, 폼 제출 등
- **접근성 테스트**: Alt 텍스트 확인, 키보드 네비게이션 등
- **성능 테스트**: 로드 시간 측정, 메모리 사용량 모니터링 등
- **스마트 선택자 생성**: ID, 클래스, 속성 기반 최적화된 선택자 자동 생성

### 📜 **자동화 스크립트 생성**
- **Python Playwright 스크립트**: 완전한 실행 가능한 테스트 스크립트
- **JSON 테스트 데이터**: 구조화된 테스트 데이터
- **다양한 언어 지원**: Python, JavaScript 등

### ⚡ **테스트 자동 실행**
- **MCP 기반 실행**: Playwright MCP를 통한 안정적인 브라우저 제어
- **실시간 진행 상황**: 단계별 진행률 및 상태 모니터링
- **오류 처리**: 자동 재시도 및 오류 복구

### 📊 **성능 모니터링 및 메트릭**
- **실시간 성능 측정**: 페이지 로드 시간, 메모리 사용량 등
- **네트워크 상태 모니터링**: 연결 상태, 다운로드 속도 등
- **JavaScript 오류 추적**: 콘솔 오류 및 예외 처리

### 📋 **종합 리포트 생성**
- **테스트 결과 요약**: 성공률, 실행 시간, 오류 분석
- **성능 분석**: 성능 메트릭 및 개선 권장사항
- **개선 제안**: 접근성, SEO, 성능 개선 방안

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │  Auto Test      │    │  Playwright     │
│   (Web Server)  │◄──►│  Suite Core     │◄──►│     MCP         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Test Case      │    │  Browser        │
│   (Frontend)    │    │  Generator      │    │  Control        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 설치 및 설정

### 1. 의존성 설치

```bash
# 저장소 클론
git clone <repository-url>
cd llm_quality_radar

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Python 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
npx playwright install
```

### 2. Google Cloud 설정 (선택사항)

```bash
# Google Cloud SDK 설치
# https://cloud.google.com/sdk/docs/install

# 환경 변수 설정
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

## 🚀 사용 방법

### 1. API 서버 시작

```bash
# 자동 테스트 스위트 API 서버 시작
python auto_test_api.py
```

서버가 `http://localhost:8001`에서 실행됩니다.

### 2. 웹 인터페이스 사용

브라우저에서 `http://localhost:8001/docs`에 접속하여 자동 생성된 API 문서를 확인할 수 있습니다.

### 3. API 엔드포인트

#### 완전한 자동 테스트 워크플로우 실행

```bash
curl -X POST "http://localhost:8001/test/auto" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_type": "comprehensive",
    "include_monitoring": true,
    "generate_scripts": true
  }'
```

#### 웹 페이지 분석만 수행

```bash
curl -X POST "http://localhost:8001/test/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_type": "comprehensive"
  }'
```

#### 테스트 케이스 생성만 수행

```bash
curl -X POST "http://localhost:8001/test/generate-cases" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_type": "comprehensive"
  }'
```

#### 자동화 스크립트 생성만 수행

```bash
curl -X POST "http://localhost:8001/test/generate-scripts" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_type": "comprehensive"
  }'
```

#### 성능 모니터링만 수행

```bash
curl -X POST "http://localhost:8001/test/monitor" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com",
    "test_type": "comprehensive"
  }'
```

### 4. Python 코드로 직접 사용

```python
import asyncio
from auto_test_suite_extension import AutoTestSuiteExtension

async def main():
    # 자동 테스트 스위트 인스턴스 생성
    auto_suite = AutoTestSuiteExtension()
    
    # 완전한 테스트 워크플로우 실행
    result = await auto_suite.run_complete_test_workflow(
        url="https://www.google.com",
        test_type="comprehensive"
    )
    
    # 결과 출력
    print(f"워크플로우 ID: {result['workflow_id']}")
    print(f"상태: {result['status']}")
    print(f"실행 시간: {result['execution_time']:.2f}초")
    
    if result['status'] == 'completed':
        summary = result['final_report']['summary']
        print(f"총 테스트: {summary['total_tests']}")
        print(f"성공: {summary['passed_tests']}")
        print(f"실패: {summary['failed_tests']}")
        print(f"성공률: {summary['success_rate']:.1f}%")

# 실행
asyncio.run(main())
```

## 📋 API 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | API 서버 상태 확인 |
| `/test/auto` | POST | 완전한 자동 테스트 워크플로우 실행 |
| `/test/analyze` | POST | 웹 페이지 분석만 수행 |
| `/test/generate-cases` | POST | 테스트 케이스 생성만 수행 |
| `/test/generate-scripts` | POST | 자동화 스크립트 생성만 수행 |
| `/test/monitor` | POST | 성능 모니터링만 수행 |
| `/test/status/{workflow_id}` | GET | 워크플로우 상태 조회 |
| `/test/results/{workflow_id}` | GET | 테스트 결과 조회 |
| `/test/list` | GET | 워크플로우 목록 조회 |
| `/test/clear` | DELETE | 완료된 워크플로우 정리 |

## 🧪 테스트 유형

### 1. Comprehensive (종합)
- 기능 테스트
- 접근성 테스트
- 성능 테스트
- 모든 분석 포함

### 2. Functional (기능)
- 페이지 로드 테스트
- 상호작용 요소 테스트
- 폼 테스트
- 링크 테스트

### 3. Accessibility (접근성)
- Alt 텍스트 확인
- 키보드 네비게이션
- ARIA 라벨 확인
- 색상 대비 확인

### 4. Performance (성능)
- 페이지 로드 시간 측정
- 메모리 사용량 모니터링
- 네트워크 상태 확인
- JavaScript 오류 추적

## 📊 생성되는 파일들

### 1. Python Playwright 스크립트
```python
#!/usr/bin/env python3
"""
자동 생성된 Playwright 테스트 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

class AutoGeneratedTest:
    def __init__(self, url: str):
        self.url = url
        self.results = []
    
    async def run_all_tests(self):
        # 테스트 실행 로직
        pass

# 실행
async def main():
    test = AutoGeneratedTest("https://example.com")
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. JSON 테스트 데이터
```json
{
  "metadata": {
    "generated_at": "2024-01-01T12:00:00",
    "url": "https://example.com",
    "total_test_cases": 10
  },
  "test_cases": [
    {
      "id": "page_load_test",
      "name": "페이지 로드 테스트",
      "type": "functional",
      "steps": [...]
    }
  ]
}
```

## 🔧 고급 설정

### 1. 테스트 케이스 커스터마이징

```python
# 커스텀 테스트 케이스 추가
custom_test_cases = [
    {
        "id": "custom_test",
        "name": "커스텀 테스트",
        "type": "functional",
        "priority": "high",
        "steps": [
            {
                "action": "click",
                "selector": "button.custom-button",
                "description": "커스텀 버튼 클릭"
            }
        ]
    }
]
```

### 2. 성능 임계값 설정

```python
# 성능 임계값 설정
performance_thresholds = {
    "page_load_time": 3000,  # 3초
    "memory_usage": 80,      # 80%
    "dom_elements": 1000     # 1000개
}
```

### 3. 접근성 기준 설정

```python
# 접근성 기준 설정
accessibility_standards = {
    "wcag_level": "AA",
    "color_contrast_ratio": 4.5,
    "keyboard_navigation": True
}
```

## 📈 모니터링 및 메트릭

### 1. 성능 메트릭
- **페이지 로드 시간**: 전체 페이지 로드 완료 시간
- **DOM 준비 시간**: DOM 컨텐츠 로드 완료 시간
- **First Paint**: 첫 번째 픽셀 렌더링 시간
- **First Contentful Paint**: 첫 번째 콘텐츠 렌더링 시간

### 2. 메모리 메트릭
- **JavaScript 힙 사용량**: 현재 사용 중인 메모리
- **총 힙 크기**: 할당된 총 메모리
- **힙 사용률**: 메모리 사용 비율

### 3. 네트워크 메트릭
- **연결 상태**: 온라인/오프라인 상태
- **연결 타입**: 4G, WiFi 등
- **다운로드 속도**: 네트워크 다운로드 속도
- **RTT**: 왕복 시간

## 🐛 문제 해결

### 1. MCP 연결 실패
```bash
# Playwright MCP 재설치
npm uninstall -g @playwright/mcp
npm install -g @playwright/mcp
npx playwright install
```

### 2. 브라우저 실행 오류
```bash
# 브라우저 재설치
npx playwright install --force
```

### 3. 메모리 부족
```bash
# 브라우저 인스턴스 수 제한
export PLAYWRIGHT_MAX_INSTANCES=2
```

### 4. API 서버 시작 실패
```bash
# 포트 확인
netstat -an | grep 8001

# 다른 포트로 시작
python auto_test_api.py --port 8002
```

## 🔄 워크플로우 상태

### 1. 진행 단계
- **0%**: 워크플로우 시작
- **10%**: 웹 페이지 분석 중
- **30%**: 테스트 케이스 생성 중
- **50%**: 자동화 스크립트 생성 중
- **70%**: 테스트 실행 중
- **85%**: 성능 모니터링 중
- **95%**: 종합 리포트 생성 중
- **100%**: 완료

### 2. 상태 코드
- **started**: 워크플로우 시작됨
- **running**: 실행 중
- **completed**: 완료됨
- **failed**: 실패함

## 📝 로그 및 디버깅

### 1. 로그 레벨 설정
```python
import logging

# 로그 레벨 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. 상세 로그 확인
```bash
# 로그 파일 확인
tail -f logs/auto_test_suite.log

# 실시간 로그 모니터링
python -u auto_test_api.py
```

## 🚀 성능 최적화

### 1. 병렬 실행
```python
# 여러 URL 동시 테스트
urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
tasks = [auto_suite.run_complete_test_workflow(url) for url in urls]
results = await asyncio.gather(*tasks)
```

### 2. 리소스 제한
```python
# 동시 실행 제한
semaphore = asyncio.Semaphore(3)  # 최대 3개 동시 실행
async with semaphore:
    result = await auto_suite.run_complete_test_workflow(url)
```

### 3. 캐싱
```python
# 분석 결과 캐싱
cache = {}
if url in cache:
    page_analysis = cache[url]
else:
    page_analysis = await auto_suite._analyze_webpage_with_mcp(url)
    cache[url] = page_analysis
```

## 📚 예제 및 샘플

### 1. 기본 사용 예제
```python
# 기본 사용법
from auto_test_suite_extension import AutoTestSuiteExtension

async def basic_example():
    auto_suite = AutoTestSuiteExtension()
    result = await auto_suite.run_complete_test_workflow("https://www.google.com")
    print(f"결과: {result['status']}")

asyncio.run(basic_example())
```

### 2. 고급 사용 예제
```python
# 고급 사용법
async def advanced_example():
    auto_suite = AutoTestSuiteExtension()
    
    # 단계별 실행
    page_analysis = await auto_suite._analyze_webpage_with_mcp("https://www.google.com")
    test_cases = await auto_suite._generate_test_cases_from_analysis(page_analysis, "comprehensive")
    scripts = await auto_suite._generate_automation_scripts(test_cases, page_analysis)
    
    print(f"생성된 테스트 케이스: {len(test_cases)}개")
    print(f"생성된 스크립트: {len(scripts)}개")

asyncio.run(advanced_example())
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 라이선스

MIT License

## 🆘 지원

- **문서**: [API 문서](http://localhost:8001/docs)
- **이슈**: GitHub Issues
- **토론**: GitHub Discussions

## 📋 변경 로그

### v1.0.0
- 자동 테스트 스위트 출시
- 웹 페이지 자동 분석
- 테스트 케이스 자동 생성
- 자동화 스크립트 생성
- 테스트 자동 실행
- 성능 모니터링
- 종합 리포트 생성

---

**자동 테스트 스위트** - 웹 테스트를 AI로 혁신하세요! 🚀 