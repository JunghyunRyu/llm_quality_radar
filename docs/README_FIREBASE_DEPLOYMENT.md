# 🚀 LLM Quality Radar - Firebase 배포 가이드

Google ADK + Playwright MCP 기반 테스트 자동화 코드 생성기의 Firebase 배포 가이드입니다.

## 📋 목차

- [🎯 프로젝트 개요](#-프로젝트-개요)
- [🏗️ 아키텍처](#️-아키텍처)
- [🔧 환경 설정](#-환경-설정)
- [🚀 배포 가이드](#-배포-가이드)
- [🌐 사용법](#-사용법)
- [🔍 문제 해결](#-문제-해결)
- [📊 모니터링](#-모니터링)

## 🎯 프로젝트 개요

### 주요 기능
- 🤖 **AI 기반 테스트 코드 생성**: Google ADK (Gemini 2.0 Flash)를 활용한 지능형 테스트 코드 자동 생성
- 🎭 **Playwright MCP 통합**: Model Control Protocol을 통한 안정적인 웹 자동화
- 🔧 **자동 복구 시스템**: 테스트 실패 시 ML 기반 자동 복구
- 📊 **실시간 품질 모니터링**: 웹페이지 품질 점수 실시간 측정
- 📸 **스크린샷 캡처**: 각 테스트 단계별 시각적 증거 수집

### 기술 스택
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Firebase Cloud Functions (Node.js)
- **Database**: Cloud Firestore
- **Hosting**: Firebase Hosting
- **AI**: Google ADK (Gemini 2.0 Flash)
- **Automation**: Playwright MCP

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Firebase Hosting                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   index.html    │ │ test-generator  │ │  dashboard.html ││
│  │   (메인 페이지)    │ │     .html       │ │    (대시보드)     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Cloud Functions (API)                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ generateTestCode│ │  checkAdkStatus │ │   healthCheck   ││
│  │                 │ │                 │ │                 ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Cloud Firestore                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  test_results   │ │  test_templates │ │ system_metrics  ││
│  │                 │ │                 │ │                 ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              External Integrations                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Google ADK    │ │ Playwright MCP  │ │  Target Website ││
│  │  (Gemini 2.0)   │ │     Server      │ │                 ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🔧 환경 설정

### 1. 사전 요구사항

```bash
# Node.js 18+ 설치 확인
node --version

# Firebase CLI 설치
npm install -g firebase-tools

# 프로젝트 의존성 설치
npm install
pip install -r requirements.txt
```

### 2. Firebase 프로젝트 설정

```bash
# Firebase 로그인
firebase login

# 새 Firebase 프로젝트 생성 (Console에서도 가능)
firebase projects:create llm-quality-radar

# 프로젝트 사용 설정
firebase use llm-quality-radar

# Firebase 기능 활성화
firebase init
```

선택할 기능:
- ✅ Firestore
- ✅ Functions
- ✅ Hosting

### 3. 환경 변수 설정

```bash
# Firebase Functions 환경 변수 설정
firebase functions:config:set google.api_key="YOUR_GOOGLE_API_KEY"
firebase functions:config:set adk.project_id="YOUR_ADK_PROJECT_ID"
firebase functions:config:set mcp.server_url="http://localhost:8933/mcp"
```

## 🚀 배포 가이드

### 🖥️ Windows 환경

```powershell
# PowerShell 스크립트 실행
.\deploy.ps1

# 또는 옵션 지정
.\deploy.ps1 -Option "1"  # 전체 배포
.\deploy.ps1 -Option "2"  # Hosting만
.\deploy.ps1 -Option "3"  # Functions만
```

### 🐧 Linux/Mac 환경

```bash
# Bash 스크립트 실행
chmod +x deploy.sh
./deploy.sh

# 또는 수동 배포
firebase deploy
```

### 📦 개별 배포

```bash
# Hosting만 배포
firebase deploy --only hosting

# Functions만 배포
firebase deploy --only functions

# Firestore 규칙만 배포
firebase deploy --only firestore:rules,firestore:indexes
```

## 🌐 사용법

### 1. 웹사이트 접속

배포 완료 후 다음 URL들에 접속할 수 있습니다:

- **메인 사이트**: `https://[PROJECT_ID].web.app`
- **테스트 생성기**: `https://[PROJECT_ID].web.app/test-generator.html`
- **대시보드**: `https://[PROJECT_ID].web.app/dashboard.html`

### 2. 테스트 코드 생성

1. **웹사이트 정보 입력**
   - 테스트할 URL 입력
   - 웹사이트 설명 (선택사항)

2. **테스트 시나리오 설정**
   - 테스트 목적 명시
   - 각 단계별 액션 정의
   - CSS 선택자 및 값 입력

3. **옵션 선택**
   - 자동 복구: 테스트 실패 시 자동 복구 시도
   - 품질 검사: 웹페이지 품질 점수 측정
   - 스크린샷: 각 단계별 화면 캡처
   - 접근성 테스트: WCAG 가이드라인 준수 검사

4. **코드 생성 및 다운로드**
   - Python/JavaScript 코드 생성
   - 설정 파일 및 실행 가이드 제공

### 3. API 엔드포인트

#### 테스트 코드 생성

```bash
curl -X POST https://us-central1-[PROJECT_ID].cloudfunctions.net/generateTestCode \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "test_purpose": "로그인 테스트",
    "test_scenarios": [
      {
        "action": "navigate",
        "selector": "",
        "value": ""
      },
      {
        "action": "click",
        "selector": "#login-button",
        "value": ""
      }
    ],
    "options": ["auto-healing", "quality-check", "screenshot"]
  }'
```

#### 상태 확인

```bash
# API 헬스 체크
curl https://us-central1-[PROJECT_ID].cloudfunctions.net/healthCheck

# ADK 상태 확인
curl https://us-central1-[PROJECT_ID].cloudfunctions.net/checkAdkStatus
```

## 🔍 문제 해결

### 자주 발생하는 문제

#### 1. 배포 실패

```bash
# 에러: Firebase CLI 버전 문제
npm update -g firebase-tools

# 에러: 권한 문제
firebase login --reauth

# 에러: 프로젝트 설정 문제
firebase use --add
```

#### 2. Functions 오류

```bash
# 로그 확인
firebase functions:log

# 환경 변수 확인
firebase functions:config:get

# 로컬 테스트
firebase emulators:start --only functions
```

#### 3. API 연결 오류

- **CORS 오류**: Firebase Functions에 CORS 설정 확인
- **타임아웃**: Cloud Functions 타임아웃 설정 증가
- **인증 오류**: Google API 키 및 권한 확인

### 디버깅 도구

```bash
# Firebase 에뮬레이터 실행
firebase emulators:start

# 실시간 로그 모니터링
firebase functions:log --follow

# 프로젝트 상태 확인
firebase projects:list
firebase use --current
```

## 📊 모니터링

### 1. Firebase Console

- **Hosting**: 트래픽 및 성능 모니터링
- **Functions**: 호출 수, 오류율, 실행 시간
- **Firestore**: 읽기/쓰기 작업 및 비용

### 2. Google Cloud Console

- **Cloud Functions 로그**: 상세한 실행 로그
- **Cloud Monitoring**: 커스텀 메트릭 및 알림
- **Error Reporting**: 자동 오류 수집 및 분석

### 3. 사용자 분석

```javascript
// Google Analytics 연동 (선택사항)
gtag('event', 'test_code_generated', {
  'event_category': 'engagement',
  'event_label': 'test_purpose'
});
```

## 🔒 보안 설정

### Firestore 보안 규칙

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 테스트 결과 읽기만 허용
    match /test_results/{document} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

### Functions 보안

```javascript
// CORS 설정
const cors = require('cors')({
  origin: ['https://your-domain.com'],
  credentials: true
});

// 요청 검증
if (!req.body.url || !Array.isArray(req.body.test_scenarios)) {
  return res.status(400).json({error: 'Invalid request'});
}
```

## 📈 성능 최적화

### 1. Hosting 최적화

```json
{
  "hosting": {
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

### 2. Functions 최적화

```javascript
// 메모리 및 타임아웃 설정
exports.generateTestCode = onRequest({
  memory: '1GiB',
  timeoutSeconds: 300,
  maxInstances: 10
}, handler);
```

### 3. Firestore 최적화

- 복합 인덱스 활용
- 쿼리 최적화
- 배치 작업 사용

## 🎉 다음 단계

1. **도메인 연결**: 커스텀 도메인 설정
2. **사용자 인증**: Firebase Auth 통합
3. **결제 시스템**: Firebase Extensions 활용
4. **모바일 앱**: React Native/Flutter 연동
5. **CI/CD**: GitHub Actions 자동 배포

## 📞 지원

- **이슈 리포팅**: GitHub Issues
- **문서**: Firebase Documentation
- **커뮤니티**: Firebase Discord

---

🎊 **축하합니다!** LLM Quality Radar가 성공적으로 배포되었습니다.

이제 AI 기반 테스트 자동화의 새로운 세계를 경험해보세요! 🚀
