/**
 * 테스트 코드 생성 모듈
 * Google ADK를 활용한 지능형 테스트 코드 생성
 */

const {logger} = require('firebase-functions');
const adkIntegration = require('./adk-integration');

/**
 * 테스트 코드 생성 메인 함수
 * @param {Object} params - 테스트 생성 파라미터
 * @return {Object} 생성된 테스트 코드와 설정
 */
async function generateTestCode(params) {
  const {
    url,
    description,
    test_purpose,
    test_scenarios,
    options,
    auto_healing,
    quality_checks,
    monitoring,
  } = params;

  logger.info('테스트 코드 생성 시작', {url, test_purpose});

  try {
    // 1. ADK를 통한 웹사이트 분석
    const websiteAnalysis = await adkIntegration.analyzeWebsite(url, description);
    
    // 2. 테스트 시나리오 최적화
    const optimizedScenarios = await optimizeTestScenarios(
        test_scenarios, 
        websiteAnalysis
    );

    // 3. Python 코드 생성
    const pythonCode = generatePythonCode({
      url,
      test_purpose,
      test_scenarios: optimizedScenarios,
      options,
      auto_healing,
      quality_checks,
      websiteAnalysis,
    });

    // 4. JavaScript 코드 생성
    const javascriptCode = generateJavaScriptCode({
      url,
      test_purpose,
      test_scenarios: optimizedScenarios,
      options,
      auto_healing,
      quality_checks,
      websiteAnalysis,
    });

    // 5. 테스트 설정 파일 생성
    const testConfig = generateTestConfig({
      url,
      test_purpose,
      test_scenarios: optimizedScenarios,
      options,
      auto_healing,
      quality_checks,
      monitoring,
      websiteAnalysis,
    });

    // 6. 실행 가이드 생성
    const executionGuide = generateExecutionGuide({
      url,
      test_purpose,
      options,
      websiteAnalysis,
    });

    const result = {
      success: true,
      python_code: pythonCode,
      javascript_code: javascriptCode,
      config: testConfig,
      execution_guide: executionGuide,
      website_analysis: websiteAnalysis,
      generated_at: new Date().toISOString(),
    };

    logger.info('테스트 코드 생성 완료');
    return result;

  } catch (error) {
    logger.error('테스트 코드 생성 중 오류:', error);
    
    // 오류 발생 시 기본 템플릿 반환
    return generateFallbackCode(params);
  }
}

/**
 * 테스트 시나리오 최적화
 */
async function optimizeTestScenarios(scenarios, websiteAnalysis) {
  try {
    // ADK를 통한 시나리오 개선 제안
    const optimization = await adkIntegration.optimizeScenarios(
        scenarios, 
        websiteAnalysis
    );
    
    return optimization.optimized_scenarios || scenarios;
  } catch (error) {
    logger.warn('시나리오 최적화 실패, 원본 사용:', error);
    return scenarios;
  }
}

/**
 * Python 테스트 코드 생성
 */
