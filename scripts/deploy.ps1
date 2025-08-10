# LLM Quality Radar Firebase 배포 스크립트 (PowerShell)
# Firebase Hosting + Cloud Functions 배포 자동화

param(
    [string]$Option = "1",
    [switch]$SkipTests = $false
)

# 오류 발생 시 중단
$ErrorActionPreference = "Stop"

Write-Host "🚀 LLM Quality Radar Firebase 배포 시작..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 현재 시간 기록
$StartTime = Get-Date

# 함수 정의
function Write-Status {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

try {
    # 1. 환경 검사
    Write-Status "환경 검사 중..."

    # Node.js 버전 확인
    try {
        $NodeVersion = node --version
        Write-Success "Node.js 버전: $NodeVersion"
    }
    catch {
        Write-Error-Custom "Node.js가 설치되어 있지 않습니다."
        exit 1
    }

    # Firebase CLI 확인
    try {
        $FirebaseVersion = firebase --version
        Write-Success "Firebase CLI 버전: $FirebaseVersion"
    }
    catch {
        Write-Warning "Firebase CLI가 설치되어 있지 않습니다. 설치 중..."
        npm install -g firebase-tools
        $FirebaseVersion = firebase --version
        Write-Success "Firebase CLI 설치 완료: $FirebaseVersion"
    }

    # 2. Firebase 로그인 확인
    Write-Status "Firebase 인증 상태 확인 중..."
    try {
        firebase projects:list | Out-Null
        Write-Success "Firebase 인증 완료"
    }
    catch {
        Write-Warning "Firebase에 로그인이 필요합니다."
        firebase login
    }

    # 3. 프로젝트 확인
    Write-Status "Firebase 프로젝트 확인 중..."
    try {
        $ProjectId = firebase use --current 2>$null
        if (-not $ProjectId) {
            throw "프로젝트가 설정되지 않음"
        }
    }
    catch {
        Write-Warning "Firebase 프로젝트가 설정되지 않았습니다."
        Write-Host "사용 가능한 프로젝트 목록:"
        firebase projects:list
        $ProjectId = Read-Host "사용할 프로젝트 ID를 입력하세요"
        firebase use $ProjectId
    }
    Write-Success "현재 프로젝트: $ProjectId"

    # 4. 의존성 설치
    Write-Status "Cloud Functions 의존성 설치 중..."
    Push-Location functions
    
    if (-not (Test-Path "node_modules") -or (Get-Item "package.json").LastWriteTime -gt (Get-Item "node_modules").LastWriteTime) {
        npm install
        Write-Success "의존성 설치 완료"
    }
    else {
        Write-Success "의존성이 이미 최신 상태입니다"
    }
    
    # 5. 린팅 검사 (선택적)
    if (-not $SkipTests) {
        Write-Status "코드 품질 검사 중..."
        try {
            npm run lint
            Write-Success "린팅 검사 통과"
        }
        catch {
            Write-Warning "린팅 오류가 발견되었습니다. 계속 진행하시겠습니까? (y/N)"
            $Continue = Read-Host
            if ($Continue -notmatch '^[Yy]$') {
                Write-Error-Custom "배포가 취소되었습니다."
                exit 1
            }
        }
    }
    
    Pop-Location

    # 6. 빌드
    Write-Status "프로젝트 빌드 중..."
    # 정적 파일이므로 별도 빌드 과정 없음
    Write-Success "빌드 완료"

    # 7. Firebase 설정 확인
    Write-Status "Firebase 설정 확인 중..."
    if (-not (Test-Path "firebase.json")) {
        Write-Error-Custom "firebase.json 파일이 없습니다."
        exit 1
    }
    
    if (-not (Test-Path ".firebaserc")) {
        Write-Error-Custom ".firebaserc 파일이 없습니다."
        exit 1
    }
    
    Write-Success "Firebase 설정 파일 확인 완료"

    # 8. 배포 옵션 선택
    if ($Option -eq "1") {
        Write-Host ""
        Write-Host "배포 옵션을 선택하세요:" -ForegroundColor Cyan
        Write-Host "1) 전체 배포 (Hosting + Functions + Firestore)"
        Write-Host "2) Hosting만 배포"
        Write-Host "3) Functions만 배포"
        Write-Host "4) Firestore 규칙만 배포"
        
        $Option = Read-Host "선택 (1-4, 기본값: 1)"
        if (-not $Option) { $Option = "1" }
    }

    # 9. 배포 실행
    Write-Status "배포 실행 중..."

    switch ($Option) {
        "1" {
            Write-Status "전체 배포 실행 중..."
            firebase deploy
        }
        "2" {
            Write-Status "Hosting 배포 실행 중..."
            firebase deploy --only hosting
        }
        "3" {
            Write-Status "Functions 배포 실행 중..."
            firebase deploy --only functions
        }
        "4" {
            Write-Status "Firestore 규칙 배포 실행 중..."
            firebase deploy --only firestore:rules,firestore:indexes
        }
        default {
            Write-Error-Custom "잘못된 선택입니다."
            exit 1
        }
    }

    # 10. 배포 완료 처리
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalSeconds

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Success "🎉 배포가 성공적으로 완료되었습니다!"
    Write-Host ""
    Write-Host "📊 배포 정보:" -ForegroundColor Cyan
    Write-Host "   • 프로젝트: $ProjectId"
    Write-Host "   • 소요 시간: $([math]::Round($Duration, 2))초"
    Write-Host "   • 배포 시간: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""

    # 11. URL 정보 표시
    Write-Status "🌐 접속 URL:"
    if ($Option -eq "1" -or $Option -eq "2") {
        $HostingUrl = "https://$ProjectId.web.app"
        Write-Host "   • 메인 사이트: $HostingUrl" -ForegroundColor Green
        Write-Host "   • 테스트 생성기: $HostingUrl/test-generator.html" -ForegroundColor Green
        Write-Host "   • 대시보드: $HostingUrl/dashboard.html" -ForegroundColor Green
    }

    if ($Option -eq "1" -or $Option -eq "3") {
        $FunctionsUrl = "https://us-central1-$ProjectId.cloudfunctions.net"
        Write-Host "   • API 엔드포인트: $FunctionsUrl" -ForegroundColor Green
        Write-Host "     - 테스트 코드 생성: $FunctionsUrl/generateTestCode" -ForegroundColor Green
        Write-Host "     - ADK 상태 확인: $FunctionsUrl/checkAdkStatus" -ForegroundColor Green
        Write-Host "     - 헬스 체크: $FunctionsUrl/healthCheck" -ForegroundColor Green
    }

    # 12. 다음 단계 안내
    Write-Host ""
    Write-Status "🔧 Next Steps:"
    Write-Host "   1. Access website and verify normal operation"
    Write-Host "   2. Generate sample tests using test code generator"
    Write-Host "   3. Set Google ADK API key (Firebase Console > Functions > Environment Variables)"
    Write-Host "   4. Review Firestore security rules and user authentication settings"
    Write-Host "   5. Connect domain (optional)"

    # 13. 로그 모니터링 옵션
    Write-Host ""
    $MonitorLogs = Read-Host "실시간 로그를 모니터링하시겠습니까? (y/N)"
    if ($MonitorLogs -match '^[Yy]$') {
        Write-Status "실시간 로그 모니터링 시작... (Ctrl+C로 종료)"
        firebase functions:log --follow
    }

    Write-Success "배포 스크립트 실행 완료! 🎊"

}
catch {
    Write-Error-Custom "배포 중 오류가 발생했습니다: $($_.Exception.Message)"
    exit 1
}

# Usage examples:
# .\deploy.ps1                     # Interactive mode
# .\deploy.ps1 -Option "2"         # Deploy Hosting only
# .\deploy.ps1 -Option "3" -SkipTests  # Deploy Functions only, skip tests
