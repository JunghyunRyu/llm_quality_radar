/**
 * 테스트 자동화 코드 생성기 JavaScript
 * Google ADK + Playwright MCP 기반 테스트 코드 생성
 */

let testCaseCounter = 0;
let activeOptions = new Set(['auto-healing', 'quality-check', 'screenshot']);
let currentMode = 'manual';

// API 설정
const API_CONFIG = {
    local: 'http://localhost:5001',
    production: 'https://us-central1-llm-quality-radar.cloudfunctions.net'
};

/**
 * 현재 환경에 맞는 API URL 반환
 */
function getApiUrl() {
    // 로컬 개발 환경 감지
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return API_CONFIG.local;
    }
    
    // Firebase 프로젝트 ID 자동 감지
    const hostname = window.location.hostname;
    if (hostname.includes('.web.app') || hostname.includes('.firebaseapp.com')) {
        const projectId = hostname.split('.')[0];
        return `https://us-central1-${projectId}.cloudfunctions.net`;
    }
    
    // 기본값
    return API_CONFIG.production;
}

/**
 * API 상태 확인
 */
async function checkApiStatus() {
    try {
        const apiUrl = getApiUrl();
        const response = await fetch(`${apiUrl}/healthCheck`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const status = await response.json();
            console.log('API 상태:', status);
            return status;
        }
        return null;
    } catch (error) {
        console.warn('API 상태 확인 실패:', error);
        return null;
    }
}

/**
 * API 상태 초기화 및 사용자 알림
 */
async function initializeApiStatus() {
    const statusElement = createApiStatusElement();
    document.body.appendChild(statusElement);
    
    const status = await checkApiStatus();
    
    if (status) {
        updateApiStatusElement(statusElement, 'connected', `API 연결됨 (${status.version || '1.0.0'})`);
        
        // 3초 후 상태 표시 숨기기
        setTimeout(() => {
            statusElement.style.opacity = '0';
            setTimeout(() => statusElement.remove(), 300);
        }, 3000);
    } else {
        updateApiStatusElement(statusElement, 'disconnected', 'API 연결 실패 - 데모 모드로 실행');
        
        // 5초 후 상태 표시 숨기기
        setTimeout(() => {
            statusElement.style.opacity = '0';
            setTimeout(() => statusElement.remove(), 300);
        }, 5000);
    }
}

/**
 * API 상태 표시 요소 생성
 */
function createApiStatusElement() {
    const element = document.createElement('div');
    element.id = 'api-status';
    element.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 10000;
        padding: 12px 20px;
        border-radius: 25px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
        transform: translateX(100%);
        opacity: 0;
    `;
    
    // 애니메이션으로 나타나기
    setTimeout(() => {
        element.style.transform = 'translateX(0)';
        element.style.opacity = '1';
    }, 100);
    
    return element;
}

/**
 * API 상태 표시 요소 업데이트
 */
function updateApiStatusElement(element, status, message) {
    const icon = status === 'connected' 
        ? '<i class="fas fa-check-circle" style="color: #4CAF50;"></i>'
        : '<i class="fas fa-exclamation-triangle" style="color: #FF9800;"></i>';
    
    element.innerHTML = `${icon} ${message}`;
    
    if (status === 'connected') {
        element.style.borderColor = 'rgba(76, 175, 80, 0.5)';
        element.style.background = 'rgba(76, 175, 80, 0.1)';
    } else {
        element.style.borderColor = 'rgba(255, 152, 0, 0.5)';
        element.style.background = 'rgba(255, 152, 0, 0.1)';
    }
}

// 초기 테스트 케이스 추가
document.addEventListener('DOMContentLoaded', async function() {
    addTestCase();
    addTestCase();
    initializeEventListeners();
    
    // API 상태 확인
    await initializeApiStatus();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 옵션 카드 클릭 이벤트
    document.querySelectorAll('.option-card').forEach(card => {
        card.addEventListener('click', function() {
            const option = this.dataset.option;
            
            if (this.classList.contains('active')) {
                this.classList.remove('active');
                activeOptions.delete(option);
            } else {
                this.classList.add('active');
                activeOptions.add(option);
            }
        });
    });
}

// 모드 토글
function toggleMode(mode) {
    currentMode = mode;
    const autoSection = document.getElementById('auto-mode-section');
    if (!autoSection) return;
    autoSection.style.display = mode === 'auto' ? 'block' : 'none';
}

// 자동 생성 호출
async function requestAutoCases() {
    const websiteUrl = document.getElementById('website-url').value;
    if (!websiteUrl) {
        alert('웹사이트 URL을 입력해주세요.');
        return;
    }
    const testType = document.getElementById('auto-test-type')?.value || 'comprehensive';
    const apiUrl = getApiUrl();
    try {
        const resp = await fetch(`${apiUrl}/generateAutoTestCases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: websiteUrl, test_type: testType })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || '자동 생성 실패');
        const cases = data.test_cases || [];
        renderAutoTestCases(cases);
        const summary = document.getElementById('auto-cases-summary');
        if (summary) summary.innerText = `자동 생성된 케이스: ${cases.length}개`;
        showMessage('자동 생성된 테스트 케이스를 불러왔습니다. 필요시 수정 후 코드 생성을 진행하세요.');
    } catch (e) {
        console.error(e);
        showMessage(`자동 생성 실패: ${e.message}`, 'error');
    }
}