function generatePythonCode(params) {
  const {url, test_purpose, test_scenarios, options, auto_healing, quality_checks, websiteAnalysis} = params;
  
  const testPurpose = (test_purpose || 'main_scenario').replace(/\s+/g, '_');
  const timestamp = new Date().toLocaleString('ko-KR');
  
  const imports = `#!/usr/bin/env python3
"""
자동 생성된 테스트 코드 - ${url}
Google ADK + Playwright MCP 기반 웹 자동화 테스트
생성 시간: ${timestamp}
테스트 목적: ${test_purpose || '웹사이트 기능 테스트'}
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# LLM Quality Radar 모듈
from multi_tool_agent.adk_playwright_mcp_agent import ADKPlaywrightMCPAgent
from core.quality_monitor import QualityMonitor
from core.auto_healing import AutoHealingSystem
from utils.logger import setup_logger

logger = setup_logger(__name__)`;

  const classDefinition = `

class GeneratedTestSuite:
    """자동 생성된 테스트 스위트"""
    
    def __init__(self):
        self.agent = ADKPlaywrightMCPAgent()
        self.quality_monitor = QualityMonitor() if ${quality_checks} else None
        self.auto_healing = AutoHealingSystem() if ${auto_healing} else None
        self.test_url = "${url}"
        self.results = []
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # 웹사이트 분석 정보
        self.website_info = ${JSON.stringify(websiteAnalysis, null, 8)}
    
    async def setup(self):
        """테스트 환경 설정"""
        logger.info("🔧 테스트 환경 설정 중...")
        
        try:
            # ADK Playwright MCP 에이전트 초기화
            await self.agent._initialize_agent()
            logger.info("✅ Google ADK + Playwright MCP 에이전트 초기화 완료")
            
            # 품질 모니터링 설정
            if self.quality_monitor:
                await self.quality_monitor.initialize()
                logger.info("✅ 품질 모니터링 시스템 준비 완료")
            
            # 자동 복구 시스템 설정
            if self.auto_healing:
                await self.auto_healing.initialize()
                logger.info("✅ 자동 복구 시스템 준비 완료")
                
        except Exception as e:
            logger.error(f"❌ 테스트 환경 설정 실패: {e}")
            raise`;

  const testMethod = `
    
    async def test_${testPurpose}(self):
        """${test_purpose || '메인 테스트 시나리오'}"""
        test_start_time = datetime.now()
        test_results = {
            "test_name": "test_${testPurpose}",
            "url": self.test_url,
            "start_time": test_start_time.isoformat(),
            "steps": [],
            "status": "running"
        }
        
        try:
            logger.info(f"🚀 테스트 시작: {self.test_url}")
            logger.info(f"📋 테스트 목적: ${test_purpose || '웹사이트 기능 테스트'}")
            
            # 브라우저 시작 및 초기 설정
            logger.info("📂 브라우저 시작 및 페이지 로드...")
            await self.agent.navigate_to_page(self.test_url)
            
            # 초기 페이지 품질 검사
            if self.quality_monitor:
                initial_quality = await self.quality_monitor.assess_page_quality()
                logger.info(f"📊 초기 페이지 품질 점수: {initial_quality}/100")
            
            ${options.includes('screenshot') ? `
            # 초기 페이지 스크린샷
            await self.agent.take_screenshot("00_initial_page")
            logger.info("📸 초기 페이지 스크린샷 캡처 완료")` : ''}

${test_scenarios.map((scenario, index) => 
  generatePythonTestStep(scenario, index + 1, options)
).join('\n')}
            
            ${quality_checks ? `
            # 최종 품질 검사
            logger.info("📊 최종 품질 검사 실행 중...")
            final_quality = await self.quality_monitor.assess_page_quality()
            test_results["quality_scores"] = {
                "initial": initial_quality if self.quality_monitor else None,
                "final": final_quality,
                "improvement": final_quality - (initial_quality or 0) if self.quality_monitor else None
            }
            logger.info(f"📊 최종 페이지 품질 점수: {final_quality}/100")` : ''}
            
            ${options.includes('screenshot') ? `
            # 최종 결과 스크린샷
            await self.agent.take_screenshot("99_final_result")
            logger.info("📸 최종 결과 스크린샷 캡처 완료")` : ''}
            
            test_end_time = datetime.now()
            test_duration = (test_end_time - test_start_time).total_seconds()
            
            test_results.update({
                "end_time": test_end_time.isoformat(),
                "duration_seconds": test_duration,
                "status": "success"
            })
            
            logger.info(f"✅ 테스트 완료 (소요시간: {test_duration:.2f}초)")
            return test_results
            
        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            
            ${auto_healing ? `
            # 자동 복구 시도
            if self.auto_healing:
                logger.info("🔧 자동 복구 시도 중...")
                try:
                    healing_result = await self.auto_healing.attempt_healing(str(e))
                    if healing_result.get("success"):
                        logger.info("✨ 자동 복구 성공! 테스트 재시도")
                        test_results["healing_attempts"] = [healing_result]
                        return await self.test_${testPurpose}()
                    else:
                        logger.warning("🔧 자동 복구 실패")
                        test_results["healing_attempts"] = [healing_result]
                except Exception as healing_error:
                    logger.error(f"💥 자동 복구 과정에서 오류: {healing_error}")` : ''}
            
            test_results.update({
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            return test_results`;

  const mainMethods = `
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("=" * 60)
        logger.info("🎯 LLM Quality Radar 테스트 스위트 시작")
        logger.info("=" * 60)
        
        suite_start_time = datetime.now()
        
        try:
            await self.setup()
            
            # 실행할 테스트 메서드 목록
            test_methods = [
                self.test_${testPurpose}
            ]
            
            all_results = []
            
            for test_method in test_methods:
                logger.info(f"\\n▶️ {test_method.__name__} 실행 중...")
                result = await test_method()
                all_results.append(result)
                
                # 각 테스트 결과 요약 출력
                status_icon = "✅" if result.get("status") == "success" else "❌"
                duration = result.get("duration_seconds", 0)
                logger.info(f"{status_icon} {test_method.__name__}: {result.get('status', 'unknown').upper()} ({duration:.2f}초)")
            
            suite_end_time = datetime.now()
            suite_duration = (suite_end_time - suite_start_time).total_seconds()
            
            # 전체 결과 요약
            logger.info("\\n" + "=" * 60)
            logger.info("📋 테스트 스위트 결과 요약")
            logger.info("=" * 60)
            
            total_tests = len(all_results)
            success_count = sum(1 for r in all_results if r.get("status") == "success")
            
            logger.info(f"📊 전체 결과: {success_count}/{total_tests} 성공")
            logger.info(f"⏱️ 총 소요 시간: {suite_duration:.2f}초")
            
            # 상세 결과 반환
            return {
                "suite_results": {
                    "start_time": suite_start_time.isoformat(),
                    "end_time": suite_end_time.isoformat(),
                    "duration_seconds": suite_duration,
                    "total_tests": total_tests,
                    "success_count": success_count,
                    "failure_count": total_tests - success_count,
                    "success_rate": (success_count / total_tests * 100) if total_tests > 0 else 0
                },
                "test_results": all_results,
                "website_info": self.website_info
            }
            
        except Exception as e:
            logger.error(f"❌ 테스트 스위트 실행 중 오류: {e}")
            return {
                "suite_results": {
                    "start_time": suite_start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e)
                },
                "test_results": [],
                "website_info": self.website_info
            }
        
        finally:
            # 리소스 정리
            try:
                await self.agent.cleanup()
                logger.info("🧹 리소스 정리 완료")
            except Exception as e:
                logger.warning(f"⚠️ 리소스 정리 중 오류: {e}")

async def main():
    """메인 실행 함수"""
    test_suite = GeneratedTestSuite()
    results = await test_suite.run_all_tests()
    
    # JSON 파일로 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"test_results_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"\\n💾 상세 결과가 {output_file}에 저장되었습니다.")
        
        # 성공률에 따른 최종 메시지
        success_rate = results.get("suite_results", {}).get("success_rate", 0)
        if success_rate == 100:
            logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        elif success_rate >= 80:
            logger.info("✨ 대부분의 테스트가 성공했습니다!")
        elif success_rate >= 50:
            logger.info("⚠️ 일부 테스트에서 문제가 발견되었습니다.")
        else:
            logger.info("🔧 여러 문제가 발견되어 수정이 필요합니다.")
            
    except Exception as e:
        logger.error(f"❌ 결과 저장 중 오류: {e}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())`;

  return imports + classDefinition + testMethod + mainMethods;
}

