#!/usr/bin/env python3
"""
Google ADK와 Playwright MCP 연계 시스템 실행 스크립트
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    # Python 버전 확인
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다")
        return False
    
    # 필요한 패키지 확인
    required_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "playwright"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
        print("   다음 명령어로 설치하세요:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ 의존성 확인 완료")
    return True

def check_playwright_mcp():
    """Playwright MCP 확인"""
    print("🔍 Playwright MCP 확인 중...")
    
    try:
        # npx 명령어 확인
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ npx가 설치되지 않았습니다")
            print("   Node.js를 설치하세요: https://nodejs.org/")
            return False
        
        # Playwright MCP 설치 확인
        result = subprocess.run(["npx", "@playwright/mcp", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  Playwright MCP가 설치되지 않았습니다")
            print("   설치 중...")
            
            result = subprocess.run(["npm", "install", "-g", "@playwright/mcp"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Playwright MCP 설치 실패")
                return False
        
        print("✅ Playwright MCP 확인 완료")
        return True
        
    except FileNotFoundError:
        print("❌ Node.js가 설치되지 않았습니다")
        print("   Node.js를 설치하세요: https://nodejs.org/")
        return False

def check_google_cloud():
    """Google Cloud 설정 확인"""
    print("🔍 Google Cloud 설정 확인 중...")
    
    # 환경 변수 확인
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id:
        print("⚠️  GOOGLE_CLOUD_PROJECT_ID가 설정되지 않았습니다")
        print("   Google ADK 기능이 제한될 수 있습니다")
    
    if not credentials:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS가 설정되지 않았습니다")
        print("   Google ADK 기능이 제한될 수 있습니다")
    
    # gcloud 명령어 확인
    try:
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud SDK 확인 완료")
        else:
            print("⚠️  Google Cloud SDK가 설치되지 않았습니다")
            print("   Google ADK 기능이 제한될 수 있습니다")
    except FileNotFoundError:
        print("⚠️  Google Cloud SDK가 설치되지 않았습니다")
        print("   Google ADK 기능이 제한될 수 있습니다")
    
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    print("📁 디렉토리 생성 중...")
    
    directories = [
        "screenshots",
        "logs",
        "reports",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ 디렉토리 생성 완료")

def start_server():
    """서버 시작"""
    print("🚀 서버 시작 중...")
    
    try:
        # 서버 프로세스 시작
        process = subprocess.Popen([
            sys.executable, "playwright_adk_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 서버 시작 대기
        print("   서버 시작 대기 중...")
        time.sleep(5)
        
        # 서버 상태 확인
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ 서버가 성공적으로 시작되었습니다")
                print(f"   URL: http://localhost:8000")
                print(f"   API 문서: http://localhost:8000/docs")
                print(f"   프로세스 ID: {process.pid}")
                return process
            else:
                print(f"❌ 서버 응답 오류: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ 서버에 연결할 수 없습니다")
            return None
            
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return None

def run_tests():
    """테스트 실행"""
    print("\n🧪 테스트 실행 중...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_playwright_adk.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 테스트 완료")
        else:
            print("⚠️  테스트에 일부 오류가 있었습니다")
            print(result.stdout)
            if result.stderr:
                print("오류:")
                print(result.stderr)
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {e}")

def show_menu():
    """메뉴 표시"""
    print("\n" + "="*50)
    print("🎯 Google ADK & Playwright MCP 연계 시스템")
    print("="*50)
    print("1. 시스템 시작")
    print("2. 테스트 실행")
    print("3. 시스템 시작 + 테스트 실행")
    print("4. 종료")
    print("="*50)

def main():
    """메인 함수"""
    print("🎯 Google ADK와 Playwright MCP 연계 시스템")
    print("="*50)
    
    # 1. 의존성 확인
    if not check_dependencies():
        return
    
    # 2. Playwright MCP 확인
    if not check_playwright_mcp():
        return
    
    # 3. Google Cloud 설정 확인
    check_google_cloud()
    
    # 4. 디렉토리 생성
    create_directories()
    
    server_process = None
    
    while True:
        show_menu()
        
        try:
            choice = input("선택하세요 (1-4): ").strip()
            
            if choice == "1":
                # 시스템 시작
                if server_process:
                    print("⚠️  서버가 이미 실행 중입니다")
                else:
                    server_process = start_server()
                    if server_process:
                        print("\n서버를 중지하려면 Ctrl+C를 누르세요")
                        try:
                            server_process.wait()
                        except KeyboardInterrupt:
                            print("\n⏹️  서버를 중지합니다...")
                            server_process.terminate()
                            server_process = None
            
            elif choice == "2":
                # 테스트 실행
                if not server_process:
                    print("⚠️  먼저 서버를 시작하세요")
                else:
                    run_tests()
            
            elif choice == "3":
                # 시스템 시작 + 테스트 실행
                if server_process:
                    print("⚠️  서버가 이미 실행 중입니다")
                else:
                    server_process = start_server()
                    if server_process:
                        time.sleep(3)  # 서버 안정화 대기
                        run_tests()
                        print("\n서버를 중지하려면 Ctrl+C를 누르세요")
                        try:
                            server_process.wait()
                        except KeyboardInterrupt:
                            print("\n⏹️  서버를 중지합니다...")
                            server_process.terminate()
                            server_process = None
            
            elif choice == "4":
                # 종료
                if server_process:
                    print("⏹️  서버를 중지합니다...")
                    server_process.terminate()
                print("👋 시스템을 종료합니다")
                break
            
            else:
                print("❌ 잘못된 선택입니다. 1-4 중에서 선택하세요.")
        
        except KeyboardInterrupt:
            print("\n⏹️  사용자에 의해 중단되었습니다")
            if server_process:
                server_process.terminate()
            break
        
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 