function renderAutoTestCases(cases) {
    const container = document.getElementById('test-case-builder');
    if (!container) return;
    container.innerHTML = '';
    testCaseCounter = 0;

    const mapStep = (step) => {
        const action = step.action || 'click';
        const selector = step.selector || '';
        const value = step.value || '';
        return { action, selector, value };
    };

    cases.forEach(tc => {
        (tc.steps || []).forEach(step => {
            addTestCase();
            const id = testCaseCounter;
            const row = mapStep(step);
            const actionEl = document.querySelector(`[name="action-${id}"]`);
            const selectorEl = document.querySelector(`[name="selector-${id}"]`);
            const valueEl = document.querySelector(`[name="value-${id}"]`);
            if (actionEl) actionEl.value = row.action;
            if (selectorEl) selectorEl.value = row.selector;
            if (valueEl) valueEl.value = row.value;
        });
    });
}

// 테스트 케이스 추가
function addTestCase() {
    testCaseCounter++;
    const container = document.getElementById('test-case-builder');
    
    const testCaseHtml = `
        <div class="test-case-item" id="test-case-${testCaseCounter}">
            <div class="test-case-header">
                <span class="test-case-number">테스트 케이스 ${testCaseCounter}</span>
                <button class="remove-test-case" onclick="removeTestCase(${testCaseCounter})" ${testCaseCounter <= 2 ? 'style="display:none;"' : ''}>
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="test-case-inputs">
                <select class="form-input" name="action-${testCaseCounter}">
                    <option value="navigate">페이지 이동</option>
                    <option value="click">클릭</option>
                    <option value="type">텍스트 입력</option>
                    <option value="wait">요소 대기</option>
                    <option value="assert">검증</option>
                    <option value="screenshot">스크린샷</option>
                </select>
                <input type="text" class="form-input" name="selector-${testCaseCounter}" 
                       placeholder="CSS 선택자 또는 설명 (예: #login-button, 로그인 버튼)">
                <input type="text" class="form-input" name="value-${testCaseCounter}" 
                       placeholder="값 (필요시)">
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', testCaseHtml);

    // 기본값 설정
    if (testCaseCounter === 1) {
        document.querySelector(`[name="selector-1"]`).placeholder = '페이지 URL이 자동으로 설정됩니다';
        document.querySelector(`[name="selector-1"]`).disabled = true;
    }
}

// 테스트 케이스 제거
function removeTestCase(id) {
    const element = document.getElementById(`test-case-${id}`);
    if (element) {
        element.remove();
    }
}

// 탭 전환
function showTab(tabName) {
    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.result-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 모든 패널 숨기기
    document.querySelectorAll('.result-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // 선택된 탭 활성화
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// 코드 복사
function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    const text = codeElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // 복사 성공 알림
        const button = event.target.closest('.copy-btn');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> 복사됨';
        button.style.background = 'rgba(76, 175, 80, 0.2)';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.background = '';
        }, 2000);
    });
}

// 메시지 표시
function showMessage(message, type = 'success') {
    const messagesContainer = document.getElementById('messages');
    const messageClass = type === 'success' ? 'success-message' : 'error-message';
    const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
    
    const messageHtml = `
        <div class="${messageClass}">
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        </div>
    `;
    
    messagesContainer.innerHTML = messageHtml;
    
    // 5초 후 메시지 제거
    setTimeout(() => {
        messagesContainer.innerHTML = '';
    }, 5000);
}

// 테스트 코드 생성
async function generateTestCode() {
    const generateBtn = document.querySelector('.generate-btn');
    const resultSection = document.getElementById('result-section');
    
    // 입력값 검증
    const websiteUrl = document.getElementById('website-url').value;
    if (!websiteUrl) {
        alert('웹사이트 URL을 입력해주세요.');
        return;
    }
    
    // 로딩 상태
    const originalText = generateBtn.innerHTML;
    generateBtn.innerHTML = '<div class="loading"></div> 코드 생성 중...';
    generateBtn.disabled = true;
    
    try {
        // 테스트 케이스 수집
        const testCases = [];
        document.querySelectorAll('.test-case-item').forEach((item, index) => {
            const id = index + 1;
            const action = document.querySelector(`[name="action-${id}"]`)?.value;
            const selector = document.querySelector(`[name="selector-${id}"]`)?.value;
            const value = document.querySelector(`[name="value-${id}"]`)?.value;
            
            if (action) {
                testCases.push({
                    action: action,
                    selector: selector || '',
                    value: value || ''
                });
            }
        });
        
        // API 요청 데이터 준비
        const requestData = {
            url: websiteUrl,
            description: document.getElementById('website-description').value,
            test_purpose: document.getElementById('test-purpose').value,
            test_scenarios: testCases,
            options: Array.from(activeOptions),
            auto_healing: activeOptions.has('auto-healing'),
            quality_checks: activeOptions.has('quality-check'),
            monitoring: true
        };
        
        console.log('Sending request:', requestData);
        
        // Firebase Cloud Functions API 호출
        const apiUrl = getApiUrl();
        const response = await fetch(`${apiUrl}/generateTestCode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Received response:', result);
        
        // 결과 표시
        displayGeneratedCode(result);
        resultSection.classList.add('show');
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        showMessage('테스트 코드가 성공적으로 생성되었습니다!');
        
    } catch (error) {
        console.error('Error generating test code:', error);
        showMessage('API 연결 중 오류가 발생했습니다. 데모 코드를 표시합니다.', 'error');
        
        // 데모용 코드 표시 (API 연결 실패 시)
        displayDemoCode(requestData);
        resultSection.classList.add('show');
        resultSection.scrollIntoView({ behavior: 'smooth' });
    } finally {
        // 버튼 복원
        generateBtn.innerHTML = originalText;
        generateBtn.disabled = false;
    }
}

