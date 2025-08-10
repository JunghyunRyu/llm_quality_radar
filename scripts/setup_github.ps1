param(
  [Parameter(Mandatory=$true)] [string]$RepoOwner,
  [Parameter(Mandatory=$true)] [string]$RepoName,
  [Parameter(Mandatory=$false)] [string]$FirebaseToken
)

# Requires: gh CLI (https://cli.github.com/)
# Usage:
#   pwsh scripts/setup_github.ps1 -RepoOwner "JunghyunRyu" -RepoName "llm_quality_radar" -FirebaseToken "..."

function Require-Tool($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Error "'$name' 명령을 찾을 수 없습니다. 설치 후 다시 실행하세요." -ErrorAction Stop
  }
}

Require-Tool gh

# 리포지토리 식별자
$repo = "$RepoOwner/$RepoName"

Write-Host "🔧 GitHub 리포지토리 설정: $repo"

# 1) Secrets 설정(FIREBASE_TOKEN)
if ($FirebaseToken) {
  gh secret set FIREBASE_TOKEN -R $repo -b $FirebaseToken
  Write-Host "✅ GitHub Secret 'FIREBASE_TOKEN' 설정 완료"
} else {
  Write-Host "⚠️ FirebaseToken 미제공: 'FIREBASE_TOKEN'은 수동으로 설정하거나 -FirebaseToken 인자를 제공하세요."
}

# 2) 기본 브랜치 보호 규칙
Write-Host "🔒 'main' 브랜치 보호 규칙 구성"
gh api -X PUT repos/$repo/branches/main/protection `
  -f required_status_checks.strict=true `
  -f required_status_checks.contexts[]="CI" `
  -f enforce_admins=true `
  -f required_pull_request_reviews.required_approving_review_count=1 `
  -f restrictions='' | Out-Null
Write-Host "✅ 브랜치 보호 규칙 적용"

# 3) 리포지토리 메타데이터(설명/토픽)
Write-Host "📝 리포지토리 설명/토픽 업데이트"
$desc = "AI 기반 웹 자동화 테스트 및 품질 분석(ADK + Playwright MCP)"
gh repo edit $repo --description "$desc" --homepage "https://github.com/$repo" | Out-Null

$topics = @(
  'ai-testing','llm','playwright','mcp','quality','fastapi','firebase','gcp','automation','qa'
)
gh repo edit $repo --add-topics ($topics -join ',') | Out-Null
Write-Host "✅ 설명/토픽 업데이트 완료"

Write-Host "🎉 GitHub 설정 완료"

