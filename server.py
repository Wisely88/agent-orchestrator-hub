#!/usr/bin/env python3
"""
Agent Orchestrator Hub.
Only configured providers may execute; generated code is saved but never run.
The HTTP server binds to loopback until authenticated remote access is implemented.
"""

import os
import sys
import json
import mimetypes
import subprocess
import socket
import urllib.request
import urllib.error
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "tasks.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS_DIR, exist_ok=True)

# 优先加载本地 .env 文件
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.isfile(ENV_FILE):
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception as e:
        print(f"Error loading .env: {e}")

# 读取环境变量中的配置
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

genai_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ [AI Brain] Gemini API 客户端已配置")
    except Exception as e:
        print(f"⚠️ [AI Brain] Gemini 客户端初始化失败: {e}")
else:
    print("ℹ️ [AI Brain] 未配置 GEMINI_API_KEY；需求拆解将明确失败，不会伪造任务。

# 获取本机局域网 IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# 纯净清爽的通用工作台初始状态
DEFAULT_DATA = {
    "current_project": "多 Agent 协同研发通用中枢",
    "tasks": [],
    "messages": [
        {
            "id": "M1",
            "sender": "Gemini",
            "name": "Gemini 调度中枢",
            "text": "工作台已就绪。需求拆解由已配置的 Gemini API 完成；只有接通真实适配器的 Agent 才能执行。未配置会明确报错，生成代码不会自动运行。",
            "time": "System Ready"
        }
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return DEFAULT_DATA

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_real_gemini_brain(user_prompt):
    """调用真实 Gemini 2.5 Flash 进行深度任务拆解"""
    if not genai_client:
        return None

    system_instruction = f"""你是需求拆解与任务规划模型，不是其他 Agent 的代言人。
可以建议 OpenClaw、Muse、Claude、Codex 等角色，但规划不代表这些服务已连接。
不要伪造任何 Agent 的第一人称开工回执；系统只会记录真实适配器的执行结果。

人类用户发来了真实项目开发指令：
"{user_prompt}"

请你根据该具体指令，输出严格的 JSON（禁止包含 markdown 代码块包裹，纯 JSON 字符串）：
{{
  "gemini_analysis": "你作为架构师，针对该需求的架构分析、技术栈选型与切片规划",
  "tasks": [
    {{
      "title": "任务简短标题",
      "desc": "具体实施内容与技术交付物",
      "assignedAgent": "OpenClaw 或 Muse 或 Claude 或 Codex",
      "slice": "切片说明"
    }}
  ]
}}
注意：tasks 输出 2 到 4 个最核心的任务，职责分明，不要过度碎片化；不要生成 agent_acks 或其他 Agent 的开工回执。"""

    try:
        resp = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=system_instruction
        )
        text = resp.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ [AI Brain] Gemini API 异常: {e}")
        return None

class AgentNotConfiguredError(RuntimeError):
    """Raised when the requested Agent has no genuine execution adapter."""


def call_agent_for_code(agent, prompt):
    """Call only a configured provider. Never impersonate an unconnected Agent."""
    if agent == "Gemini":
        if not genai_client:
            raise AgentNotConfiguredError("Gemini 未配置：请设置 GEMINI_API_KEY。")
        response = genai_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        content = (getattr(response, "text", None) or "").strip()
        if not content:
            raise RuntimeError("Gemini 返回空内容。")
        return content, "Google Gemini API"

    if agent == "Claude":
        if not ANTHROPIC_API_KEY:
            raise AgentNotConfiguredError("Claude 未配置：请设置 ANTHROPIC_API_KEY。")
        payload = json.dumps({
            "model": ANTHROPIC_MODEL,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "content-type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Claude API HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Claude API 网络/超时错误：{exc}") from exc
        blocks = result.get("content", [])
        content = "\n".join(
            block.get("text", "") for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
        if not content:
            raise RuntimeError("Claude API 返回空内容。")
        return content, f"Anthropic API ({ANTHROPIC_MODEL})"

    configured = {
        "Codex": "Codex CLI/执行器尚未接入；不会用其他模型冒充 Codex。",
        "OpenClaw": "OpenClaw Gateway 尚未接入；不会伪造 OpenClaw 执行。",
        "Muse": "Muse 的可验证执行接口尚未配置；不会伪造 Muse 执行。"
    }
    raise AgentNotConfiguredError(configured.get(agent, f"未知或未配置的 Agent：{agent}"))


def execute_real_agent_task(task):
    """Generate an artifact using the specifically assigned, configured provider.
    Generated code is written as an artifact only and is never executed here.
    """
    agent = str(task.get("assignedAgent", "")).strip()
    title = str(task.get("title", ""))
    desc = str(task.get("desc", ""))
    task_id = str(task.get("id", "task"))
    if not agent:
        raise AgentNotConfiguredError("任务没有指派 Agent。")
    prompt = f"""你是执行任务的工程 Agent。
任务 ID：{task_id}
任务名称：{title}
任务需求：{desc}

只输出该任务的代码或配置文件内容，不要声称运行过测试或部署。
不要输出密钥、凭据或无关文件内容。"""
    content, provider = call_agent_for_code(agent, prompt)
    extensions = {"Claude": ".py", "Codex": ".py", "Muse": ".html",
                  "OpenClaw": ".json", "Gemini": ".txt"}
    extension = extensions.get(agent, ".txt")
    safe_id = "".join(ch for ch in task_id if ch.isalnum() or ch in "-_")[:40] or "task"
    safe_agent = "".join(ch for ch in agent.lower() if ch.isalnum() or ch in "-_")[:30] or "agent"
    output_filename = f"task_{safe_id}_{safe_agent}{extension}"
    output_root = os.path.abspath(OUTPUTS_DIR)
    file_path = os.path.abspath(os.path.join(output_root, output_filename))
    if os.path.commonpath([output_root, file_path]) != output_root:
        raise RuntimeError("非法产物路径。")
    os.makedirs(output_root, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as output_file:
        output_file.write(content)
    return {
        "file_name": output_filename,
        "file_path": file_path,
        "relative_path": f"/outputs/{output_filename}",
        "size": len(content.encode("utf-8")),
        "provider": provider,
        "execution_result": "未执行生成的代码",
        "test_result": "未运行测试；仅生成并保存产物"
    }


class HubRequestHandler(BaseHTTPRequestHandler):
    def send_json(self, status_code, data):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/data" or path == "/api/tasks":
            data = load_data()
            data["local_ip"] = "127.0.0.1"
            self.send_json(200, data)
            return

        if path == "/api/messages":
            data = load_data()
            self.send_json(200, {"messages": data.get("messages", [])})
            return

        # 访问生成的代码产物目录
        if path.startswith("/outputs/"):
            rel_file = path[len("/outputs/"):].lstrip("/")
            output_root = os.path.abspath(OUTPUTS_DIR)
            file_path = os.path.abspath(os.path.join(output_root, rel_file))
            if os.path.commonpath([output_root, file_path]) != output_root:
                self.send_error(403, "Forbidden")
                return
            if os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
                content_type = content_type or "text/plain; charset=utf-8"
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    if not head_only:
                        self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_error(500, str(e))
                    return

        if path == "/" or path == "/index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
        else:
            rel_path = path.lstrip("/")
            static_root = os.path.abspath(STATIC_DIR)
            file_path = os.path.abspath(os.path.join(static_root, rel_path))
            if os.path.commonpath([static_root, file_path]) != static_root:
                self.send_error(403, "Forbidden")
                return

        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                if not head_only:
                    self.wfile.write(content)
                return
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")
                return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            req_data = {}

        data = load_data()

        # 清空重置看板
        if path == "/api/tasks/reset":
            data["tasks"] = []
            msg = {
                "id": "M" + str(len(data.get("messages", [])) + 1),
                "sender": "Gemini",
                "name": "Gemini 调度中枢",
                "text": "🧹 看板与工作台已清空重置，欢迎输入您的任意真实工程开发需求！",
                "time": "刚刚"
            }
            data.setdefault("messages", []).append(msg)
            save_data(data)
            self.send_json(200, {"success": True, "tasks": [], "message": msg})
            return

        # 核心：真正调用 Agent 落地开发代码与单测！
        if path.startswith("/api/tasks/execute/"):
            task_id = path.split("/")[-1]
            target_task = next((task for task in data.get("tasks", []) if task.get("id") == task_id), None)
            if not target_task:
                self.send_json(404, {"success": False, "error": "Task Not Found"})
                return
            target_task["status"] = "执行中"
            target_task.pop("error", None)
            save_data(data)
            try:
                exec_res = execute_real_agent_task(target_task)
            except AgentNotConfiguredError as exc:
                target_task["status"] = "未配置"
                target_task["error"] = str(exc)
                save_data(data)
                self.send_json(409, {"success": False, "task": target_task, "error": str(exc)})
                return
            except Exception as exc:
                target_task["status"] = "失败"
                target_task["error"] = str(exc)
                save_data(data)
                self.send_json(502, {"success": False, "task": target_task, "error": str(exc)})
                return
            target_task["status"] = "✅ 已落盘；未执行代码"
            target_task["artifact"] = exec_res["relative_path"]
            target_task["file_name"] = exec_res["file_name"]
            target_task["provider"] = exec_res["provider"]
            target_task["test_result"] = exec_res["test_result"]
            report_msg = {
                "id": "M" + str(len(data.get("messages", [])) + 1),
                "sender": target_task.get("assignedAgent", "Agent"),
                "name": f"{target_task.get('assignedAgent', 'Agent')}（真实 API）",
                "text": f"产物已保存：outputs/{exec_res['file_name']}（{exec_res['size']} 字节）。调用方：{exec_res['provider']}。未执行生成代码，未运行测试。",
                "time": "刚刚"
            }
            data.setdefault("messages", []).append(report_msg)
            save_data(data)
            self.send_json(200, {"success": True, "task": target_task, "result": exec_res})
            return

        # 一键执行全部待办任务
        if path == "/api/tasks/execute_all":
            results = []
            failures = []
            for task in data.get("tasks", []):
                if "已落盘" in task.get("status", ""):
                    continue
                task["status"] = "执行中"
                task.pop("error", None)
                save_data(data)
                try:
                    result = execute_real_agent_task(task)
                    task["status"] = "✅ 已落盘；未执行代码"
                    task["artifact"] = result["relative_path"]
                    task["file_name"] = result["file_name"]
                    task["provider"] = result["provider"]
                    task["test_result"] = result["test_result"]
                    results.append(result)
                except AgentNotConfiguredError as exc:
                    task["status"] = "未配置"
                    task["error"] = str(exc)
                    failures.append({"task_id": task.get("id"), "error": str(exc)})
                except Exception as exc:
                    task["status"] = "失败"
                    task["error"] = str(exc)
                    failures.append({"task_id": task.get("id"), "error": str(exc)})
                save_data(data)
            summary_msg = {
                "id": "M" + str(len(data.get("messages", [])) + 1),
                "sender": "System",
                "name": "执行结果汇总",
                "text": f"真实 API 产物生成 {len(results)} 项；失败或未配置 {len(failures)} 项。生成的代码未被执行，测试未运行。",
                "time": "刚刚"
            }
            data.setdefault("messages", []).append(summary_msg)
            save_data(data)
            self.send_json(200 if not failures else 207, {
                "success": len(failures) == 0,
                "tasks": data.get("tasks", []),
                "results": results,
                "failures": failures
            })
            return

        # 新增自定义任务
        if path == "/api/tasks":
            new_task = {
                "id": "T" + str(len(data.get("tasks", [])) + 1),
                "title": req_data.get("title", "未命名工作"),
                "desc": req_data.get("desc", ""),
                "assignedAgent": req_data.get("assignedAgent", "Claude"),
                "status": "已调度",
                "slice": req_data.get("slice", "自定义切片 (0.6k)")
            }
            data.setdefault("tasks", []).append(new_task)
            save_data(data)
            self.send_json(201, {"success": True, "task": new_task})
            return

        # 聊天指令发送与真实 AI 调度拆解
        if path == "/api/messages":
            text = req_data.get("text", "").strip()
            sender = req_data.get("sender", "user")
            name = req_data.get("name", "人类用户")

            if text:
                user_msg = {
                    "id": "M" + str(len(data.get("messages", [])) + 1),
                    "sender": sender,
                    "name": name,
                    "text": text,
                    "time": "刚刚"
                }
                data.setdefault("messages", []).append(user_msg)

                ai_result = call_real_gemini_brain(text)
                if not ai_result or "tasks" not in ai_result:
                    error_text = "需求拆解失败：Gemini API 未配置、调用失败或返回内容不是有效 JSON。未创建虚假任务；请检查 GEMINI_API_KEY、模型配置和服务日志。"
                    error_msg = {
                        "id": "M" + str(len(data.get("messages", [])) + 1),
                        "sender": "System",
                        "name": "执行错误",
                        "text": error_text,
                        "time": "刚刚"
                    }
                    data.setdefault("messages", []).append(error_msg)
                    save_data(data)
                    self.send_json(502, {"success": False, "error": error_text, "messages": [user_msg, error_msg]})
                    return

                analysis = ai_result.get("gemini_analysis", "需求意图已解构并分配完成。")
                raw_tasks = ai_result.get("tasks", [])
                agent_acks = ai_result.get("agent_acks", [])

                base_id = len(data.get("tasks", [])) + 1
                created_tasks = []
                for t in raw_tasks:
                    task_item = {
                        "id": f"T{base_id}",
                        "title": t.get("title", "子任务"),
                        "desc": t.get("desc", ""),
                        "assignedAgent": t.get("assignedAgent", "Claude"),
                        "status": "已调度",
                        "slice": t.get("slice", "按需切片 (0.8k)")
                    }
                    data.setdefault("tasks", []).append(task_item)
                    created_tasks.append(task_item)
                    base_id += 1

                gemini_reply = {
                    "id": "M" + str(len(data.get("messages", [])) + 1),
                    "sender": "Gemini",
                    "name": "Gemini 调度中枢",
                    "text": f"🧠 【架构调度决策】\n{analysis}\n\n已切片生成 {len(created_tasks)} 个研发主线排入看板：\n" + "\n".join([f"• [{t['id']}] {t['title']} ➔ 【{t['assignedAgent']}】 ({t['slice']})" for t in created_tasks]) + "\n\n提示：执行按钮只调用已配置的真实适配器；未配置会明确失败。产物保存后不会自动执行，测试也不会被虚报为通过。",
                    "time": "刚刚"
                }
                data.setdefault("messages", []).append(gemini_reply)

                # 只发布真实 Gemini 调度结果；不把第一人称生成文本冒充其他 Agent 回执。
                added_replies = [user_msg, gemini_reply]

                save_data(data)
                self.send_json(200, {"success": True, "messages": added_replies, "new_tasks": created_tasks})
                return

        self.send_error(400, "Bad Request")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/tasks/"):
            task_id = path.split("/")[-1]
            data = load_data()
            tasks = data.get("tasks", [])
            data["tasks"] = [t for t in tasks if t.get("id") != task_id]
            save_data(data)
            self.send_json(200, {"success": True, "deleted": task_id})
            return
        self.send_error(404, "Not Found")

def run(port=8765):
    # Remote/LAN exposure is disabled until an authenticated access layer exists.
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, HubRequestHandler)
    print(f"🚀 [Hub Server] Listening locally at http://127.0.0.1:{port}")
    print("🔒 远程访问已禁用：请勿通过公网隧道暴露此服务。"
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Hub Server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run(port)
