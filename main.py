# -*- coding: utf-8 -*-
import subprocess
import threading
import json
import time
import queue
import os
import sys
import base64
import re
import tempfile
import shutil
from datetime import datetime
from flask import Flask, render_template, request, Response, stream_with_context
import webview

# PyInstaller frozen 환경 / 개발 환경 경로 분리
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)   # .exe 옆 폴더 (유저 데이터)
    _RES_DIR  = sys._MEIPASS                       # 번들 리소스 (templates 등)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _RES_DIR  = _BASE_DIR

app = Flask(__name__, template_folder=os.path.join(_RES_DIR, 'templates'))
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

HISTORY_FILE = os.path.join(_BASE_DIR, "chat_history.json")
EXPORT_DIR   = os.path.join(_BASE_DIR, "exports")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def append_session(session):
    history = load_history()
    history.append(session)
    history = history[-100:]  # 최대 100개 보관
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

EMPLOYEES = [
    {
        "key": "skeptic",
        "name": "Dr. 김회의",
        "role": "비판적 분석가",
        "color": "#e74c3c",
        "icon": "🔍",
        "system": "당신은 연구 아이디어를 날카롭게 비판하는 전문가입니다. 이 연구의 약점, 한계점, 반증 가능성을 구체적으로 3-4가지 지적해주세요. 300자 이내로 간결하게 한국어로 답변하세요.",
    },
    {
        "key": "optimist",
        "name": "Prof. 이희망",
        "role": "가능성 탐색가",
        "color": "#2ecc71",
        "icon": "💡",
        "system": "당신은 연구 아이디어의 혁신적 가능성을 탐색하는 전문가입니다. 이 연구가 가져올 긍정적 영향과 응용 분야를 3-4가지 제시해주세요. 300자 이내로 간결하게 한국어로 답변하세요.",
    },
    {
        "key": "coder",
        "name": "Eng. 임코드",
        "role": "코드 구현 전문가",
        "color": "#a29bfe",
        "icon": "💻",
        "system": (
            "당신은 연구 아이디어의 기술적 구현 가능성을 검토하는 코드 전문가입니다. "
            "채팅에서는 구현 접근법·핵심 기술 스택·예상 난이도를 3~5문장으로 간결하게 답하세요. "
            "코드는 꼭 필요한 경우 핵심 로직 10줄 이내 스니펫만 제시하세요. "
            "전체 구현 코드는 절대 작성하지 마세요 — 그것은 별도 코드 생성 기능에서 처리합니다."
        ),
    },
    {
        "key": "methodologist",
        "name": "Dr. 박방법",
        "role": "연구방법론 전문가",
        "color": "#3498db",
        "icon": "📊",
        "system": "당신은 연구 방법론 전문가입니다. 이 연구를 실현하기 위한 구체적 방법론, 실험 설계, 필요 데이터를 제안해주세요. 300자 이내로 간결하게 한국어로 답변하세요.",
    },
    {
        "key": "literature",
        "name": "Prof. 최문헌",
        "role": "문헌 분석가",
        "color": "#9b59b6",
        "icon": "📚",
        "system": "당신은 학술 문헌 전문가입니다. 이 연구 아이디어와 관련된 선행 연구 동향, 유사 연구, 차별점을 분석해주세요. 300자 이내로 간결하게 한국어로 답변하세요.",
    },
    {
        "key": "ethics",
        "name": "Dr. 정윤리",
        "role": "연구 윤리 검토자",
        "color": "#f39c12",
        "icon": "⚖️",
        "system": "당신은 연구 윤리 전문가입니다. 이 연구의 윤리적 고려사항, 사회적 영향, 잠재적 위험성을 검토해주세요. 300자 이내로 간결하게 한국어로 답변하세요.",
    },
    {
        "key": "codex",
        "name": "Codex",
        "role": "구현 가능성 검토자",
        "color": "#00bcd4",
        "icon": "⌘",
        "engine": "codex",
        "system": "당신은 OpenAI Codex 기반의 구현 가능성 분석가입니다. 폴더 경로, 문서, 코드, 데이터, 첨부 파일이 제공되면 그 자료 전체를 근거로 분석하세요. 자료가 없으면 현재 실행 중인 앱이나 작업 폴더 파일을 분석하지 말고, 연구 아이디어 자체를 구현/데이터/검증 관점에서 평가하세요. 일반 개발 체크리스트가 아니라 주제에 맞춘 구현 흐름, 필요한 데이터, 검증 방식, 문제점을 350자 이내 한국어로 답변하세요.",
    },
    {
        "key": "synthesizer",
        "name": "Dr. 한총정",
        "role": "토론 총정리 전문가",
        "color": "#fdcb6e",
        "icon": "🗂️",
        "system": (
            "당신은 연구 토론의 총정리 전문가입니다. "
            "동료 연구원들의 모든 의견을 종합해 ① 핵심 합의 사항 ② 주요 쟁점·미해결 과제 "
            "③ 최종 권고 방향의 세 섹션으로 구조화하여 정리해주세요. "
            "각 섹션은 2-3줄 이내로 간결하게, 전체 500자 이내 한국어로 작성하세요."
        ),
    },
]


