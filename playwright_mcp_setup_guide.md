# Playwright MCP 설정 가이드 (Windows 환경)

## 문제점 분석

1. **@latest 버전 사용 문제**: Playwright MCP의 최신 버전이 Cursor에서 제대로 작동하지 않는 경우가 많음
2. **npx 경로 인식 문제**: Cursor가 npx 명령을 찾지 못하는 경우
3. **importAssertions 오류**: Node.js 환경과 MCP 패키지 문법 간 호환성 문제
4. **작업 디렉토리 설정 누락**: cwd 경로가 명시되지 않아 MCP 서버가 제대로 작동하지 않음
5. **Headless 모드 문제**: 브라우저 GUI가 나오지 않는 문제

## 해결책

### 1단계: 안정적인 버전 설치
```powershell
npm install -g @playwright/mcp@0.0.29
```

### 2단계: MCP 설정 파일 업데이트

**주 설정 (권장)**: `c:\Users\forza\.cursor\mcp.json`
```json
{
  "mcpServers": {
    "playwright": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": [
        "@playwright/mcp@0.0.29",
        "--headless=false",
        "--no-sandbox"
      ],
      "cwd": "C:\\jhryu\\llm_quality_radar",
      "env": {
        "NODE_OPTIONS": "--experimental-modules"
      }
    }
  }
}
```

**대안 설정**: `c:\Users\forza\.cursor\mcp_alternative.json`
```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": [
        "C:\\Users\\forza\\AppData\\Roaming\\npm\\node_modules\\@playwright\\mcp\\cli.js"
      ],
      "cwd": "C:\\jhryu\\llm_quality_radar"
    }
  }
}
```

### 3단계: 설정 검증
```powershell
# MCP 서버 실행 테스트
npx @playwright/mcp@0.0.29 --help

# 또는 직접 실행
node "C:\Users\forza\AppData\Roaming\npm\node_modules\@playwright\mcp\cli.js" --help
```

## 주요 설정 옵션 설명

- `--headless=false`: 브라우저 GUI 표시
- `--no-sandbox`: Windows 환경에서 샌드박스 비활성화
- `cwd`: MCP 서버의 작업 디렉토리 지정
- `env`: Node.js 환경 변수 설정

## 문제 해결

만약 첫 번째 설정이 작동하지 않는다면:
1. 대안 설정 파일을 사용
2. Cursor 재시작
3. MCP 연결 상태 확인

## 확인된 환경 정보

- Node.js: v20.17.0
- npm: 10.8.2
- npx 경로: C:\Program Files\nodejs\npx.cmd
- Playwright MCP: 0.0.29
- 설치 위치: C:\Users\forza\AppData\Roaming\npm\node_modules\@playwright\mcp\
