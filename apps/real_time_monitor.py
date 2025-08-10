#!/usr/bin/env python3
import requests
import time
import threading
from datetime import datetime

def start_test():
    """테스트 시작"""
    test_request = {
        "url": "https://www.google.com",
        "test_scenarios": [
            {
                "action": "wait",
                "selector": "body",
                "description": "페이지 로드 대기"
            },
            {
                "action": "wait",
                "selector": "title",
                "description": "제목 요소 대기"
            }
        ],
        "auto_healing": False,
        "quality_analysis": True,
        "performance_monitoring": False,
        "accessibility_testing": False,
        "responsive_testing": False
    }
    
    try:
        response = requests.post("http://localhost:8000/test/web", json=test_request, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['test_id']
        else:
            print(f"테스트 시작 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"테스트 시작 오류: {e}")
        return None

def monitor_test(test_id):
    """테스트 모니터링"""
    print(f"테스트 {test_id} 모니터링 시작...")
    print("=" * 60)
    
    start_time = datetime.now()
    last_progress = -1
    last_step = ""
    
    while True:
        try:
            response = requests.get(f"http://localhost:8000/report/{test_id}", timeout=5)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                
                if status == 'completed':
                    print(f"\n✅ 테스트 완료!")
                    print(f"   성공률: {result.get('success_rate', 0):.1f}%")
                    print(f"   실행 시간: {result.get('execution_time', 0):.2f}초")
                    break
                    
                elif status == 'error':
                    print(f"\n❌ 테스트 오류: {result.get('error_message', 'Unknown error')}")
                    break
                    
                elif status in ['started', 'running']:
                    current_step = result.get('current_step', 'Unknown')
                    progress = result.get('progress', 0)
                    current_scenario = result.get('current_scenario', '')
                    completed_scenarios = result.get('completed_scenarios', 0)
                    total_scenarios = result.get('total_scenarios', 0)
                    
                    # 변경사항이 있을 때만 출력
                    if progress != last_progress or current_step != last_step:
                        elapsed_time = (datetime.now() - start_time).total_seconds()
                        progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
                        
                        print(f"[{elapsed_time:6.1f}s] ⏳ {current_step}")
                        print(f"         [{progress_bar}] {progress}%")
                        
                        if current_scenario:
                            print(f"         📋 {current_scenario}")
                        
                        if total_scenarios > 0:
                            print(f"         📊 시나리오: {completed_scenarios}/{total_scenarios}")
                        
                        print("-" * 40)
                        
                        last_progress = progress
                        last_step = current_step
                        
            else:
                print(f"상태 확인 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"모니터링 오류: {e}")
        
        time.sleep(1)

def main():
    print("=== 실시간 테스트 모니터링 ===")
    
    # 테스트 시작
    test_id = start_test()
    if test_id:
        print(f"✅ 테스트 시작됨: {test_id}")
        
        # 모니터링 시작
        monitor_test(test_id)
    else:
        print("❌ 테스트 시작 실패")

if __name__ == "__main__":
    main() 