// 생성된 코드 표시
function displayGeneratedCode(result) {
    // Python 코드
    if (result.python_code) {
        document.getElementById('python-code-content').textContent = result.python_code;
    }
    
    // JavaScript 코드
    if (result.javascript_code) {
        document.getElementById('js-code-content').textContent = result.javascript_code;
    }
    
    // 설정 파일
    if (result.config) {
        document.getElementById('config-content').textContent = JSON.stringify(result.config, null, 2);
    }
    
    // 실행 가이드
    if (result.execution_guide) {
        document.getElementById('execution-steps').innerHTML = result.execution_guide;
    }
    
    // 코드 하이라이팅 적용
    Prism.highlightAll();
}

// 데모용 코드 표시 (API 연결 전)
function displayDemoCode(requestData) {
    const pythonCode = generateDemoPythonCode(requestData);
    const jsCode = generateDemoJavaScriptCode(requestData);
    const config = generateDemoConfig(requestData);
    const guide = generateDemoGuide();
    
    document.getElementById('python-code-content').textContent = pythonCode;
    document.getElementById('js-code-content').textContent = jsCode;
    document.getElementById('config-content').textContent = JSON.stringify(config, null, 2);
    document.getElementById('execution-steps').innerHTML = guide;
    
    // 코드 하이라이팅 적용
    Prism.highlightAll();
}

