# AI Research Team

AI 연구원 페르소나들이 아이디어를 함께 분석·토론해주는 데스크탑 앱입니다.  
Claude CLI를 백엔드로 사용하며, 8명의 가상 연구원이 각자의 관점으로 응답합니다.

---

## 설치 방법

### 1. Claude CLI 설치 및 로그인

```bash
# Claude CLI 설치 (공식 사이트에서 다운로드)
# https://claude.ai/download

# 로그인
claude
```

> Claude 계정이 있어야 합니다. 앱 실행 전에 반드시 로그인하세요.

### 2. 앱 다운로드

[Releases](../../releases/latest) 페이지에서 `AI_Research_Team_Windows.zip` 다운로드 후 압축 해제.

### 3. 실행

`AI_Research_Team.exe` 더블클릭.

---

## 요구 사항

| 항목 | 버전 |
|---|---|
| OS | Windows 10 / 11 |
| Claude CLI | 최신 버전 |
| WebView2 Runtime | Windows 11 기본 포함 / Windows 10은 자동 설치 |

---

## 기능

- **채팅** — 연구 아이디어 입력 시 8명의 AI 연구원이 각자 응답
- **토론** — 연구원들이 서로 반론하며 심층 토론
- **코드 생성** — 아이디어를 코드로 구현
- **MD 요약** — 토론 내용을 마크다운으로 저장
- **언어 전환** — 한국어 / 영어 지원
- **채찍 모드** — 🔴 채찍 버튼 ON → 스페이스 누르고 마우스 휘두르기

---

## 직접 빌드

```bash
git clone https://github.com/YOUR_USERNAME/AI_Research_Team
cd AI_Research_Team
pip install -r requirements.txt
pip install pyinstaller
build.bat
```

---

## 라이선스

MIT