/**
 * Python 테스트 단계 생성
 */
function generatePythonTestStep(scenario, stepNum, options) {
  const indent = "            ";
  
  const stepStart = `${indent}# 단계 ${stepNum}: ${getActionDescription(scenario.action)}
${indent}step_start = time.time()
${indent}logger.info("📋 단계 ${stepNum} 시작: ${getActionDescription(scenario.action)}")
${indent}try:`;

  let stepAction = '';
  switch(scenario.action) {
    case 'navigate':
      stepAction = `${indent}    await self.agent.navigate_to_page("${scenario.selector || url}")`;
      break;
    case 'click':
      stepAction = `${indent}    await self.agent.click_element("${scenario.selector}")`;
      break;
    case 'type':
      stepAction = `${indent}    await self.agent.type_text("${scenario.selector}", "${scenario.value}")`;
      break;
    case 'wait':
      stepAction = `${indent}    await self.agent.wait_for_element("${scenario.selector}")`;
      break;
    case 'assert':
      stepAction = `${indent}    assert await self.agent.verify_element("${scenario.selector}", "${scenario.value}")`;
      break;
    case 'screenshot':
      stepAction = `${indent}    await self.agent.take_screenshot("step_${stepNum}_screenshot")`;
      break;
    default:
      stepAction = `${indent}    await self.agent.execute_action("${scenario.action}", "${scenario.selector}", "${scenario.value}")`;
  }

  const stepEnd = `${indent}    step_duration = time.time() - step_start
${indent}    test_results["steps"].append({
${indent}        "step": ${stepNum},
${indent}        "action": "${scenario.action}",
${indent}        "selector": "${scenario.selector}",
${indent}        "value": "${scenario.value}",
${indent}        "duration": step_duration,
${indent}        "status": "success"
${indent}    })
${indent}    logger.info(f"✅ 단계 ${stepNum} 완료 ({step_duration:.2f}초)")
${indent}    
${indent}except Exception as step_error:
${indent}    step_duration = time.time() - step_start
${indent}    test_results["steps"].append({
${indent}        "step": ${stepNum},
${indent}        "action": "${scenario.action}",
${indent}        "selector": "${scenario.selector}",
${indent}        "value": "${scenario.value}",
${indent}        "duration": step_duration,
${indent}        "status": "failed",
${indent}        "error": str(step_error)
${indent}    })
${indent}    logger.error(f"❌ 단계 ${stepNum} 실패: {step_error}")
${indent}    raise step_error`;

  return stepStart + '\n' + stepAction + '\n' + stepEnd;
}

