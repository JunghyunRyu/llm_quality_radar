#!/usr/bin/env node
/**
 * 단순한 MCP 호환 HTTP 서버
 * Google ADK와 직접 호환되도록 설계
 */

import http from 'http';
import { randomUUID } from 'crypto';

const PORT = process.env.PORT || 8933;
const HOST = process.env.HOST || 'localhost';

console.log('🎭 단순한 MCP HTTP 서버 시작 중...');

// 가상의 Playwright 도구들 
const PLAYWRIGHT_TOOLS = [
  {
    name: 'browser_navigate',
    description: 'Navigate to a URL in the browser',
    inputSchema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'URL to navigate to' }
      },
      required: ['url']
    }
  },
  {
    name: 'page_screenshot',
    description: 'Take a screenshot of the current page',
    inputSchema: {
      type: 'object',
      properties: {
        fullPage: { type: 'boolean', description: 'Take full page screenshot' }
      }
    }
  },
  {
    name: 'element_click',
    description: 'Click on an element',
    inputSchema: {
      type: 'object',
      properties: {
        selector: { type: 'string', description: 'CSS selector of element to click' }
      },
      required: ['selector']
    }
  },
  {
    name: 'page_content',
    description: 'Get the text content of the page',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

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
      service: 'simple-mcp-server',
      tools: PLAYWRIGHT_TOOLS.length
    }));
    return;
  }

  if (req.url === '/tools') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      tools: PLAYWRIGHT_TOOLS
    }));
    return;
  }

  if (req.url === '/mcp-simple') {
    // SSE 없는 간단한 MCP 응답
    console.log('🔌 간단한 MCP 연결 요청');
    
    try {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'connected',
        protocol: 'mcp-simple',
        tools: PLAYWRIGHT_TOOLS,
        capabilities: ['tools'],
        server: {
          name: 'simple-playwright-mcp',
          version: '1.0.0'
        }
      }));
      
      console.log('✅ 간단한 MCP 연결 응답 전송 완료');
      
    } catch (error) {
      console.error('❌ 간단한 MCP 연결 실패:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ 
        error: 'MCP 연결 실패', 
        details: error.message
      }));
    }
    return;
  }

  if (req.url === '/mcp') {
    console.log('🔌 새로운 MCP 연결 요청');
    console.log('요청 헤더:', req.headers);
    
    try {
      // SSE 헤더 설정
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'X-Accel-Buffering': 'no'
      });

      // MCP 초기화 메시지 (JSON-RPC 형식)
      const initMessage = {
        jsonrpc: "2.0",
        method: "notifications/initialized",
        params: {}
      };
      res.write(`data: ${JSON.stringify(initMessage)}\n\n`);

      // 서버 정보 전송
      const serverInfo = {
        jsonrpc: "2.0",
        method: "server/info",
        params: {
          name: 'simple-playwright-mcp',
          version: '1.0.0',
          capabilities: ['tools'],
          tools: PLAYWRIGHT_TOOLS
        }
      };
      res.write(`data: ${JSON.stringify(serverInfo)}\n\n`);

      // 도구 목록 전송
      const toolsList = {
        jsonrpc: "2.0",
        method: "tools/list",
        params: {
          tools: PLAYWRIGHT_TOOLS
        }
      };
      res.write(`data: ${JSON.stringify(toolsList)}\n\n`);

      console.log('✅ MCP SSE 연결 설정 완료');

      // 연결 유지를 위한 heartbeat
      const heartbeatInterval = setInterval(() => {
        try {
          const heartbeat = {
            jsonrpc: "2.0",
            method: "heartbeat",
            params: { timestamp: new Date().toISOString() }
          };
          res.write(`data: ${JSON.stringify(heartbeat)}\n\n`);
        } catch (error) {
          console.log('⚠️ Heartbeat 전송 실패:', error.message);
          clearInterval(heartbeatInterval);
        }
      }, 30000); // 30초마다

      // 연결 종료 처리
      req.on('close', () => {
        console.log('🔌 클라이언트 연결 종료');
        clearInterval(heartbeatInterval);
      });

      req.on('error', (error) => {
        console.log('❌ 연결 오류:', error.message);
        clearInterval(heartbeatInterval);
      });
      
    } catch (error) {
      console.error('❌ MCP 연결 실패:', error);
      if (!res.headersSent) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          error: 'MCP 연결 실패', 
          details: error.message
        }));
      }
    }
    return;
  }

  // POST 요청 처리 (도구 실행)
  if (req.method === 'POST' && req.url === '/execute') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const request = JSON.parse(body);
        console.log('🛠️ 도구 실행 요청:', request);

        // 간단한 도구 실행 시뮬레이션
        const result = {
          tool: request.tool,
          status: 'success',
          result: `Executed ${request.tool} with params: ${JSON.stringify(request.params)}`,
          timestamp: new Date().toISOString()
        };

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));

      } catch (error) {
        console.error('❌ 도구 실행 실패:', error);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          error: '잘못된 요청', 
          details: error.message 
        }));
      }
    });
    return;
  }

  // 기본 응답
  if (req.url === '/' || req.url === '/info') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'Simple MCP HTTP Server',
      version: '1.0.0',
      description: 'Google ADK 호환 단순 MCP 서버',
      endpoints: {
        health: '/health',
        tools: '/tools',
        mcp: '/mcp',
        'mcp-simple': '/mcp-simple',
        execute: '/execute',
        info: '/info'
      },
      tools: PLAYWRIGHT_TOOLS.length
    }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, HOST, () => {
  console.log(`🚀 단순한 MCP 서버 실행 중:`);
  console.log(`   HTTP: http://${HOST}:${PORT}`);
  console.log(`   MCP (SSE): http://${HOST}:${PORT}/mcp`);
  console.log(`   MCP (Simple): http://${HOST}:${PORT}/mcp-simple`);
  console.log(`   Tools: http://${HOST}:${PORT}/tools`);
  console.log(`   Health: http://${HOST}:${PORT}/health`);
  console.log(`🛠️ 사용 가능한 도구: ${PLAYWRIGHT_TOOLS.length}개`);
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