// 데모 Python 코드 생성
function generateDemoPythonCode(requestData) {
    const testPurpose = (requestData.test_purpose || 'main_scenario').replace(/\s+/g, '_');
    
    return `#!/usr/bin/env python3
"""
자동 생성된 테스트 코드 - ${requestData.url}
Google ADK + Playwright MCP 기반 웹 자동화 테스트
생성 시간: ${new Date().toLocaleString('ko-KR')}
"""

import asyncio
import json
from datetime import datetime
from multi_tool_agent.adk_playwright_mcp_agent import ADKPlaywrightMCPAgent

class GeneratedTestSuite:
    def __init__(self):
        self.agent = ADKPlaywrightMCPAgent()
        self.test_url = "${requestData.url}"
        self.results = []
    
    async def setup(self):
        """테스트 환경 설정"""
        print("🔧 테스트 환경 설정 중...")
        await self.agent._initialize_agent()
        print("✅ Google ADK + Playwright MCP 에이전트 초기화 완료")
    
    async def test_${testPurpose}(self):
        """${requestData.test_purpose || '메인 테스트 시나리오'}"""
        try:
            print(f"🚀 테스트 시작: {self.test_url}")
            
            # 브라우저 시작 및 페이지 이동
            print("📂 브라우저 시작...")
            await self.agent.navigate_to_page(self.test_url)
            ${requestData.options.includes('screenshot') ? 'await self.agent.take_screenshot("01_initial_page")' : ''}
            
${requestData.test_scenarios.map((scenario, index) => 
    generatePythonTestStep(scenario, index + 1)
).join('\n')}
            
            ${requestData.options.includes('quality-check') ? `
            # 품질 검사 실행
            print("📊 품질 검사 실행 중...")
            quality_score = await self.agent.assess_page_quality()
            print(f"📊 페이지 품질 점수: {quality_score}/100")
            ` : ''}
            
            ${requestData.options.includes('screenshot') ? 'await self.agent.take_screenshot("99_final_result")' : ''}
            
            print("✅ 테스트 완료")
            return {
                "status": "success",
                "url": self.test_url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
            ${requestData.options.includes('auto-healing') ? `
            # 자동 복구 시도
            print("🔧 자동 복구 시도 중...")
            healing_result = await self.agent.attempt_auto_healing(str(e))
            if healing_result:
                print("✨ 자동 복구 성공! 테스트 재시도")
                return await self.test_${testPurpose}()
            else:
                print("💥 자동 복구 실패")
            ` : ''}
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 50)
        print("🎯 LLM Quality Radar 테스트 스위트 시작")
        print("=" * 50)
        
        await self.setup()
        
        test_methods = [
            self.test_${testPurpose}
        ]
        
        results = []
        for test_method in test_methods:
            print(f"\\n▶️ {test_method.__name__} 실행 중...")
            start_time = datetime.now()
            
            result = await test_method()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            test_result = {
                'test_name': test_method.__name__,
                'result': result,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            results.append(test_result)
        
        # 결과 요약 출력
        print("\\n" + "=" * 50)
        print("📋 테스트 결과 요약")
        print("=" * 50)
        
        total_tests = len(results)
        success_count = sum(1 for r in results if r['result'].get('status') == 'success')
        
        for result in results:
            status_icon = "✅" if result['result'].get('status') == 'success' else "❌"
            status_text = result['result'].get('status', 'unknown').upper()
            
            print(f"{status_icon} {result['test_name']}: {status_text} ({result['duration_seconds']:.2f}초)")
        
        print(f"\\n📊 전체 결과: {success_count}/{total_tests} 성공")
        print(f"⏱️ 총 소요 시간: {sum(r['duration_seconds'] for r in results):.2f}초")
        
        return results

async def main():
    """메인 실행 함수"""
    test_suite = GeneratedTestSuite()
    results = await test_suite.run_all_tests()
    
    # JSON 파일로 결과 저장
    output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\\n💾 상세 결과가 {output_file}에 저장되었습니다.")
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())`;
}