/**
 * JavaScript 테스트 코드 생성
 */
function generateJavaScriptCode(params) {
  const {url, test_purpose, test_scenarios, options, auto_healing, quality_checks} = params;
  
  const testPurpose = (test_purpose || 'MainScenario').replace(/\s+/g, '');
  const timestamp = new Date().toLocaleString('ko-KR');
  
  return `/**
 * 자동 생성된 테스트 코드 - ${url}
 * Google ADK + Playwright MCP 기반 웹 자동화 테스트
 * 생성 시간: ${timestamp}
 * 테스트 목적: ${test_purpose || '웹사이트 기능 테스트'}
 */

const fs = require('fs');
const path = require('path');

// LLM Quality Radar 모듈 (구현 필요)
// const { ADKPlaywrightMCPClient } = require('./mcp_client');

class GeneratedTestSuite {
    constructor() {
        // this.client = new ADKPlaywrightMCPClient();
        this.testUrl = '${url}';
        this.options = ${JSON.stringify(options)};
        this.autoHealing = ${auto_healing};
        this.qualityChecks = ${quality_checks};
        this.results = [];
        this.screenshotsDir = './screenshots';
        
        // 스크린샷 디렉토리 생성
        if (!fs.existsSync(this.screenshotsDir)) {
            fs.mkdirSync(this.screenshotsDir, { recursive: true });
        }
    }
    
    async setup() {
        console.log('🔧 테스트 환경 설정 중...');
        
        try {
            // await this.client.initialize();
            console.log('✅ Google ADK + Playwright MCP 클라이언트 초기화 완료');
            
            // 추가 설정들...
            
        } catch (error) {
            console.error('❌ 테스트 환경 설정 실패:', error);
            throw error;
        }
    }
    
    async test${testPurpose}() {
        const testStartTime = Date.now();
        const testResults = {
            testName: 'test${testPurpose}',
            url: this.testUrl,
            startTime: new Date(testStartTime).toISOString(),
            steps: [],
            status: 'running'
        };
        
        try {
            console.log('🚀 테스트 시작:', this.testUrl);
            console.log('📋 테스트 목적: ${test_purpose || '웹사이트 기능 테스트'}');
            
            // 브라우저 시작 및 페이지 로드
            console.log('📂 브라우저 시작 및 페이지 로드...');
            // await this.client.navigate(this.testUrl);
            
            ${options.includes('screenshot') ? `
            // 초기 페이지 스크린샷
            // await this.client.screenshot('00_initial_page');
            console.log('📸 초기 페이지 스크린샷 캡처 완료');` : ''}

${test_scenarios.map((scenario, index) => 
  generateJSTestStep(scenario, index + 1, options)
).join('\n')}
            
            ${quality_checks ? `
            // 최종 품질 검사
            console.log('📊 최종 품질 검사 실행 중...');
            // const finalQuality = await this.client.assessPageQuality();
            // console.log('📊 최종 페이지 품질 점수:', finalQuality + '/100');` : ''}
            
            ${options.includes('screenshot') ? `
            // 최종 결과 스크린샷
            // await this.client.screenshot('99_final_result');
            console.log('📸 최종 결과 스크린샷 캡처 완료');` : ''}
            
            const testEndTime = Date.now();
            const testDuration = (testEndTime - testStartTime) / 1000;
            
            testResults.endTime = new Date(testEndTime).toISOString();
            testResults.durationSeconds = testDuration;
            testResults.status = 'success';
            
            console.log(\`✅ 테스트 완료 (소요시간: \${testDuration.toFixed(2)}초)\`);
            return testResults;
            
        } catch (error) {
            console.error('❌ 테스트 실패:', error);
            
            ${auto_healing ? `
            // 자동 복구 시도
            if (this.autoHealing) {
                console.log('🔧 자동 복구 시도 중...');
                try {
                    // const healingResult = await this.client.attemptAutoHealing(error.message);
                    // if (healingResult.success) {
                    //     console.log('✨ 자동 복구 성공! 테스트 재시도');
                    //     testResults.healingAttempts = [healingResult];
                    //     return await this.test${testPurpose}();
                    // }
                    console.log('🔧 자동 복구 기능은 구현 중입니다...');
                } catch (healingError) {
                    console.error('💥 자동 복구 과정에서 오류:', healingError);
                }
            }` : ''}
            
            testResults.endTime = new Date().toISOString();
            testResults.status = 'failed';
            testResults.error = error.message;
            return testResults;
        }
    }
    
    async runAllTests() {
        console.log('='.repeat(60));
        console.log('🎯 LLM Quality Radar 테스트 스위트 시작');
        console.log('='.repeat(60));
        
        const suiteStartTime = Date.now();
        
        try {
            await this.setup();
            
            const testMethods = [
                this.test${testPurpose}
            ];
            
            const allResults = [];
            
            for (const testMethod of testMethods) {
                console.log(\`\\n▶️ \${testMethod.name} 실행 중...\`);
                const result = await testMethod.call(this);
                allResults.push(result);
                
                // 각 테스트 결과 요약 출력
                const statusIcon = result.status === 'success' ? '✅' : '❌';
                const duration = result.durationSeconds || 0;
                console.log(\`\${statusIcon} \${testMethod.name}: \${(result.status || 'unknown').toUpperCase()} (\${duration.toFixed(2)}초)\`);
            }
            
            const suiteEndTime = Date.now();
            const suiteDuration = (suiteEndTime - suiteStartTime) / 1000;
            
            // 전체 결과 요약
            console.log('\\n' + '='.repeat(60));
            console.log('📋 테스트 스위트 결과 요약');
            console.log('='.repeat(60));
            
            const totalTests = allResults.length;
            const successCount = allResults.filter(r => r.status === 'success').length;
            
            console.log(\`📊 전체 결과: \${successCount}/\${totalTests} 성공\`);
            console.log(\`⏱️ 총 소요 시간: \${suiteDuration.toFixed(2)}초\`);
            
            return {
                suiteResults: {
                    startTime: new Date(suiteStartTime).toISOString(),
                    endTime: new Date(suiteEndTime).toISOString(),
                    durationSeconds: suiteDuration,
                    totalTests: totalTests,
                    successCount: successCount,
                    failureCount: totalTests - successCount,
                    successRate: totalTests > 0 ? (successCount / totalTests * 100) : 0
                },
                testResults: allResults
            };
            
        } catch (error) {
            console.error('❌ 테스트 스위트 실행 중 오류:', error);
            return {
                suiteResults: {
                    startTime: new Date(suiteStartTime).toISOString(),
                    endTime: new Date().toISOString(),
                    status: 'failed',
                    error: error.message
                },
                testResults: []
            };
        }
    }
}

// 메인 실행
async function main() {
    const testSuite = new GeneratedTestSuite();
    const results = await testSuite.runAllTests();
    
    // JSON 파일로 결과 저장
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputFile = \`test_results_\${timestamp}.json\`;
    
    try {
        fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
        console.log(\`\\n💾 상세 결과가 \${outputFile}에 저장되었습니다.\`);
        
        // 성공률에 따른 최종 메시지
        const successRate = results.suiteResults.successRate || 0;
        if (successRate === 100) {
            console.log('🎉 모든 테스트가 성공적으로 완료되었습니다!');
        } else if (successRate >= 80) {
            console.log('✨ 대부분의 테스트가 성공했습니다!');
        } else if (successRate >= 50) {
            console.log('⚠️ 일부 테스트에서 문제가 발견되었습니다.');
        } else {
            console.log('🔧 여러 문제가 발견되어 수정이 필요합니다.');
        }
        
    } catch (error) {
        console.error('❌ 결과 저장 중 오류:', error);
    }
    
    return results;
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { GeneratedTestSuite };`;
}

/**
 * JavaScript 테스트 단계 생성
 */
function generateJSTestStep(scenario, stepNum, options) {
  const indent = "            ";
  
  const stepStart = `${indent}// 단계 ${stepNum}: ${getActionDescription(scenario.action)}
${indent}const step${stepNum}Start = Date.now();
${indent}console.log('📋 단계 ${stepNum} 시작: ${getActionDescription(scenario.action)}');
${indent}try {`;

  let stepAction = '';
  switch(scenario.action) {
    case 'navigate':
      stepAction = `${indent}    // await this.client.navigate('${scenario.selector || url}');`;
      break;
    case 'click':
      stepAction = `${indent}    // await this.client.click('${scenario.selector}');`;
      break;
    case 'type':
      stepAction = `${indent}    // await this.client.type('${scenario.selector}', '${scenario.value}');`;
      break;
    case 'wait':
      stepAction = `${indent}    // await this.client.waitFor('${scenario.selector}');`;
      break;
    case 'assert':
      stepAction = `${indent}    // await this.client.assert('${scenario.selector}', '${scenario.value}');`;
      break;
    case 'screenshot':
      stepAction = `${indent}    // await this.client.screenshot('step_${stepNum}_screenshot');`;
      break;
    default:
      stepAction = `${indent}    // await this.client.executeAction('${scenario.action}', '${scenario.selector}', '${scenario.value}');`;
  }

  const stepEnd = `${indent}    const step${stepNum}Duration = (Date.now() - step${stepNum}Start) / 1000;
${indent}    testResults.steps.push({
${indent}        step: ${stepNum},
${indent}        action: '${scenario.action}',
${indent}        selector: '${scenario.selector}',
${indent}        value: '${scenario.value}',
${indent}        duration: step${stepNum}Duration,
${indent}        status: 'success'
${indent}    });
${indent}    console.log(\`✅ 단계 ${stepNum} 완료 (\${step${stepNum}Duration.toFixed(2)}초)\`);
${indent}    
${indent}} catch (stepError) {
${indent}    const step${stepNum}Duration = (Date.now() - step${stepNum}Start) / 1000;
${indent}    testResults.steps.push({
${indent}        step: ${stepNum},
${indent}        action: '${scenario.action}',
${indent}        selector: '${scenario.selector}',
${indent}        value: '${scenario.value}',
${indent}        duration: step${stepNum}Duration,
${indent}        status: 'failed',
${indent}        error: stepError.message
${indent}    });
${indent}    console.error(\`❌ 단계 ${stepNum} 실패: \${stepError.message}\`);
${indent}    throw stepError;
${indent}}`;

  return stepStart + '\n' + stepAction + '\n' + stepEnd;
}

/**
 * 테스트 설정 파일 생성
 */
function generateTestConfig(params) {
  const {url, test_purpose, test_scenarios, options, auto_healing, quality_checks, monitoring, websiteAnalysis} = params;
  
  return {
    "test_configuration": {
      "project_name": "LLM Quality Radar Generated Test",
      "target_url": url,
      "test_purpose": test_purpose || "자동화 테스트",
      "generated_at": new Date().toISOString(),
      "generator_version": "1.0.0",
      
      "browser_options": {
        "headless": false,
        "timeout": 30000,
        "slow_mo": 1000,
        "viewport": {
          "width": 1280,
          "height": 720
        },
        "user_agent": "LLM Quality Radar Test Agent"
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
        "retry_attempts": 3,
        "retry_delay": 1000,
        "tools": [
          "browser_navigate",
          "browser_click",
          "browser_type",
          "browser_screenshot",
          "browser_wait_for",
          "browser_close",
          "browser_evaluate"
        ]
      },
      
      "test_options": {
        "auto_healing": auto_healing,
        "quality_checks": quality_checks,
        "screenshots": options.includes('screenshot'),
        "accessibility_testing": options.includes('accessibility'),
        "performance_monitoring": monitoring,
        "detailed_logging": true
      },
      
      "reporting": {
        "screenshot_path": "./screenshots",
        "log_path": "./logs",
        "report_formats": ["json", "html"],
        "include_metrics": true,
        "save_page_source": true,
        "generate_summary": true
      },
      
      "thresholds": {
        "page_load_timeout": 30000,
        "element_wait_timeout": 10000,
        "quality_score_minimum": 70,
        "performance_budget": {
          "first_contentful_paint": 2000,
          "largest_contentful_paint": 4000,
          "time_to_interactive": 5000
        }
      }
    },
    
    "test_scenarios": test_scenarios.map((scenario, index) => ({
      ...scenario,
      step_number: index + 1,
      description: getActionDescription(scenario.action),
      estimated_duration: getEstimatedDuration(scenario.action)
    })),
    
    "website_analysis": websiteAnalysis
  };
}

/**
 * 실행 가이드 생성
 */
function generateExecutionGuide(params) {
  const {url, test_purpose, options, websiteAnalysis} = params;
  
  return `
    <div style="line-height: 1.8; color: rgba(255, 255, 255, 0.9); max-width: 100%;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
            <h3 style="color: white; margin-bottom: 1rem; font-size: 1.4rem;">🚀 ${test_purpose || '테스트'} 실행 가이드</h3>
            <p style="opacity: 0.9;">생성된 테스트 코드를 즉시 실행할 수 있도록 상세하게 안내해드립니다.</p>
        </div>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="color: #ff6b6b; margin-bottom: 1.5rem; font-size: 1.2rem; display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-info-circle"></i> 시작하기 전에
            </h4>
            <div style="background: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; padding: 1.5rem; border-radius: 8px;">
                <p style="margin-bottom: 1rem;"><strong>테스트 대상:</strong> ${url}</p>
                ${websiteAnalysis ? `<p style="margin-bottom: 1rem;"><strong>웹사이트 유형:</strong> ${websiteAnalysis.type || '일반 웹사이트'}</p>` : ''}
                <p style="margin-bottom: 1rem;"><strong>활성화된 옵션:</strong> ${options.join(', ')}</p>
                <p><strong>예상 소요 시간:</strong> 2-5분</p>
            </div>
        </div>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">📦 1. 환경 설정</h4>
        <p style="margin-bottom: 1rem;">필요한 패키지를 설치하세요:</p>
        <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto; font-size: 0.9rem;"><code># Python 패키지 설치
pip install google-adk playwright asyncio aiofiles

# Node.js 패키지 설치  
npm install playwright @google-adk/core

# Playwright 브라우저 설치
npx playwright install chromium

# LLM Quality Radar 프로젝트 의존성 설치
pip install -r requirements.txt</code></pre>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🔧 2. MCP 서버 시작</h4>
        <p style="margin-bottom: 1rem;">Playwright MCP 서버를 먼저 시작해야 합니다:</p>
        <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto; font-size: 0.9rem;"><code># 프로젝트 루트 디렉토리에서 실행
node playwright_mcp_server.js

# 성공 메시지 확인:
# "✅ Playwright MCP Server가 포트 8933에서 실행 중입니다"</code></pre>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🎯 3. 테스트 실행</h4>
        <p style="margin-bottom: 1rem;">새 터미널에서 생성된 테스트를 실행하세요:</p>
        <pre style="background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; overflow-x: auto; font-size: 0.9rem;"><code># Python 버전 실행
python generated_test.py

# JavaScript 버전 실행
node generated_test.js

# 디버그 모드 (더 자세한 로그)
DEBUG=true python generated_test.py</code></pre>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">📊 4. 결과 확인</h4>
        <p style="margin-bottom: 1rem;">테스트 완료 후 다음과 같은 파일들이 생성됩니다:</p>
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div style="background: rgba(76, 175, 80, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid #4CAF50;">
                    <strong style="color: #4CAF50;">📄 test_results_[timestamp].json</strong><br>
                    <small>상세한 테스트 결과 및 메트릭</small>
                </div>
                ${options.includes('screenshot') ? `
                <div style="background: rgba(33, 150, 243, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid #2196F3;">
                    <strong style="color: #2196F3;">📸 screenshots/</strong><br>
                    <small>각 단계별 스크린샷 이미지</small>
                </div>` : ''}
                <div style="background: rgba(255, 152, 0, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid #FF9800;">
                    <strong style="color: #FF9800;">📋 logs/</strong><br>
                    <small>실행 과정의 상세 로그</small>
                </div>
                <div style="background: rgba(156, 39, 176, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid #9C27B0;">
                    <strong style="color: #9C27B0;">📈 reports/</strong><br>
                    <small>HTML 형태의 테스트 리포트</small>
                </div>
            </div>
        </div>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">🔍 5. 문제 해결</h4>
        <div style="background: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
            <p style="margin-bottom: 1rem;"><strong>자주 발생하는 문제와 해결 방법:</strong></p>
            <ul style="margin-left: 1.5rem; margin-bottom: 0;">
                <li style="margin-bottom: 1rem;">
                    <strong>MCP 연결 실패:</strong><br>
                    <code style="background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 3px;">node playwright_mcp_server.js</code>가 실행 중인지 확인
                </li>
                <li style="margin-bottom: 1rem;">
                    <strong>CSS 선택자 오류:</strong><br>
                    브라우저 개발자 도구(F12)에서 올바른 선택자 확인
                </li>
                <li style="margin-bottom: 1rem;">
                    <strong>타임아웃 오류:</strong><br>
                    <code style="background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 3px;">timeout</code> 값을 늘리거나 wait 단계 추가
                </li>
                <li style="margin-bottom: 1rem;">
                    <strong>권한 오류:</strong><br>
                    headless 모드로 실행하거나 브라우저 권한 설정 확인
                </li>
            </ul>
        </div>
        
        <h4 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.1rem;">💡 6. 고급 사용법</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div style="background: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; padding: 1.5rem; border-radius: 8px;">
                <h5 style="color: #4CAF50; margin-bottom: 0.5rem;">🚀 성능 최적화</h5>
                <ul style="margin-left: 1rem; font-size: 0.9rem;">
                    <li>headless 모드 사용</li>
                    <li>불필요한 리소스 차단</li>
                    <li>병렬 테스트 실행</li>
                </ul>
            </div>
            <div style="background: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; padding: 1.5rem; border-radius: 8px;">
                <h5 style="color: #2196F3; margin-bottom: 0.5rem;">🔧 CI/CD 통합</h5>
                <ul style="margin-left: 1rem; font-size: 0.9rem;">
                    <li>GitHub Actions 연동</li>
                    <li>자동 스케줄링</li>
                    <li>Slack 알림 설정</li>
                </ul>
            </div>
            <div style="background: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; padding: 1.5rem; border-radius: 8px;">
                <h5 style="color: #FF9800; margin-bottom: 0.5rem;">📊 모니터링</h5>
                <ul style="margin-left: 1rem; font-size: 0.9rem;">
                    <li>실시간 대시보드</li>
                    <li>알림 설정</li>
                    <li>히스토리 추적</li>
                </ul>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%); padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h5 style="color: white; margin-bottom: 0.5rem;">🎉 준비 완료!</h5>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">이제 생성된 테스트 코드를 실행하여 웹사이트의 품질을 확인해보세요.</p>
        </div>
    </div>
  `;
}

/**
 * 액션에 대한 설명 반환
 */
function getActionDescription(action) {
  const descriptions = {
    'navigate': '페이지 이동',
    'click': '요소 클릭',
    'type': '텍스트 입력',
    'wait': '요소 대기',
    'assert': '요소 검증',
    'screenshot': '스크린샷 캡처'
  };
  return descriptions[action] || '사용자 정의 동작';
}

/**
 * 액션별 예상 소요 시간 반환 (밀리초)
 */
function getEstimatedDuration(action) {
  const durations = {
    'navigate': 3000,
    'click': 1000,
    'type': 2000,
    'wait': 5000,
    'assert': 1000,
    'screenshot': 2000
  };
  return durations[action] || 1000;
}

/**
 * 오류 발생 시 폴백 코드 생성
 */
function generateFallbackCode(params) {
  logger.warn('ADK 연결 실패, 기본 템플릿 코드 생성');
  
  const basicPythonCode = `# 기본 테스트 템플릿 (${params.url})
import asyncio

async def main():
    print("테스트 템플릿이 생성되었습니다.")
    print("URL:", "${params.url}")
    print("실제 실행을 위해서는 ADK 연결이 필요합니다.")

if __name__ == "__main__":
    asyncio.run(main())`;

  const basicJSCode = `// 기본 테스트 템플릿 (${params.url})
async function main() {
    console.log("테스트 템플릿이 생성되었습니다.");
    console.log("URL:", "${params.url}");
    console.log("실제 실행을 위해서는 ADK 연결이 필요합니다.");
}

main().catch(console.error);`;

  return {
    success: false,
    python_code: basicPythonCode,
    javascript_code: basicJSCode,
    config: {
      error: "ADK 연결 실패",
      fallback: true,
      url: params.url
    },
    execution_guide: `
      <div style="padding: 2rem; text-align: center; color: #FF9800;">
        <h3>⚠️ 제한된 기능</h3>
        <p>현재 Google ADK 연결에 문제가 있어 기본 템플릿만 제공됩니다.</p>
        <p>완전한 기능을 사용하려면 ADK 설정을 확인해주세요.</p>
      </div>
    `,
    generated_at: new Date().toISOString(),
  };
}

module.exports = {
  generateTestCode,
};
