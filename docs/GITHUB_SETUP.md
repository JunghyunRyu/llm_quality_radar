# GitHub 설정 가이드

## 1) Secrets: FIREBASE_TOKEN 추가

1. Firebase CLI 설치 및 로그인
   ```powershell
   npm i -g firebase-tools
   firebase login
   firebase login:ci
   # 출력된 토큰 복사
   ```
2. GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret
   - Name: `FIREBASE_TOKEN`
   - Value: (위에서 복사한 토큰)

## 2) 브랜치 보호 규칙(main)
- Settings → Branches → Add rule
  - Branch name pattern: `main`
  - Require a pull request before merging: 체크, 최소 1명 리뷰
  - Require status checks to pass before merging: 체크, `CI` 지정
  - Include administrators: 체크

PowerShell 스크립트로 자동 구성:
```powershell
pwsh scripts/setup_github.ps1 -RepoOwner "JunghyunRyu" -RepoName "llm_quality_radar" -FirebaseToken "<TOKEN>"
```

## 3) 리포지토리 메타데이터(설명/토픽)
- Settings → General → Description 업데이트
- Topics 추가: `ai-testing, llm, playwright, mcp, quality, fastapi, firebase, gcp, automation, qa`

또는 스크립트 사용(위 스크립트 참조).

## 4) 워크플로우
- CI: `.github/workflows/ci.yml`
- Release: `.github/workflows/release.yml` (태그 `v*.*.*`)
- Deploy: `.github/workflows/deploy.yml` (main 푸시/수동 실행)

Secrets가 설정되면 main 푸시 시 Firebase Hosting 자동 배포가 실행됩니다.

