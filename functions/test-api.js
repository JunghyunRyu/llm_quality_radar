/**
 * 간단한 테스트 API - Functions 동작 확인용
 */

const {onRequest} = require('firebase-functions/v2/https');
const cors = require('cors')({origin: true});

/**
 * 기본 테스트 API
 */
exports.testApi = onRequest({cors: true}, (req, res) => {
  return cors(req, res, () => {
    const testData = {
      status: 'success',
      message: 'Firebase Functions가 정상적으로 작동하고 있습니다!',
      timestamp: new Date().toISOString(),
      method: req.method,
      path: req.path,
      userAgent: req.get('User-Agent'),
      environment: {
        node_version: process.version,
        platform: process.platform,
        memory_usage: process.memoryUsage(),
      },
      firebase_functions: {
        region: process.env.FUNCTION_REGION || 'us-central1',
        project: process.env.GCLOUD_PROJECT || 'unknown',
      }
    };

    res.json(testData);
  });
});

/**
 * 간단한 테스트 코드 생성 API (모킹)
 */
exports.mockTestGeneration = onRequest({
  cors: true,
  memory: '512MiB',
  timeoutSeconds: 60,
}, (req, res) => {
  return cors(req, res, () => {
    if (req.method !== 'POST') {
      return res.status(405).json({error: 'POST method required'});
    }

    const {url, test_purpose, test_scenarios} = req.body;

    if (!url) {
      return res.status(400).json({error: 'URL is required'});
    }

    // 모킹된 테스트 코드 생성 결과
    const mockResult = {
      success: true,
      message: 'Mock 테스트 코드가 생성되었습니다',
      input: {
        url,
        test_purpose: test_purpose || '기본 테스트',
        scenarios_count: test_scenarios ? test_scenarios.length : 0,
      },
      python_code: `# Mock Python 테스트 코드
import asyncio
import pytest

async def test_website():
    """${test_purpose || '기본 테스트'}"""
    print("테스트 대상: ${url}")
    print("Firebase Functions에서 생성된 Mock 코드입니다.")
    assert True  # 항상 성공

if __name__ == "__main__":
    asyncio.run(test_website())`,
      
      javascript_code: `// Mock JavaScript 테스트 코드
const assert = require('assert');

async function testWebsite() {
  console.log('테스트 대상: ${url}');
  console.log('Firebase Functions에서 생성된 Mock 코드입니다.');
  
  // Mock 테스트
  assert(true, '테스트 통과');
  return { status: 'success', url: '${url}' };
}

testWebsite().then(console.log).catch(console.error);`,

      config: {
        project_name: 'LLM Quality Radar Test',
        target_url: url,
        test_purpose: test_purpose || '기본 테스트',
        generated_at: new Date().toISOString(),
        mock: true,
        note: 'This is a mock response. Full ADK integration is in progress.'
      },
      
      execution_guide: `
        <div style="padding: 1rem; background: rgba(255, 152, 0, 0.1); border-radius: 8px;">
          <h4 style="color: #FF9800; margin-bottom: 1rem;">🔧 Mock 모드</h4>
          <p>현재 Firebase Functions가 정상 작동하는 것을 확인했습니다!</p>
          <p>실제 Google ADK 연동을 위해서는 API 키 설정이 필요합니다.</p>
          <ul style="margin-left: 1.5rem;">
            <li>테스트 대상: ${url}</li>
            <li>생성 시간: ${new Date().toLocaleString('ko-KR')}</li>
            <li>상태: Functions 연결 성공 ✅</li>
          </ul>
        </div>
      `,
      
      generated_at: new Date().toISOString(),
    };

    res.json(mockResult);
  });
});