function generatePythonTestStep(scenario, stepNum) {
    const indent = "            ";
    
    switch(scenario.action) {
        case 'navigate':
            return `${indent}# 단계 ${stepNum}: 페이지 이동
${indent}print("🌐 페이지 이동 중...")
${indent}await self.agent.navigate_to_page("${scenario.selector || requestData.url}")`;
            
        case 'click':
            return `${indent}# 단계 ${stepNum}: 클릭 동작
${indent}print("👆 요소 클릭: ${scenario.selector}")
${indent}await self.agent.click_element("${scenario.selector}")`;
            
        case 'type':
            return `${indent}# 단계 ${stepNum}: 텍스트 입력
${indent}print("⌨️ 텍스트 입력: ${scenario.value}")
${indent}await self.agent.type_text("${scenario.selector}", "${scenario.value}")`;
            
        case 'wait':
            return `${indent}# 단계 ${stepNum}: 요소 대기
${indent}print("⏳ 요소 대기: ${scenario.selector}")
${indent}await self.agent.wait_for_element("${scenario.selector}")`;
            
        case 'assert':
            return `${indent}# 단계 ${stepNum}: 검증
${indent}print("✔️ 요소 검증: ${scenario.selector}")
${indent}assert await self.agent.verify_element("${scenario.selector}", "${scenario.value}")`;
            
        case 'screenshot':
            return `${indent}# 단계 ${stepNum}: 스크린샷 캡처
${indent}print("📸 스크린샷 캡처")
${indent}await self.agent.take_screenshot("step_${stepNum}_screenshot")`;
            
        default:
            return `${indent}# 단계 ${stepNum}: ${scenario.action}
${indent}print("🔧 사용자 정의 동작: ${scenario.action}")
${indent}await self.agent.execute_action("${scenario.action}", "${scenario.selector}", "${scenario.value}")`;
    }
}