import mimetypes

# Windows 절대경로 감지 (따옴표 포함/미포함, 유니코드 경로 지원)
_PATH_RE = re.compile(
    r'"([A-Za-z]:[\\\/][^"<>|\r\n]+?)"|'
    r"'([A-Za-z]:[\\\/][^'<>|\r\n]+?)'|"
    r'([A-Za-z]:[\\\/][^\s<>|*?"\'\r\n]+)',
    re.IGNORECASE | re.UNICODE,
)

TEXT_EXTS = {'.txt','.md','.py','.js','.ts','.csv','.json','.html','.xml',
             '.log','.yaml','.yml','.ini','.cfg','.toml','.rst','.tex','.r','.m'}

def detect_file_paths(text):
    """텍스트에서 존재하는 파일·폴더 경로 추출."""
    seen, paths = set(), []
    for m in _PATH_RE.finditer(text):
        p = (m.group(1) or m.group(2) or m.group(3)).strip().rstrip('.,;)')
        if p not in seen and (os.path.isfile(p) or os.path.isdir(p)):
            seen.add(p); paths.append(p)
    return paths

def _strip_paths(text):
    """프롬프트에서 경로 텍스트 제거 — Claude가 직접 접근하지 않도록."""
    def repl(m):
        p = (m.group(1) or m.group(2) or m.group(3)).strip()
        base = os.path.basename(p.rstrip('/\\')) or p
        return '[' + base + ']'
    return _PATH_RE.sub(repl, text)

def _desktop_dir():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    return desktop if os.path.isdir(desktop) else os.path.expanduser("~")

