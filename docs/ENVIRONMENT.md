# 환경 변수 설정 가이드

다음 환경 변수는 웹/CLI 서버 및 AI·클라우드 연동에 필요합니다.

## 필수
- `GOOGLE_API_KEY`: Gemini 2.0 Flash를 포함한 Google GenAI API 키.

## 권장/선택
- `GOOGLE_CLOUD_PROJECT_ID`: GCP 프로젝트 ID.
- `GOOGLE_APPLICATION_CREDENTIALS`: 서비스 계정 키(JSON) 경로.
- `LOG_LEVEL`: 기본 `INFO`.
- `LOG_FILE`: 예) `logs/app.log`.
- `HOST` / `PORT`: 기본 `0.0.0.0` / `8080`.
- `FIREBASE_PROJECT_ID`: Firebase Hosting/Functions 사용 시.

## Windows PowerShell 예시
```powershell
copy .env.example .env
# .env 파일을 열어 값을 채워 넣으세요.
```

참고: 저장소 정책/환경에 따라 `.env.example` 자동 생성이 제한될 수 있습니다. 이 경우 본 문서와 `README.md`의 환경 변수 섹션을 참고하여 직접 `.env`를 구성하세요.