// 데모 JavaScript 코드 생성
function generateDemoJavaScriptCode(requestData) {
    const testPurpose = (requestData.test_purpose || 'MainScenario').replace(/\s+/g, '');
    
    return `/**
 * 자동 생성된 테스트 코드 - ${requestData.url}
 * Google ADK + Playwright MCP 기반 웹 자동화 테스트
 * 생성 시간: ${new Date().toLocaleString('ko-KR')}
 */

const { ADKPlaywrightMCPClient } = require('./mcp_client');

class GeneratedTestSuite {
    constructor() {
        this.client = new ADKPlaywrightMCPClient();
        this.testUrl = '${requestData.url}';
        this.results = [];
    }
    
    async setup() {
        console.log('🔧 테스트 환경 설정 중...');
        await this.client.initialize();
        console.log('✅ Google ADK + Playwright MCP 클라이언트 초기화 완료');
    }
    
    async test${testPurpose}() {
        console.log('🚀 테스트 시작:', this.testUrl);
        
        try {
            // 브라우저 시작 및 페이지 이동
            console.log('📂 브라우저 시작...');
            await this.client.navigate(this.testUrl);
            ${requestData.options.includes('screenshot') ? 'await this.client.screenshot("01_initial_page");' : ''}
            
${requestData.test_scenarios.map((scenario, index) => 
    generateJSTestStep(scenario, index + 1)
).join('\n')}
            
            ${requestData.options.includes('quality-check') ? `
            // 품질 검사 실행
            console.log('📊 품질 검사 실행 중...');
            const qualityScore = await this.client.assessPageQuality();
            console.log('📊 페이지 품질 점수:', qualityScore + '/100');
            ` : ''}
            
            ${requestData.options.includes('screenshot') ? 'await this.client.screenshot("99_final_result");' : ''}
            
            console.log('✅ 테스트 완료');
            return {
                status: 'success',
                url: this.testUrl,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ 테스트 실패:', error);
            ${requestData.options.includes('auto-healing') ? `
            // 자동 복구 시도
            console.log('🔧 자동 복구 시도 중...');
            const healingResult = await this.client.attemptAutoHealing(error.message);
            if (healingResult) {
                console.log('✨ 자동 복구 성공! 테스트 재시도');
                return await this.test${testPurpose}();
            } else {
                console.log('💥 자동 복구 실패');
            }
            ` : ''}
            return {
                status: 'failed',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    async runAllTests() {
        console.log('='.repeat(50));
        console.log('🎯 LLM Quality Radar 테스트 스위트 시작');
        console.log('='.repeat(50));
        
        await this.setup();
        
        const testMethods = [
            this.test${testPurpose}
        ];
        
        const results = [];
        
        for (const testMethod of testMethods) {
            console.log(\`\\n▶️ \${testMethod.name} 실행 중...\`);
            const startTime = Date.now();
            
            const result = await testMethod.call(this);
            
            const endTime = Date.now();
            const duration = (endTime - startTime) / 1000;
            
            const testResult = {
                testName: testMethod.name,
                result: result,
                durationSeconds: duration,
                startTime: new Date(startTime).toISOString(),
                endTime: new Date(endTime).toISOString()
            };
            results.push(testResult);
        }
        
        // 결과 요약 출력
        console.log('\\n' + '='.repeat(50));
        console.log('📋 테스트 결과 요약');
        console.log('='.repeat(50));
        
        const totalTests = results.length;
        const successCount = results.filter(r => r.result.status === 'success').length;
        
        results.forEach(result => {
            const statusIcon = result.result.status === 'success' ? '✅' : '❌';
            const statusText = (result.result.status || 'unknown').toUpperCase();
            
            console.log(\`\${statusIcon} \${result.testName}: \${statusText} (\${result.durationSeconds.toFixed(2)}초)\`);
        });
        
        console.log(\`\\n📊 전체 결과: \${successCount}/\${totalTests} 성공\`);
        console.log(\`⏱️ 총 소요 시간: \${results.reduce((sum, r) => sum + r.durationSeconds, 0).toFixed(2)}초\`);
        
        return results;
    }
}

// 메인 실행
async function main() {
    const testSuite = new GeneratedTestSuite();
    const results = await testSuite.runAllTests();
    
    // JSON 파일로 결과 저장
    const fs = require('fs');
    const outputFile = \`test_results_\${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.json\`;
    fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
    
    console.log(\`\\n💾 상세 결과가 \${outputFile}에 저장되었습니다.\`);
    console.log('🎉 테스트 완료!');
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { GeneratedTestSuite };`;
}

