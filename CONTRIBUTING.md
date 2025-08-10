# 기여 가이드

LLM Quality Radar 프로젝트에 관심 가져주셔서 감사합니다.
이 문서는 이슈 등록, 기능 제안, 코드 기여 방법을 안내합니다.

## 이슈 등록
- 버그: 재현 단계, 기대 동작, 실제 동작, 로그/스크린샷을 포함해 주세요.
- 개선/기능 제안: 동기와 사용 시나리오를 구체적으로 작성해 주세요.

## 브랜치 전략
- 기본: `main`(안정), `develop`(개발).
- 기능: `feature/<short-name>`.
- 수정: `fix/<short-name>`.

## 코드 스타일
- Python: black, flake8, mypy.
- JavaScript: 기본 ESLint/Prettier 규칙(선택).

## 개발 준비
```bash
pip install -r requirements.txt
```

## 검사/테스트
```bash
black --check .
flake8 .
mypy apps/ core/ multi_tool_agent/ utils/ --ignore-missing-imports
pytest -q
```

## 커밋 메시지 권장 컨벤션
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
refactor: 리팩터링
test: 테스트 추가/변경
chore: 빌드/설정/잡무
```

## PR 가이드
- 작은 단위의 변경으로 PR을 열어 주세요.
- 목적, 변경 요약, 테스트 결과를 간단히 적어 주세요.

