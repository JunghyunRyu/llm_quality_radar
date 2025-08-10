# LLM Quality Radar

AI 기반 웹 자동화 테스트 및 품질 분석 플랫폼입니다. Google ADK와 Playwright MCP를 연계해 자연어 기반 테스트 생성·실행과 품질 분석을 제공합니다.

## ✨ 주요 기능

- AI 기반 품질 분석(Gemini 2.0 Flash).
- 웹 자동화 테스트(Playwright MCP) 및 스크린샷/로그 수집.
- 성능·접근성·SEO 분석과 종합 리포트.
- 자동 복구(오류 재시도/치유) 프레임워크.
- 웹 UI와 API/CLI 동시 제공.

## 🚀 빠른 시작

```bash
# 1) 저장소 클론
git clone <your-repo-url>
cd llm_quality_radar

# 2) 의존성 설치
pip install -r requirements.txt

# 3) 환경 변수 설정
copy .env.example .env   # Windows PowerShell
# .env에 GOOGLE_API_KEY 등 채워 넣기

# 4) 웹 서버 실행
python apps/web_server.py
```

- 브라우저에서 http://localhost:8080 접속.

CLI/API 실행 예시:

```bash
# 기본 API 서버 실행
python apps/app.py

# 자동 테스트 스위트 실행(데모)
python demos/run_system.py
```

## 📁 프로젝트 구조

- `apps/`: FastAPI 기반 웹/API 서버들.
- `core/`: MCP 클라이언트, 자동 복구, 모니터링 등 핵심 모듈.
- `multi_tool_agent/`: ADK 연계 에이전트.
- `public/`·`static/`: 웹 UI 정적 리소스.
- `functions/`: Firebase Functions (선택).
- `demos/`·`scripts/`: 데모와 배포/유틸 스크립트.
- `docs/`: 상세 문서.

## 🛠️ 기술 스택

- Backend: Python(FastAPI, Uvicorn).
- Automation: Playwright MCP.
- AI/ML: Google ADK, Gemini 2.0.
- Cloud: Firebase, GCP(선택).

## ⚙️ 환경 변수(.env)

```bash
GOOGLE_API_KEY=your_google_api_key
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

GCP/Firebase를 사용하는 경우 관련 변수들을 추가로 설정하세요. 자세한 내용은 `docs/README.md` 및 `docs/README_FIREBASE_DEPLOYMENT.md` 참고.

## 📖 문서

- 설치/실행: `docs/README.md`.
- 웹 데모 가이드: `public/index.html` 상단 링크.
- Firebase 배포: `docs/README_FIREBASE_DEPLOYMENT.md`.
- 프로젝트 개요: `docs/프로젝트_개요_및_실행가이드.md`.
- 로드맵: `docs/프로젝트_발전방향_및_로드맵.md`.

## 🤝 기여하기

프로젝트에 기여를 환영합니다. 상세한 절차는 `CONTRIBUTING.md`를 확인하세요.

## 📄 라이선스

MIT License. 세부 내용은 `LICENSE` 파일을 참고하세요.