function generateJSTestStep(scenario, stepNum) {
    const indent = "            ";
    
    switch(scenario.action) {
        case 'navigate':
            return `${indent}// 단계 ${stepNum}: 페이지 이동
${indent}console.log('🌐 페이지 이동 중...');
${indent}await this.client.navigate('${scenario.selector || requestData.url}');`;
            
        case 'click':
            return `${indent}// 단계 ${stepNum}: 클릭 동작
${indent}console.log('👆 요소 클릭: ${scenario.selector}');
${indent}await this.client.click('${scenario.selector}');`;
            
        case 'type':
            return `${indent}// 단계 ${stepNum}: 텍스트 입력
${indent}console.log('⌨️ 텍스트 입력: ${scenario.value}');
${indent}await this.client.type('${scenario.selector}', '${scenario.value}');`;
            
        case 'wait':
            return `${indent}// 단계 ${stepNum}: 요소 대기
${indent}console.log('⏳ 요소 대기: ${scenario.selector}');
${indent}await this.client.waitFor('${scenario.selector}');`;
            
        case 'assert':
            return `${indent}// 단계 ${stepNum}: 검증
${indent}console.log('✔️ 요소 검증: ${scenario.selector}');
${indent}await this.client.assert('${scenario.selector}', '${scenario.value}');`;
            
        case 'screenshot':
            return `${indent}// 단계 ${stepNum}: 스크린샷 캡처
${indent}console.log('📸 스크린샷 캡처');
${indent}await this.client.screenshot('step_${stepNum}_screenshot');`;
            
        default:
            return `${indent}// 단계 ${stepNum}: ${scenario.action}
${indent}console.log('🔧 사용자 정의 동작: ${scenario.action}');
${indent}await this.client.executeAction('${scenario.action}', '${scenario.selector}', '${scenario.value}');`;
    }
}

// 데모 설정 파일 생성
function generateDemoConfig(requestData) {
    return {
        "test_configuration": {
            "project_name": "LLM Quality Radar Test",
            "target_url": requestData.url,
            "test_purpose": requestData.test_purpose || "자동화 테스트",
            "generated_at": new Date().toISOString(),
            "browser_options": {
                "headless": false,
                "timeout": 30000,
                "viewport": {
                    "width": 1280,
                    "height": 720
                },
                "slow_mo": 1000
            },
            "google_adk": {
                "model": "gemini-2.0-flash-exp",
                "temperature": 0.1,
                "max_tokens": 4096,
                "system_instruction": "웹 자동화 테스트를 위한 AI 어시스턴트"
            },
            "playwright_mcp": {
                "server_url": "http://localhost:8933/mcp",
                "connection_type": "http_sse",
                "tools": [
                    "browser_navigate",
                    "browser_click", 
                    "browser_type",
                    "browser_screenshot",
                    "browser_wait_for",
                    "browser_close"
                ]
            },
            "test_options": {
                "auto_healing": requestData.options.includes('auto-healing'),
                "quality_checks": requestData.options.includes('quality-check'),
                "screenshots": requestData.options.includes('screenshot'),
                "accessibility_testing": requestData.options.includes('accessibility'),
                "performance_monitoring": true
            },
            "reporting": {
                "screenshot_path": "./screenshots",
                "report_format": ["json", "html"],
                "include_metrics": true,
                "save_page_source": true
            }
        },
        "test_scenarios": requestData.test_scenarios.map((scenario, index) => ({
            ...scenario,
            step_number: index + 1,
            description: getActionDescription(scenario.action)
        }))
    };
}

function getActionDescription(action) {
    const descriptions = {
        'navigate': '웹페이지로 이동',
        'click': '요소 클릭',
        'type': '텍스트 입력',
        'wait': '요소 로딩 대기',
        'assert': '요소 존재 검증',
        'screenshot': '화면 캡처'
    };
    return descriptions[action] || '사용자 정의 동작';
}