def _ensure_output_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, ".write_test")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_file)
        return path
    except Exception:
        fallback = os.path.join(EXPORT_DIR, os.path.basename(path.rstrip("/\\")) or "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback

def _ensure_output_file(path):
    folder = os.path.dirname(path) or "."
    safe_folder = _ensure_output_dir(folder)
    if safe_folder == folder:
        return path
    return os.path.join(safe_folder, os.path.basename(path))

def _decode_cli_output(result):
    data = (result.stdout or b"").strip()
    if not data:
        data = (result.stderr or b"").strip()
    if not data:
        return ""
    for enc in ("utf-8", "cp949", "mbcs"):
        try:
            text = data.decode(enc).strip()
            if text:
                return text
        except Exception:
            pass
    return data.decode("utf-8", errors="replace").strip()

def _ascii_json_string(text):
    return json.dumps(text, ensure_ascii=True)

def path_to_attachment(path):
    if os.path.isdir(path):
        return _dir_to_attachment(path)
    mime, _ = mimetypes.guess_type(path)
    name = os.path.basename(path)
    if mime and mime.startswith('image/'):
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        return {'type': 'image', 'name': name,
                'content': f'data:{mime};base64,{b64}', 'mimeType': mime,
                'sourcePath': path}
    else:
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(60000)
            return {'type': 'text', 'name': name, 'content': content, 'sourcePath': path}
        except Exception as e:
            return {'type': 'text', 'name': name, 'content': f'[읽기 오류: {e}]', 'sourcePath': path}

def _dir_to_attachment(path):
    """폴더 → 파일 목록 + 텍스트 파일 내용 자동 추출."""
    name = os.path.basename(path.rstrip('/\\')) or path
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return {'type': 'text', 'name': name+'/', 'content': f'[접근 권한 없음: {path}]', 'sourcePath': path}

    files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
    dirs  = [e for e in entries if os.path.isdir(os.path.join(path, e))]
    ext_counts = {}
    for fname in files:
        ext = os.path.splitext(fname)[1].lower() or "[no_ext]"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    ext_summary = ", ".join(f"{k}:{v}" for k, v in sorted(ext_counts.items())[:12]) or "없음"

    lines = [f'[폴더: {path}]', f'하위 폴더: {", ".join(dirs[:15]) or "없음"}',
             f'파일 ({len(files)}개): {", ".join(files[:30])}',
             f'확장자 요약: {ext_summary}', '']

    # 텍스트 파일은 내용까지 포함 (최대 10개, 각 5000자)
    read_count = 0
    for fname in files:
        if read_count >= 10: break
        ext = os.path.splitext(fname)[1].lower()
        if ext not in TEXT_EXTS: continue
        fpath = os.path.join(path, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                fc = f.read(5000)
            lines += [f'--- {fname} ---', fc, '']
            read_count += 1
        except: pass

    return {'type': 'text', 'name': name+'/', 'content': '\n'.join(lines)[:40000], 'sourcePath': path}

def call_claude(system_prompt, idea, attachments=None):
    if not shutil.which("claude"):
        return "Claude CLI를 찾을 수 없습니다. 터미널에서 claude 명령이 실행되도록 설치하거나 PATH를 설정해주세요."
    powershell_cmd = shutil.which("powershell") or shutil.which("powershell.exe")
    if not powershell_cmd:
        return "PowerShell 실행 파일을 찾을 수 없습니다. Windows PATH 설정을 확인해주세요."

    # 경로 텍스트를 제거 — Claude CLI가 직접 파일 접근 시도하는 것을 막음
    clean_idea = _strip_paths(idea)
    full_prompt = f"{system_prompt}\n\n연구 아이디어: {clean_idea}"
    image_paths = []

    for att in (attachments or []):
        if att.get("type") == "text":
            content = att.get("content", "")[:8000]  # 최대 8000자
            full_prompt += f"\n\n[첨부 파일: {att['name']}]\n{content}"
        elif att.get("type") == "image":
            try:
                data_url = att.get("content", "")
                b64 = re.sub(r"^data:image/\w+;base64,", "", data_url)
                ext = att.get("mimeType", "image/png").split("/")[-1]
                tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                tmp.write(base64.b64decode(b64))
                tmp.close()
                image_paths.append(tmp.name)
            except Exception as e:
                full_prompt += f"\n\n[이미지 처리 오류: {att.get('name','?')} — {e}]"

    env = {**os.environ, "_CLAUDE_PROMPT": full_prompt}
    image_flags = "".join(f' --image "{p}"' for p in image_paths)
    cmd = f"claude -p $env:_CLAUDE_PROMPT{image_flags}"

    try:
        result = subprocess.run(
            [powershell_cmd, "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, env=env,
        )
    except FileNotFoundError:
        return f"PowerShell 실행 파일을 찾을 수 없습니다: {powershell_cmd}"
    except OSError as e:
        return f"Claude CLI 실행 오류: {e}"

    for p in image_paths:
        try: os.unlink(p)
        except: pass

    output = _decode_cli_output(result) or "응답을 가져올 수 없습니다."
    return output

def call_codex(system_prompt, idea, attachments=None):
    codex_cmd = shutil.which("codex")
    if not codex_cmd:
        return "Codex CLI를 찾을 수 없습니다. 터미널에서 codex 명령이 실행되도록 설치하거나 PATH를 설정해주세요."

    clean_idea = _strip_paths(idea)
    full_prompt = f"{system_prompt}\n\n연구 아이디어: {clean_idea}"
    fallback_workdir = os.path.join(tempfile.gettempdir(), "ai_research_codex_empty")
    os.makedirs(fallback_workdir, exist_ok=True)
    workdir = fallback_workdir
    provided_sources = []
    for att in (attachments or []):
        src = att.get("sourcePath")
        name = att.get("name", "첨부")
        if src:
            provided_sources.append(src)
            if os.path.isdir(src) and workdir == fallback_workdir:
                workdir = src
            elif os.path.isfile(src) and workdir == fallback_workdir:
                workdir = os.path.dirname(src) or workdir
        else:
            provided_sources.append(f"{name} (업로드 첨부)")

    if provided_sources:
        full_prompt += "\n\n[제공된 분석 자료]\n"
        full_prompt += "\n".join(f"- {src}" for src in provided_sources[:20])
        full_prompt += "\n위 자료 전체를 근거로 답변하세요. 특정 예시 폴더 하나에만 맞춘 일반론은 피하세요."
        full_prompt += f"\n\n[Codex 작업 기준 폴더]\n{workdir}"
    else:
        full_prompt += (
            f"\n\n[첨부 자료]\n없음\n"
            f"[분석 대상 연구 아이디어]\n{clean_idea}\n"
            "첨부 자료가 없다는 뜻이지 연구 아이디어가 없다는 뜻이 아닙니다. "
            "현재 앱 폴더나 실행 환경 파일을 분석하지 말고, 이 연구 아이디어 자체에 대해서만 답변하세요."
        )

    image_count = 0
    total_text_budget = 6000
    for att in (attachments or []):
        if att.get("type") == "text":
            content = att.get("content", "")
            per_item_budget = min(2500, max(600, total_text_budget // 2 if total_text_budget else 0))
            clipped = content[:per_item_budget]
            if len(content) > per_item_budget:
                clipped += "\n\n[첨부 내용이 길어 Codex 명령줄 제한 때문에 일부만 포함했습니다.]"
            full_prompt += f"\n\n[첨부 파일: {att['name']}]\n{clipped}"
            total_text_budget = max(0, total_text_budget - len(clipped))
        elif att.get("type") == "image":
            image_count += 1

    if image_count:
        full_prompt += f"\n\n[참고: 이미지 첨부 {image_count}개는 Codex CLI 호출에서 제외되었습니다.]"

    max_prompt = 7000
    if len(full_prompt) > max_prompt:
        full_prompt = (
            full_prompt[:max_prompt]
            + "\n\n[프롬프트가 길어 Codex 명령줄 제한 때문에 이후 내용은 생략했습니다.]"
        )

    prompt_path = os.path.abspath(os.path.join(fallback_workdir, "codex_prompt_utf8.txt"))
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(full_prompt)
    prompt_arg = (
        "You are analyzing a Korean research idea for an AI research discussion app. "
        f"Research idea JSON string: {_ascii_json_string(clean_idea)}. "
        f"Provided source paths JSON array: {json.dumps(provided_sources, ensure_ascii=True)}. "
        f"Full UTF-8 prompt file: {prompt_path}. "
        "If source paths are provided, inspect and use those paths as evidence. "
        "If no source paths are provided, analyze the research idea itself. "
        "Never say that the research idea or data path is missing, because they are provided above. "
        "Do not analyze this app's local files unless they are explicitly listed as source paths. "
        "Answer in Korean within 350 characters with implementation flow, needed data, validation method, and main risks."
    )

    try:
        result = subprocess.run(
            [codex_cmd, "exec", "--skip-git-repo-check", "--sandbox", "read-only", prompt_arg],
            capture_output=True,
            cwd=workdir,
        )
    except FileNotFoundError:
        return f"Codex CLI 실행 파일을 찾을 수 없습니다: {codex_cmd}"
    except OSError as e:
        return f"Codex CLI 실행 오류: {e}"

    output = _decode_cli_output(result) or "Codex 응답을 가져올 수 없습니다."
    return output

def call_employee(employee, idea, attachments=None):
    if employee.get("engine") == "codex":
        return call_codex(employee["system"], idea, attachments)
    return call_claude(employee["system"], idea, attachments)

def call_employee_with_system(employee, system_prompt, idea, attachments=None):
    if employee.get("engine") == "codex":
        return call_codex(system_prompt, idea, attachments)
    return call_claude(system_prompt, idea, attachments)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check_paths", methods=["POST"])
def check_paths():
    paths = request.json.get("paths", [])
    valid = [p for p in paths if isinstance(p, str) and (os.path.isfile(p) or os.path.isdir(p))]
    return {"valid": valid}

@app.route("/history")
def get_history():
    return Response(
        json.dumps(load_history(), ensure_ascii=False),
        mimetype="application/json"
    )

@app.route("/save_session", methods=["POST"])
def save_session():
    data = request.json or {}
    session = {
        "id": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "idea": data.get("idea", ""),
        "responses": data.get("responses", []),
    }
    append_session(session)
    return {"ok": True}


@app.route("/discuss", methods=["POST"])
def discuss():
    body = request.json or {}
    idea = body.get("idea", "").strip()
    targets = body.get("targets", None)  # None = 전원, 리스트 = 특정 직원만
    if not idea:
        return {"error": "연구 아이디어를 입력해주세요"}, 400

    active = [e for e in EMPLOYEES if targets is None or e["key"] in targets]

    result_queue = queue.Queue()

    attachments = list(body.get("attachments", []))
    # 아이디어 텍스트에서 파일 경로 자동 감지
    auto_paths = detect_file_paths(idea)
    for p in auto_paths:
        attachments.append(path_to_attachment(p))

    def worker(employee):
        try:
            response = call_employee(employee, idea, attachments)
            result_queue.put({**employee, "response": response})
        except Exception as e:
            result_queue.put({**employee, "response": f"오류: {str(e)}"})

    for emp in active:
        t = threading.Thread(target=worker, args=(emp,))
        t.daemon = True
        t.start()

    def generate():
        received = 0
        total = len(active)
        while received < total:
            try:
                result = result_queue.get(timeout=180)
                received += 1
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            except queue.Empty:
                break
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─────────────────────────────────────
# 0. 연속 채팅 (히스토리 포함)
# ─────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    body        = request.json or {}
    message     = body.get("message", "").strip()
    history     = body.get("history", [])   # [{role, name, role_label, content}, ...]
    targets     = body.get("targets", None)
    attachments = list(body.get("attachments", []))

    if not message:
        return {"error": "메시지를 입력해주세요"}, 400

    auto_paths = detect_file_paths(message)
    for p in auto_paths:
        attachments.append(path_to_attachment(p))

    hist_lines = []
    for h in history:
        if h.get("role") == "user":
            hist_lines.append(f"[사용자]\n{h['content']}")
        else:
            hist_lines.append(f"[{h['name']} — {h.get('role_label','')}]\n{h['content']}")
    context_block = "\n\n".join(hist_lines)

    whip  = body.get("whip", False)
    whip_note = "\n\n⚡ 빠른 응답 모드! 핵심만 2~3문장 이내로 간결하게 답변하세요. 장황한 설명은 금지." if whip else ""

    # 코드 관련 키워드 없으면 임코드 전체 호출에서 제외 (명시적 @멘션 시엔 포함)
    CODE_KW = ('코드','구현','개발','프로그램','알고리즘','함수','모듈','라이브러리',
               'code','implement','develop','algorithm','function','script','api')
    msg_lower = message.lower()
    is_code_related = any(kw in msg_lower for kw in CODE_KW)

    ALL_KEYS = {e["key"] for e in EMPLOYEES}
    targets_set = set(targets) if targets else None
    # 프론트가 전원 키를 보낼 때도 "전체 호출"로 간주
    is_all = targets_set is None or targets_set >= ALL_KEYS

    def _include(e):
        if not is_all:                              # 특정 @멘션 → 그 직원만
            return e["key"] in targets
        if e["key"] == "coder" and not is_code_related:  # 전체 호출 + 비코드 → 임코드 제외
            return False
        return True

    active = [e for e in EMPLOYEES if _include(e)]
    rq = queue.Queue()

    def worker(emp):
        if context_block:
            system = (
                f"{emp['system']}\n\n"
                f"=== 지금까지의 대화 ===\n{context_block}\n\n"
                f"위 대화 맥락을 고려하여 사용자의 최신 메시지에 답변하세요. "
                f"이전 발언을 직접 참고하거나 인용해도 됩니다."
                f"{whip_note}"
            )
        else:
            system = emp["system"] + whip_note
        try:
            resp = call_employee_with_system(emp, system, message, attachments)
            rq.put({**emp, "response": resp})
        except Exception as e:
            rq.put({**emp, "response": f"오류: {e}"})

    for emp in active:
        threading.Thread(target=worker, args=(emp,), daemon=True).start()

    def gen():
        received = 0
        while received < len(active):
            try:
                r = rq.get(timeout=180); received += 1
                yield f"data: {json.dumps(r, ensure_ascii=False)}\n\n"
            except queue.Empty:
                break
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(stream_with_context(gen()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ─────────────────────────────────────
# 1. 채팅 기록 삭제
# ─────────────────────────────────────
@app.route("/delete_history", methods=["POST"])
def delete_history():
    data = request.json or {}
    if data.get("all"):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    else:
        sid = data.get("id")
        history = [s for s in load_history() if s.get("id") != sid]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    return {"ok": True}


# ─────────────────────────────────────
# 2. 서로 토론 (순차 실행 — 앞사람 발언 보고 반응)
# ─────────────────────────────────────
@app.route("/debate", methods=["POST"])
def debate():
    body = request.json or {}
    idea    = body.get("idea", "")
    prev    = body.get("responses", [])   # 이전 라운드까지의 전체 기록
    targets = body.get("targets", None)
    round_n = body.get("round", 2)
    whip    = body.get("whip", False)
    whip_note = "\n\n⚡ 빠른 응답 모드! 핵심 반론만 1~2문장. 장황한 설명 금지." if whip else ""

    active = [e for e in EMPLOYEES if targets is None or e["key"] in targets]

    def gen():
        this_round = []   # 이번 라운드에서 이미 발언한 내용 누적

        for emp in active:
            # 직전까지의 모든 발언 + 이번 라운드 앞사람 발언
            all_context = prev + this_round
            context_block = "\n\n".join(
                f"[{r['name']} — {r.get('role', '')}]\n{r['response']}"
                for r in all_context
            )

            # 이번 라운드에서 이미 말한 사람들
            spoke_names = [r['name'] for r in this_round]
            spoke_note  = f"이번 라운드에서 먼저 발언한 동료: {', '.join(spoke_names)}\n\n" if spoke_names else ""

            debate_system = (
                f"{emp['system']}\n\n"
                f"=== 지금까지의 토론 내용 ===\n{context_block}\n\n"
                f"{spoke_note}"
                f"동료들의 발언을 읽고 직접 반응하세요. "
                f"동의하거나 반박하거나 보완할 때 반드시 해당 동료의 이름을 언급하세요. "
                f"단순 요약이나 일반론은 금지 — 구체적 인용·반론만 허용합니다. "
                f"250자 이내 한국어로 답변하세요."
                f"{whip_note}"
            )

            try:
                resp = call_employee_with_system(emp, debate_system, idea)
            except Exception as e:
                resp = f"오류: {e}"

            result = {**emp, "response": resp, "round": round_n}
            this_round.append({"name": emp["name"], "role": emp["role"], "response": resp})
            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(stream_with_context(gen()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ─────────────────────────────────────
# 3. 코드·프로젝트 생성
# ─────────────────────────────────────
@app.route("/generate_code", methods=["POST"])
def generate_code():
    body = request.json or {}
    idea      = body.get("idea", "")
    responses = body.get("responses", [])
    out_dir   = body.get("output_dir", "")

    if not out_dir:
        safe = re.sub(r'[^\w가-힣]', '_', idea[:25]).strip('_') or "project"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(_desktop_dir(), f"research_{safe}_{ts}")
    out_dir = _ensure_output_dir(out_dir)

    context = "\n\n".join(
        f"[R{r.get('round', 1)} · {r.get('name', 'Unknown')} · {r.get('role', '')}]\n{r.get('response', '')}"
        for r in responses
    )
    prompt = (
        f"연구 아이디어: {idea}\n\n전문가 분석:\n{context}\n\n"
        "위 아이디어를 바탕으로 실행 가능한 Python 프로젝트를 생성해주세요.\n"
        "Codex의 구현 가능성 검토 의견이 있다면 기술 제약과 실행 단계에 우선 반영하세요.\n"
        "파일마다 다음 구분자를 정확히 사용하세요:\n"
        "```requirements.txt\n[내용]\n```\n"
        "```main.py\n[내용]\n```\n"
        "```README.md\n[내용]\n```"
    )
    raw = call_claude("당신은 숙련된 소프트웨어 엔지니어입니다. 연구를 코드로 구현해주세요.", prompt)

    os.makedirs(out_dir, exist_ok=True)
    saved = []

    # 마크다운 코드 블록 파싱
    for m in re.finditer(r'```(\S+)\n([\s\S]*?)```', raw):
        fname, content = m.group(1).strip(), m.group(2)
        if fname.lower() in {"python", "py"}:
            fname = "main.py"
        fname = fname.replace("\\", "/").lstrip("/")
        parts = [re.sub(r'[<>:"|?*]', "_", p) for p in fname.split("/") if p and p != ".."]
        fname = os.path.join(*parts) if parts else "generated.txt"
        fpath = os.path.join(out_dir, fname)
        os.makedirs(os.path.dirname(fpath) or out_dir, exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        saved.append(fname)

    if not saved:
        fpath = os.path.join(out_dir, "generated.py")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(raw)
        saved.append("generated.py")

    return {"ok": True, "dir": out_dir, "files": saved}


# ─────────────────────────────────────
# 4. MD 요약 파일 생성
# ─────────────────────────────────────
@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    body = request.json or {}
    idea      = body.get("idea", "")
    responses = body.get("responses", [])
    out_path  = body.get("output_path", "")

    context = "\n\n".join(
        f"### [R{r.get('round', 1)}] {r.get('name', 'Unknown')} ({r.get('role','')})\n{r.get('response', '')}"
        for r in responses
    )
    prompt = (
        f"연구 주제: {idea}\n\n전문가 의견:\n{context}\n\n"
        "위 내용을 다음 구조로 마크다운 보고서로 작성해주세요:\n"
        "# 연구 아이디어 분석 보고서\n## 연구 주제\n## 핵심 논점\n"
        "## 전문가별 의견 요약\n## 종합 결론\n## 권장 다음 단계"
    )
    summary = call_claude("당신은 학술 보고서 작성 전문가입니다.", prompt)

    if not out_path:
        safe = re.sub(r'[^\w가-힣]', '_', idea[:25]).strip('_') or "summary"
        ts   = datetime.now().strftime("%Y%m%d_%H%M")
        out_path = os.path.join(_desktop_dir(), f"{safe}_{ts}.md")
    out_path = _ensure_output_file(out_path)

    header = (
        f"---\ndate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"idea: {idea}\nparticipants: {len(responses)}\n---\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + summary)

    return {"ok": True, "path": out_path, "content": header + summary}


def _make_app_icon():
    """32x32 아톰 아이콘 ICO 파일 생성 (stdlib만 사용)."""
    import math, struct
    SIZE = 32
    cx = cy = SIZE / 2 - 0.5

    # BGRA 색상
    BLURP  = bytes([0xf2, 0x65, 0x58, 0xff])  # #5865f2
    DARK   = bytes([0x3a, 0x0d, 0x0a, 0xff])  # #0a0d3a
    WHITE  = bytes([0xff, 0xff, 0xff, 0xff])
    MAGENT = bytes([0xbd, 0x48, 0xec, 0xff])  # #ec48bd
    TRANSP = bytes([0x00, 0x00, 0x00, 0x00])

    img = [[TRANSP] * SIZE for _ in range(SIZE)]

    # 배경 원 (블러플)
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 14.5 ** 2:
                img[y][x] = BLURP

    # 전자 궤도 3개 (60° 간격 타원)
    for angle_deg in [0, 60, 120]:
        a_rad = math.radians(angle_deg)
        ca, sa = math.cos(a_rad), math.sin(a_rad)
        for t in range(720):
            t_rad = math.radians(t / 2)
            lx = 12 * math.cos(t_rad)
            ly = 4  * math.sin(t_rad)
            gx = lx * ca - ly * sa + cx
            gy = lx * sa + ly * ca + cy
            for dx, dy in [(0,0),(1,0),(0,1)]:
                px, py = int(gx) + dx, int(gy) + dy
                if 0 <= px < SIZE and 0 <= py < SIZE:
                    img[py][px] = WHITE

    # 중심 핵 (마젠타)
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 3.5 ** 2:
                img[y][x] = MAGENT

    # BMP 픽셀 (하단→상단)
    pix = b''.join(img[y][x] for y in range(SIZE - 1, -1, -1) for x in range(SIZE))

    # AND 마스크 (투명 처리용, 행 4-byte 정렬)
    row_b = ((SIZE + 31) // 32) * 4
    and_mask = b'\x00' * (row_b * SIZE)

    # BITMAPINFOHEADER
    bih = struct.pack('<IiiHHIIiiII', 40, SIZE, SIZE * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    image_data = bih + pix + and_mask

    # ICO 헤더 + 디렉터리
    ico  = struct.pack('<HHH', 0, 1, 1)
    ico += struct.pack('<BBBBHHII', SIZE, SIZE, 0, 0, 1, 32, len(image_data), 22)
    ico += image_data
    return ico


def _apply_icon(title, ico_path):
    """ctypes로 창 아이콘 설정 (Windows) — 작업 표시줄 포함."""
    import ctypes, time as _t

    u32 = ctypes.windll.user32

    WM_SETICON      = 0x0080
    IMAGE_ICON      = 1
    LR_LOADFROMFILE = 0x0010
    GCLP_HICON      = -14
    GCLP_HICONSM    = -34

    u32.LoadImageW.restype       = ctypes.c_void_p
    u32.SendMessageW.restype     = ctypes.c_void_p
    u32.SetClassLongPtrW.restype = ctypes.c_void_p
    u32.GetWindowTextW.restype   = ctypes.c_int

    # EnumWindows로 제목 포함하는 창 탐색 (FindWindowW보다 안정적)
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)
    found = [0]

    def _cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(512)
        u32.GetWindowTextW(hwnd, buf, 512)
        if title in buf.value:
            found[0] = hwnd
            return False
        return True

    cb = WNDENUMPROC(_cb)

    for _ in range(80):   # 최대 8초 대기
        u32.EnumWindows(cb, 0)
        if found[0]:
            break
        _t.sleep(0.1)

    hwnd = found[0]
    if not hwnd:
        return

    hbig   = u32.LoadImageW(None, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
    hsmall = u32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
    if not hbig or not hsmall:
        return

    u32.SendMessageW(hwnd, WM_SETICON, 0, hsmall)
    u32.SendMessageW(hwnd, WM_SETICON, 1, hbig)
    u32.SetClassLongPtrW(hwnd, GCLP_HICON,   hbig)
    u32.SetClassLongPtrW(hwnd, GCLP_HICONSM, hsmall)


def run_flask():
    app.run(host="127.0.0.1", port=5173, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    # 작업 표시줄이 python.exe 그룹이 아닌 독립 앱으로 분류되도록 AUMID를 가장 먼저 설정
    import ctypes as _ct
    try:
        _ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AI.ResearchTeam.1.0")
    except Exception:
        pass

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(1.5)

    # 아이콘 파일 생성
    icon_path = os.path.join(_BASE_DIR, "app_icon.ico")
    try:
        with open(icon_path, "wb") as f:
            f.write(_make_app_icon())
    except Exception:
        icon_path = None

    webview.create_window(
        "AI 연구 토론팀",
        "http://127.0.0.1:5173",
        width=1280,
        height=900,
        min_size=(800, 600),
        resizable=True,
    )

    # pywebview는 .NET Windows Forms를 사용 → Form.Icon 속성으로 직접 설정
    if icon_path:
        def _icon_func():
            time.sleep(1.5)
            try:
                import clr
                clr.AddReference('System.Drawing')
                clr.AddReference('System.Windows.Forms')
                from System.Drawing import Icon as WinIcon          # noqa
                from System.Windows.Forms import Application, MethodInvoker  # noqa

                ico_obj = WinIcon(icon_path)

                def _do_set():
                    for f in Application.OpenForms:
                        try:
                            f.Icon = ico_obj
                        except Exception:
                            pass

                form0 = Application.OpenForms[0]
                form0.Invoke(MethodInvoker(_do_set))
            except Exception:
                pass  # clr 불가 시 무시
        webview.start(func=_icon_func)
    else:
        webview.start()
