/**
 * Firebase Cloud Functions for LLM Quality Radar
 * Google ADK + Playwright MCP 기반 테스트 코드 생성 API
 */

const {onRequest} = require('firebase-functions/v2/https');
const {logger} = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({origin: true});
const fetch = require('node-fetch');

// Firebase Admin 초기화
admin.initializeApp();

// API 엔드포인트들
const testGenerator = require('./api/test-generator');
const adkIntegration = require('./api/adk-integration');
const testApi = require('./test-api');

/**
 * 테스트 코드 생성 API
 */
exports.generateTestCode = onRequest({
  cors: true,
  memory: '1GiB',
  timeoutSeconds: 300,
}, async (req, res) => {
  return cors(req, res, async () => {
    try {
      logger.info('테스트 코드 생성 요청 수신', req.body);

      if (req.method !== 'POST') {
        return res.status(405).json({error: 'Method not allowed'});
      }

      const {
        url,
        description,
        test_purpose,
        test_scenarios,
        options,
        auto_healing,
        quality_checks,
        monitoring,
      } = req.body;

      // 입력 검증
      if (!url) {
        return res.status(400).json({error: 'URL is required'});
      }

      if (!test_scenarios || !Array.isArray(test_scenarios)) {
        return res.status(400).json({error: 'Test scenarios are required'});
      }

      // 테스트 코드 생성
      const result = await testGenerator.generateTestCode({
        url,
        description,
        test_purpose,
        test_scenarios,
        options: options || [],
        auto_healing: auto_healing || false,
        quality_checks: quality_checks || false,
        monitoring: monitoring || false,
      });

      logger.info('테스트 코드 생성 완료');
      return res.json(result);
    } catch (error) {
      logger.error('테스트 코드 생성 중 오류:', error);
      return res.status(500).json({
        error: error.message,
        details: 'Internal server error during test code generation',
      });
    }
  });
});

/**
 * ADK 모델 상태 확인 API
 */
exports.checkAdkStatus = onRequest({cors: true}, async (req, res) => {
  return cors(req, res, async () => {
    try {
      const status = await adkIntegration.checkAdkStatus();
      return res.json(status);
    } catch (error) {
      logger.error('ADK 상태 확인 중 오류:', error);
      return res.status(500).json({error: error.message});
    }
  });
});

/**
 * 테스트 결과 저장 API
 */
exports.saveTestResult = onRequest({cors: true}, async (req, res) => {
  return cors(req, res, async () => {
    try {
      if (req.method !== 'POST') {
        return res.status(405).json({error: 'Method not allowed'});
      }

      const testResult = req.body;
      const db = admin.firestore();

      // Firestore에 결과 저장
      const docRef = await db.collection('test_results').add({
        ...testResult,
        timestamp: admin.firestore.FieldValue.serverTimestamp(),
      });

      logger.info('테스트 결과 저장 완료:', docRef.id);
      return res.json({
        success: true,
        id: docRef.id,
        message: 'Test result saved successfully',
      });
    } catch (error) {
      logger.error('테스트 결과 저장 중 오류:', error);
      return res.status(500).json({error: error.message});
    }
  });
});

/**
 * 저장된 테스트 결과 조회 API
 */
exports.getTestResults = onRequest({cors: true}, async (req, res) => {
  return cors(req, res, async () => {
    try {
      const db = admin.firestore();
      const limit = parseInt(req.query.limit) || 50;

      const snapshot = await db.collection('test_results')
          .orderBy('timestamp', 'desc')
          .limit(limit)
          .get();

      const results = [];
      snapshot.forEach((doc) => {
        results.push({
          id: doc.id,
          ...doc.data(),
        });
      });

      return res.json({
        results,
        count: results.length,
      });
    } catch (error) {
      logger.error('테스트 결과 조회 중 오류:', error);
      return res.status(500).json({error: error.message});
    }
  });
});

/**
 * 헬스 체크 API
 */
exports.healthCheck = onRequest({cors: true}, (req, res) => {
  return cors(req, res, () => {
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      services: {
        firebase: 'connected',
        adk: 'available',
        mcp: 'ready',
      },
    });
  });
});

// 테스트 API 익스포트
exports.testApi = testApi.testApi;
exports.mockTestGeneration = testApi.mockTestGeneration;

/**
 * 자동 테스트 케이스 생성 프록시 (Cloud Run의 FastAPI로 전달)
 */
exports.generateAutoTestCases = onRequest({
  cors: true,
  memory: '1GiB',
  timeoutSeconds: 300,
}, async (req, res) => {
  return cors(req, res, async () => {
    try {
      if (req.method !== 'POST') {
        return res.status(405).json({error: 'Method not allowed'});
      }

      const {url, test_type} = req.body || {};
      if (!url) return res.status(400).json({error: 'URL is required'});

      const base = process.env.AUTO_TEST_API_BASE || 'http://localhost:8001';
      const upstream = `${base}/test/generate-cases`;
      const upstreamResp = await fetch(upstream, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, test_type: test_type || 'comprehensive'})
      });

      const data = await upstreamResp.json().catch(() => ({}));
      if (!upstreamResp.ok) {
        const msg = data.detail || data.error || 'Upstream error';
        return res.status(upstreamResp.status).json({error: msg});
      }
      return res.json(data);
    } catch (error) {
      logger.error('generateAutoTestCases error:', error);
      return res.status(500).json({error: error.message || 'internal error'});
    }
  });
});
