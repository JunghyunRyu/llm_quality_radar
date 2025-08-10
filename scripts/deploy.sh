#!/bin/bash

# LLM Quality Radar Firebase 배포 스크립트
# Firebase Hosting + Cloud Functions 배포 자동화

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 LLM Quality Radar Firebase 배포 시작..."
echo "=================================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 현재 시간 기록
START_TIME=$(date +%s)

# 1. 환경 검사
print_status "환경 검사 중..."

# Node.js 버전 확인
if ! command -v node &> /dev/null; then
    print_error "Node.js가 설치되어 있지 않습니다."
    exit 1
fi

NODE_VERSION=$(node -v)
print_success "Node.js 버전: $NODE_VERSION"

# Firebase CLI 확인
if ! command -v firebase &> /dev/null; then
    print_warning "Firebase CLI가 설치되어 있지 않습니다. 설치 중..."
    npm install -g firebase-tools
fi

FIREBASE_VERSION=$(firebase --version)
print_success "Firebase CLI 버전: $FIREBASE_VERSION"

# 2. Firebase 로그인 확인
print_status "Firebase 인증 상태 확인 중..."
if ! firebase projects:list &> /dev/null; then
    print_warning "Firebase에 로그인이 필요합니다."
    firebase login
fi
print_success "Firebase 인증 완료"

# 3. 프로젝트 확인
print_status "Firebase 프로젝트 확인 중..."
PROJECT_ID=$(firebase use --current 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
    print_warning "Firebase 프로젝트가 설정되지 않았습니다."
    echo "사용 가능한 프로젝트 목록:"
    firebase projects:list
    read -p "사용할 프로젝트 ID를 입력하세요: " PROJECT_ID
    firebase use "$PROJECT_ID"
fi
print_success "현재 프로젝트: $PROJECT_ID"

# 4. 의존성 설치
print_status "Cloud Functions 의존성 설치 중..."
cd functions
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    npm install
    print_success "의존성 설치 완료"
else
    print_success "의존성이 이미 최신 상태입니다"
fi
cd ..

# 5. 린팅 검사
print_status "코드 품질 검사 중..."
cd functions
if npm run lint; then
    print_success "린팅 검사 통과"
else
    print_warning "린팅 오류가 발견되었습니다. 계속 진행하시겠습니까? (y/N)"
    read -p "" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "배포가 취소되었습니다."
        exit 1
    fi
fi
cd ..

# 6. 빌드 (필요한 경우)
print_status "프로젝트 빌드 중..."
# 현재는 정적 파일이므로 별도 빌드 과정 없음
print_success "빌드 완료"

# 7. Firebase 프로젝트 설정 확인
print_status "Firebase 설정 확인 중..."
if [ ! -f "firebase.json" ]; then
    print_error "firebase.json 파일이 없습니다."
    exit 1
fi

if [ ! -f ".firebaserc" ]; then
    print_error ".firebaserc 파일이 없습니다."
    exit 1
fi

print_success "Firebase 설정 파일 확인 완료"

# 8. 배포 옵션 선택
echo ""
echo "배포 옵션을 선택하세요:"
echo "1) 전체 배포 (Hosting + Functions + Firestore)"
echo "2) Hosting만 배포"
echo "3) Functions만 배포"
echo "4) Firestore 규칙만 배포"

read -p "선택 (1-4, 기본값: 1): " DEPLOY_OPTION
DEPLOY_OPTION=${DEPLOY_OPTION:-1}

# 9. 배포 실행
print_status "배포 실행 중..."

case $DEPLOY_OPTION in
    1)
        print_status "전체 배포 실행 중..."
        firebase deploy
        ;;
    2)
        print_status "Hosting 배포 실행 중..."
        firebase deploy --only hosting
        ;;
    3)
        print_status "Functions 배포 실행 중..."
        firebase deploy --only functions
        ;;
    4)
        print_status "Firestore 규칙 배포 실행 중..."
        firebase deploy --only firestore:rules,firestore:indexes
        ;;
    *)
        print_error "잘못된 선택입니다."
        exit 1
        ;;
esac

# 10. 배포 완료 처리
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=================================================="
print_success "🎉 배포가 성공적으로 완료되었습니다!"
echo ""
echo "📊 배포 정보:"
echo "   • 프로젝트: $PROJECT_ID"
echo "   • 소요 시간: ${DURATION}초"
echo "   • 배포 시간: $(date)"
echo ""

# 11. URL 정보 표시
print_status "🌐 접속 URL:"
if [ "$DEPLOY_OPTION" = "1" ] || [ "$DEPLOY_OPTION" = "2" ]; then
    HOSTING_URL="https://$PROJECT_ID.web.app"
    echo "   • 메인 사이트: $HOSTING_URL"
    echo "   • 테스트 생성기: $HOSTING_URL/test-generator.html"
    echo "   • 대시보드: $HOSTING_URL/dashboard.html"
fi

if [ "$DEPLOY_OPTION" = "1" ] || [ "$DEPLOY_OPTION" = "3" ]; then
    FUNCTIONS_URL="https://us-central1-$PROJECT_ID.cloudfunctions.net"
    echo "   • API 엔드포인트: $FUNCTIONS_URL"
    echo "     - 테스트 코드 생성: $FUNCTIONS_URL/generateTestCode"
    echo "     - ADK 상태 확인: $FUNCTIONS_URL/checkAdkStatus"
    echo "     - 헬스 체크: $FUNCTIONS_URL/healthCheck"
fi

# 12. 다음 단계 안내
echo ""
print_status "🔧 다음 단계:"
echo "   1. 웹사이트에 접속하여 정상 작동 확인"
echo "   2. 테스트 코드 생성기로 샘플 테스트 생성"
echo "   3. Google ADK API 키 설정 (Firebase 콘솔 > Functions > 환경 변수)"
echo "   4. Firestore 보안 규칙 검토 및 사용자 인증 설정"
echo "   5. 도메인 연결 (선택사항)"

# 13. 로그 모니터링 옵션
echo ""
read -p "실시간 로그를 모니터링하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "실시간 로그 모니터링 시작... (Ctrl+C로 종료)"
    firebase functions:log --follow
fi

print_success "배포 스크립트 실행 완료! 🎊"
