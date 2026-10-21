# Agent Orchestrator Hub

一个以真实执行状态为准的多 Agent 工作台。当前仓库只实现了有限的 API 适配器；界面中的角色名称不代表相应服务已经接通。

## 当前真实能力

- Gemini：在配置 `GEMINI_API_KEY` 且 API 调用成功时，可拆解需求。
- Claude：在配置 `ANTHROPIC_API_KEY` 后，可通过 Anthropic Messages API 生成任务产物。
- Codex、OpenClaw、Muse：目前没有可验证的执行适配器。被指派到这些角色的任务会明确显示“未配置”，不会伪装成已执行。
- 生成的产物会写入 `outputs/`，但服务**不会执行模型生成的代码，也不会声称测试通过**。
- 模型拆解失败时，不创建占位任务或虚假 Agent 回执。

## 安全边界

- 服务默认只监听 `127.0.0.1:8765`。
- 自动 Cloudflare 临时公网隧道已移除；不要将本服务直接暴露到公网。
- 当前版本没有完整的用户认证/授权层，因此不支持局域网或公网绑定。远程多设备访问应在实现认证、授权、审计日志与隔离执行环境后再启用。
- 前端动态内容会进行 HTML 转义；产物路径限制在 `outputs/` 目录内。
- 模型生成代码视为不可信内容，当前仅保存，不自动运行。

## 安装与启动

需要 Python 3.10+。在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，只填写你确实拥有的 API key
python server.py 8765
```

浏览器访问 `http://127.0.0.1:8765`。

可配置环境变量：

```dotenv
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-5
```

不要将真实密钥提交到 GitHub。若某个模型/接口不支持配置的模型 ID，服务会返回实际 API 错误，而不会伪造成功。

## 测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖默认数据、持久化、未配置 Agent 失败关闭，以及产物写入但不执行代码的行为。

## 仍未实现

- Codex CLI 的独立工作区执行、审批与 diff 审查
- OpenClaw Gateway 的受控适配器
- Muse 的具体产品/接口核验与适配器
- 多用户身份认证、权限、任务审计和远程访问
- 独立测试执行沙盒、资源配额、取消任务与返工流程

在上述能力完成并通过测试前，不应将本项目描述为已实现完整的多 Agent 自主协作平台。