// 데모 실행 가이드 생성  
function generateDemoGuide() {
    return `
        <div style="line-height: 1.8; color: rgba(255, 255, 255, 0.9);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
                <h4 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">🚀 빠른 시작 가이드</h4>
                <p>생성된 테스트 코드를 즉시 실행할 수 있도록 단계별로 안내해드립니다.</p>
            </div>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">📦 1. 환경 설정</h4>
            <p style="margin-bottom: 1rem;">먼저 필요한 패키지를 설치하세요:</p>
            <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto;"><code># Python 패키지 설치
pip install google-adk playwright asyncio aiofiles

# Node.js 패키지 설치
npm install playwright @google-adk/core

# Playwright 브라우저 설치
npx playwright install</code></pre>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🔧 2. MCP 서버 시작</h4>
            <p style="margin-bottom: 1rem;">Playwright MCP 서버를 백그라운드에서 시작하세요:</p>
            <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto;"><code># 별도 터미널에서 MCP 서버 실행
node playwright_mcp_server.js

# 또는 백그라운드 실행 (Linux/Mac)
nohup node playwright_mcp_server.js &

# Windows에서 백그라운드 실행
start /B node playwright_mcp_server.js</code></pre>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🎯 3. 테스트 실행</h4>
            <p style="margin-bottom: 1rem;">생성된 테스트 코드를 실행하세요:</p>
            <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto;"><code># Python 버전 실행
python generated_test.py

# JavaScript 버전 실행
node generated_test.js

# 디버그 모드로 실행 (더 자세한 로그)
DEBUG=true python generated_test.py</code></pre>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">📊 4. 결과 확인</h4>
            <p style="margin-bottom: 1rem;">테스트 완료 후 다음 파일들이 생성됩니다:</p>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
                <ul style="margin-left: 1.5rem; margin-bottom: 0;">
                    <li style="margin-bottom: 0.5rem;"><strong>test_results_[timestamp].json</strong> - 상세한 테스트 결과 및 메트릭</li>
                    <li style="margin-bottom: 0.5rem;"><strong>screenshots/</strong> - 각 단계별 스크린샷 이미지</li>
                    <li style="margin-bottom: 0.5rem;"><strong>logs/</strong> - 실행 과정의 상세 로그</li>
                    <li style="margin-bottom: 0.5rem;"><strong>reports/</strong> - HTML 형태의 테스트 리포트</li>
                </ul>
            </div>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🔍 5. 문제 해결</h4>
            <div style="background: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
                <p style="margin-bottom: 1rem;"><strong>자주 발생하는 문제와 해결 방법:</strong></p>
                <ul style="margin-left: 1.5rem;">
                    <li style="margin-bottom: 0.8rem;"><strong>CSS 선택자 오류:</strong> 브라우저 개발자 도구(F12)에서 올바른 선택자를 확인하세요</li>
                    <li style="margin-bottom: 0.8rem;"><strong>요소 로딩 지연:</strong> wait 단계를 추가하거나 timeout 값을 늘려보세요</li>
                    <li style="margin-bottom: 0.8rem;"><strong>MCP 연결 실패:</strong> MCP 서버가 정상 실행 중인지 확인하세요 (포트 8933)</li>
                    <li style="margin-bottom: 0.8rem;"><strong>권한 오류:</strong> 브라우저 권한 설정을 확인하고 headless 모드를 시도해보세요</li>
                </ul>
            </div>
            
            <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">💡 6. 추가 팁</h4>
            <div style="background: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; padding: 1.5rem; border-radius: 8px;">
                <ul style="margin-left: 1.5rem; margin-bottom: 0;">
                    <li style="margin-bottom: 0.8rem;">테스트 속도를 높이려면 headless 모드를 사용하세요</li>
                    <li style="margin-bottom: 0.8rem;">복잡한 사이트의 경우 자동 복구 기능을 활성화하세요</li>
                    <li style="margin-bottom: 0.8rem;">정기적인 테스트를 위해 CI/CD 파이프라인에 통합하세요</li>
                    <li style="margin-bottom: 0.8rem;">테스트 결과를 모니터링 시스템과 연동하여 자동 알림을 설정하세요</li>
                </ul>
            </div>
        </div>
    `;
}
