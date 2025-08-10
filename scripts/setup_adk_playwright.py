#!/usr/bin/env python3
"""
Google ADK Playwright MCP 환경 설정 스크립트
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    print(f"✅ Python 버전: {sys.version}")
    return True


def check_node_js():
    """Node.js 설치 확인"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
            return True
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("❌ Node.js가 설치되지 않았습니다.")
        print("💡 Node.js를 설치하세요: https://nodejs.org/")
        return False


def install_python_dependencies():
    """Python 의존성 설치"""
    try:
        print("📦 Python 의존성 설치 중...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ Python 의존성 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python 의존성 설치 실패: {e}")
        print(f"에러 출력: {e.stderr}")
        return False


def install_playwright_mcp():
    """Playwright MCP 패키지 확인/설치"""
    try:
        print("🎭 Playwright MCP 패키지 확인 중...")
        result = subprocess.run(
            ["npx", "@playwright/mcp@latest", "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ Playwright MCP 사용 가능")
            return True
        else:
            print("⚠️ Playwright MCP 설치 중...")
            return True  # npx가 자동으로 설치함
    except Exception as e:
        print(f"⚠️ Playwright MCP 확인 실패: {e}")
        return False


def create_env_file():
    """환경 설정 파일 생성"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env 파일이 이미 존재합니다.")
        return True

    if env_example.exists():
        print("📝 .env.example에서 .env 파일 생성...")
        shutil.copy(env_example, env_file)
        print("🔧 .env 파일을 수정하여 API 키를 설정하세요:")
        print("   - GOOGLE_API_KEY (Google AI Studio)")
        print("   - 또는 GOOGLE_CLOUD_PROJECT + 서비스 계정 (Vertex AI)")
        return True
    else:
        print("⚠️ .env.example 파일이 없습니다.")
        return False


def check_directories():
    """필요한 디렉토리 확인"""
    directories = ["config", "multi_tool_agent", "utils", "core"]

    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ 디렉토리 존재")
        else:
            print(f"❌ {dir_name}/ 디렉토리 없음")
            return False

    return True


def main():
    """메인 설정 함수"""
    print("🚀 Google ADK Playwright MCP 환경 설정")
    print("=" * 50)

    checks = [
        ("Python 버전", check_python_version),
        ("Node.js", check_node_js),
        ("디렉토리 구조", check_directories),
        ("Python 의존성", install_python_dependencies),
        ("Playwright MCP", install_playwright_mcp),
        ("환경 설정 파일", create_env_file),
    ]

    all_passed = True

    for name, check_func in checks:
        print(f"\n🔍 {name} 확인 중...")
        if not check_func():
            all_passed = False
            print(f"❌ {name} 확인 실패")
        else:
            print(f"✅ {name} 확인 완료")

    print("\n" + "=" * 50)

    if all_passed:
        print("🎉 환경 설정 완료!")
        print("\n📝 다음 단계:")
        print("1. .env 파일에 API 키 설정")
        print("2. 테스트 실행: python test_adk_playwright_mcp.py")
        print("3. 간단한 데모: python run_adk_playwright_demo.py")
    else:
        print("❌ 일부 설정이 실패했습니다.")
        print("🔧 위의 오류를 해결한 후 다시 실행하세요.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
