#!/usr/bin/env node
/**
 * 개선된 Playwright MCP HTTP 서버
 * SSE와 MCP 프로토콜을 올바르게 구현
 */

import http from 'http';
import { randomUUID } from 'crypto';

// MCP 관련 import
let createConnection, SSEServerTransport, Server;
try {
  const playwrightMcp = await import('@playwright/mcp');
  createConnection = playwrightMcp.createConnection;
  console.log('✅ @playwright/mcp 모듈 로드 성공');
} catch (error) {
  console.error('❌ @playwright/mcp 모듈 로드 실패:', error.message);
  process.exit(1);
}

try {
  const mcpSdk = await import('@modelcontextprotocol/sdk/server/sse.js');
  SSEServerTransport = mcpSdk.SSEServerTransport;
  const mcpServer = await import('@modelcontextprotocol/sdk/server/index.js');
  Server = mcpServer.Server;
  console.log('✅ @modelcontextprotocol/sdk 모듈 로드 성공');
} catch (error) {
  console.error('❌ @modelcontextprotocol/sdk 모듈 로드 실패:', error.message);
  console.log('💡 기본 MCP 구현으로 대체합니다.');
}

const PORT = process.env.PORT || 8933;
const HOST = process.env.HOST || 'localhost';

// Playwright MCP 서버 설정
const playwrightConfig = {
  browser: {
    launchOptions: {
      headless: process.env.PLAYWRIGHT_HEADLESS !== 'false',
      channel: process.env.PLAYWRIGHT_BROWSER || 'chrome'
    }
  },
  capabilities: ['tabs', 'pdf', 'vision'],
  outputDir: './playwright-outputs'
};

console.log('🎭 개선된 Playwright MCP HTTP 서버 시작 중...');
console.log(`설정:`, playwrightConfig);

// 연결된 클라이언트 관리
const connectedClients = new Map();

// MCP 서버 인스턴스 생성 함수
async function createMCPServer() {
  try {
    const connection = await createConnection(playwrightConfig);
    console.log('✅ Playwright 연결 생성됨');
    return connection;
  } catch (error) {
    console.error('❌ Playwright 연결 생성 실패:', error);
    throw error;
  }
}

// MCP JSON-RPC 메시지 헬퍼 함수들
function sendMCPNotification(res, method, params = {}) {
  const message = {
    jsonrpc: "2.0",
    method: method,
    params: params
  };
  res.write(`data: ${JSON.stringify(message)}\n\n`);
}

function sendMCPResponse(res, id, result) {
  const message = {
    jsonrpc: "2.0",
    id: id,
    result: result
  };
  res.write(`data: ${JSON.stringify(message)}\n\n`);
}

function sendMCPError(res, id, error) {
  const message = {
    jsonrpc: "2.0",
    id: id,
    error: {
      code: -32603,
      message: error.message || "Internal error",
      data: error.data || null
    }
  };
  res.write(`data: ${JSON.stringify(message)}\n\n`);
}

function setupSSEHeaders(res) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'X-Accel-Buffering': 'no'
  });
}

const server = http.createServer(async (req, res) => {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy', 
      timestamp: new Date().toISOString(),
      service: 'playwright-mcp-server',
      clients: connectedClients.size
    }));
    return;
  }

  if (req.url === '/mcp') {
    const clientId = randomUUID();
    console.log(`🔌 새로운 MCP 연결 요청 (클라이언트: ${clientId})`);
    console.log('요청 메서드:', req.method);
    console.log('요청 헤더:', req.headers);
    
    try {
      // SSE 헤더 설정
      setupSSEHeaders(res);

      if (!createConnection) {
        throw new Error('Playwright MCP 모듈이 로드되지 않았습니다');
      }
      
      console.log('🎭 Playwright MCP 연결 생성 중...');
      
      // Playwright MCP 연결 생성
      const mcpServer = await createMCPServer();
      console.log('✅ MCP 서버 생성됨');
      
      // 클라이언트 등록
      connectedClients.set(clientId, {
        res,
        mcpServer,
        connected: true,
        timestamp: new Date()
      });
      
      // MCP 표준 초기화 응답 전송
      sendMCPNotification(res, 'notifications/initialized', {});
      
      // 실제 MCP 서버와의 통신 설정
      if (SSEServerTransport && mcpServer.server) {
        try {
          // SSE 전송 생성 및 MCP 서버 연결
          const transport = new SSEServerTransport('/mcp', res);
          await mcpServer.server.connect(transport);
          console.log('✅ MCP 표준 연결 성공');
        } catch (error) {
          console.log('⚠️ MCP 표준 연결 실패, 기본 모드로 진행:', error.message);
          
          // 기본 도구 목록 전송
          try {
            const tools = mcpServer.server._toolHandlers || new Map();
            sendMCPNotification(res, 'tools/list', { 
              tools: Array.from(tools.keys()).map(name => ({
                name,
                description: `Playwright tool: ${name}`
              }))
            });
          } catch (toolError) {
            console.log('⚠️ 도구 목록 전송 실패:', toolError.message);
            // 빈 도구 목록 전송
            sendMCPNotification(res, 'tools/list', { tools: [] });
          }
        }
      } else {
        // 기본 도구 목록 전송
        sendMCPNotification(res, 'tools/list', { tools: [] });
      }
      
      // 연결 종료 처리
      req.on('close', () => {
        console.log(`🔌 클라이언트 연결 종료: ${clientId}`);
        connectedClients.delete(clientId);
      });
      
      console.log(`✅ MCP 연결 성공 (클라이언트: ${clientId})`);
      
    } catch (error) {
      console.error('❌ MCP 연결 실패:', error);
      console.error('오류 스택:', error.stack);
      
      if (!res.headersSent) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          error: 'MCP 연결 실패', 
          details: error.message,
          stack: error.stack
        }));
      } else {
        sendMCPError(res, null, {
          message: error.message,
          data: { stack: error.stack }
        });
      }
      
      // 실패한 클라이언트 정리
      if (connectedClients.has(clientId)) {
        connectedClients.delete(clientId);
      }
    }
    return;
  }

  // 기본 응답
  if (req.url === '/' || req.url === '/info') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'Enhanced Playwright MCP HTTP Server',
      version: '2.0.0',
      endpoints: {
        health: '/health',
        mcp: '/mcp',
        info: '/info'
      },
      config: playwrightConfig,
      stats: {
        connectedClients: connectedClients.size,
        uptime: process.uptime()
      }
    }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, HOST, () => {
  console.log(`🚀 Playwright MCP 서버 실행 중:`);
  console.log(`   HTTP: http://${HOST}:${PORT}`);
  console.log(`   MCP:  http://${HOST}:${PORT}/mcp`);
  console.log(`   Health: http://${HOST}:${PORT}/health`);
});

// 우아한 종료 처리
process.on('SIGINT', () => {
  console.log('\n🛑 서버 종료 중...');
  server.close(() => {
    console.log('✅ 서버 종료 완료');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 서버 종료 중...');
  server.close(() => {
    console.log('✅ 서버 종료 완료');
    process.exit(0);
  });
});