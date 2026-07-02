<div align="center">

# 🔬 AI Research Team

**8명의 AI 연구원이 당신의 아이디어를 함께 분석·토론해주는 데스크탑 앱**
<img width="1264" height="891" alt="image" src="https://github.com/user-attachments/assets/fcf0ef75-b2a7-4704-9d3b-afcafa4ff5d3" />

[![Release](https://img.shields.io/github/v/release/mecharover1234-sys/My-Own-AI-Company?style=flat-square&color=blueviolet)](https://github.com/mecharover1234-sys/My-Own-AI-Company/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://github.com/mecharover1234-sys/My-Own-AI-Company/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

[📥 다운로드](#-설치-방법) · [🚀 사용 방법](#-사용-방법) · [👥 연구원 소개](#-연구원-소개)

</div>

---

## ✨ 개요

**AI Research Team**은 Claude AI를 기반으로 한 데스크탑 연구 보조 앱입니다.
연구 아이디어나 질문을 입력하면, 각자 다른 관점을 가진 **8명의 가상 연구원**이 실시간으로 분석하고 토론합니다.

단순한 AI 챗봇이 아닌, 비판·낙관·윤리·방법론 등 **다양한 시각**으로 아이디어를 입체적으로 검토해주는 연구 파트너입니다.

---

## 👥 연구원 소개

| | 이름 | 역할 | 특징 |
|---|---|---|---|
| 🔍 | **Dr. 김회의** *(Dr. Doubt)* | 비판적 분석가 | 논리적 결함과 반례를 날카롭게 파고듭니다 |
| 💡 | **Prof. 이희망** *(Prof. Hope)* | 가능성 탐색가 | 아이디어의 잠재력과 긍정적 가능성을 탐색합니다 |
| 📊 | **Dr. 박방법** *(Dr. Method)* | 방법론 전문가 | 연구 설계와 검증 방법론을 구체화합니다 |
| 📚 | **Prof. 최문헌** *(Prof. Scholar)* | 문헌 분석가 | 관련 선행 연구와 이론적 배경을 연결합니다 |
| ⚖️ | **Dr. 정윤리** *(Dr. Ethics)* | 윤리 검토자 | 사회적·윤리적 영향을 신중하게 검토합니다 |
| ⌘ | **Codex** | 구현 가능성 검토자 | 기술적 실현 가능성과 구현 난이도를 평가합니다 |
| 🗂️ | **Dr. 한총정** *(Dr. Synopsis)* | 토론 총정리 전문가 | 모든 의견을 종합해 핵심 인사이트를 도출합니다 |
| 💻 | **Eng. 임코드** *(Eng. Coder)* | 코드 구현 전문가 | 아이디어를 실제 작동하는 코드로 구현합니다 |

---

## 🎯 주요 기능

### 💬 멀티 에이전트 채팅
아이디어를 입력하면 여러 연구원이 동시에 각자의 관점으로 응답합니다.
`@이름` 으로 특정 연구원만 호출할 수도 있습니다.

### 🔄 심층 토론 (Debate)
연구원들이 서로의 의견에 반론하며 라운드별 토론을 진행합니다.
아이디어의 약점과 강점이 자연스럽게 드러납니다.

### ⚙️ 코드 자동 생성
토론된 아이디어를 바탕으로 실제 동작하는 코드 프로젝트를 자동 생성합니다.
생성된 파일은 바탕화면에 폴더로 저장됩니다.

### 📝 MD 요약 저장
토론 내용 전체를 구조화된 마크다운 문서로 자동 요약·저장합니다.

### 🌐 한국어 / 영어 지원
UI 우측 상단의 `KO / EN` 버튼으로 언제든지 언어를 전환할 수 있습니다.
전환 시 연구원 이름과 역할명도 함께 바뀝니다.

### 🔴 채찍 모드 (Whip Mode)
AI 응답이 너무 느리다 싶을 때 사용하는 특별 기능입니다.
채찍 모드 ON → `Space` 를 누른 채 마우스를 빠르게 휘두르면 채찍 소리와 함께 연구원들을 재촉합니다.

---

## 📥 설치 방법

### 요구 사항

| 항목 | 내용 |
|---|---|
| OS | Windows 10 / 11 (64bit) |
| Claude CLI | 최신 버전 (필수) |
| WebView2 Runtime | Windows 11 기본 내장 / Windows 10은 자동 설치 |

### Step 1 — Claude CLI 설치 및 로그인

```
winget install Anthropic.Claude
```

또는 [https://claude.ai/download](https://claude.ai/download) 에서 직접 다운로드.

설치 후 터미널에서 로그인:

```
claude
```

> ⚠️ Claude 계정이 없으면 앱이 작동하지 않습니다. 반드시 로그인 후 실행하세요.

### Step 2 — 앱 다운로드

[**📥 최신 버전 다운로드**](https://github.com/mecharover1234-sys/My-Own-AI-Company/releases/latest)

`AI_Research_Team_Windows.zip` 을 다운로드 후 원하는 폴더에 압축 해제합니다.

### Step 3 — 실행

`AI_Research_Team.exe` 를 더블클릭하면 바로 실행됩니다.

---

## 🚀 사용 방법

### 기본 채팅

1. 하단 입력창에 연구 아이디어나 질문을 입력
2. `▶ 전송` 버튼 또는 `Ctrl + Enter` 로 전송
3. 연구원들이 순서대로 응답 — 픽셀 캐릭터가 책상으로 이동하며 타이핑 시작

### 특정 연구원만 호출

```
@김회의 이 실험 설계에 치명적인 결함이 있나요?
```

`@이름` 을 앞에 붙이면 해당 연구원만 응답합니다.

### 토론 시작

1. 채팅으로 기본 아이디어 공유
2. `💬 추가 토론` 버튼 클릭
3. 연구원들이 서로 반론하며 라운드별 심층 토론 진행

### 단축키

| 단축키 | 기능 |
|---|---|
| `Ctrl + Enter` | 메시지 전송 |
| `Space` (채찍 모드 ON 상태에서 마우스 이동) | 채찍질 |

---

## 🛠️ 직접 빌드

```bash
git clone https://github.com/mecharover1234-sys/My-Own-AI-Company
cd My-Own-AI-Company
pip install -r requirements.txt
pip install pyinstaller
build.bat
```

빌드 완료 후 `dist/AI_Research_Team/` 폴더에 실행 파일이 생성됩니다.

---

## 🔧 기술 스택

- **Backend** — Python, Flask
- **Frontend** — HTML / CSS / JavaScript (Canvas 픽셀 애니메이션)
- **Desktop** — PyWebView (Windows EdgeChromium)
- **AI** — Claude CLI (Anthropic)

---

## 📄 라이선스

MIT License © 2026
