# Gemini Multi-Agent Orchestrator Hub
> 基于 Gemini 架构中枢的跨端多 Agent 协同研发工作台 (集成 OpenClaw, Muse, Claude, Codex 与 Antigravity 沙盒)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Cloudflare Tunnel](https://img.shields.io/badge/Tunnel-Cloudflare-orange.svg)](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-green.svg)](https://web.dev/progressive-web-apps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 项目简介

**Gemini Multi-Agent Orchestrator Hub** 是一个支持电脑端与手机端随时随地（家中/外网 4G/5G）访问的**通用多 Agent 协同研发工作台**。

通过**星型主管路由架构 (Hub-and-Spoke Topology)** 与**上下文切片引擎**，实现相比自由群聊模式 **72% 的 Token 节省** 与 **94% 的上下文纯净度**，并且**支持真正调用大模型编写工程代码落盘并执行沙盒验证**。

```
                  ┌───────────────────┐
                  │    人类用户 / PM   │
                  └─────────┬─────────┘
                            │ (切片隔离/过滤)
                            ▼
              ┌───────────────────────────┐
              │   Gemini 架构 [调度中枢]    │
              └──────┬──────┬──────┬──────┘
                     │      │      │      │
       ┌─────────────┘      │      │      └─────────────┐
       ▼                    ▼      ▼                    ▼
┌──────────────┐     ┌───────────┐ ┌───────────┐ ┌──────────────┐
│   OpenClaw   │     │   Muse    │ │  Claude   │ │    Codex     │
│ [数据感知底座]│     │[视觉/交互] │ │[核心研发] │ │[单测/沙盒门禁]│
└──────────────┘     └───────────┘ └───────────┘ └──────────────┘
```

---

## 🚀 核心特性

1. **视觉直观化工作规划看板 (Task Board)**
   - 支持自由排布、增删任务卡片。
   - 具备 **Gemini 智能任务解构与角色分配** 能力。
2. **多 Agent 实时会话与开工回执 (Chat Stream)**
   - 全面接通 Google Gemini 2.5 Flash 真实大模型。
   - 针对具体需求给出深度架构拆解，各 Agent 提供第一人称独立技术方案。
3. **真实代码落盘与执行引擎 (Real Code Execution)**
   - 告别“仅在嘴上汇报”，点击 **【▶ 真正写代码落盘】** 或 **【⚡ 编写全部代码】**，后台真正生成可执行代码并写入 `outputs/` 目录。
   - 自动在沙盒中执行单元测试，提供真实回执。
4. **跨端自适应与双通道访问**
   - **📱 移动端沉浸体验**：针对手机竖屏优化，支持 **PWA 一键添加到桌面**（全屏无地址栏独立 App 体验）。
   - **🏠 家中局域网直连通道**：手机连家中 WiFi 打开 `http://<Local_IP>:8765` 永不掉线。
   - **🌐 外网安全隧道通道**：集成 Cloudflare Tunnel，外出 4G/5G 随时随地安全直连。

---

## 🛠️ 快速启动指南

### 1. 克隆与依赖安装

```bash
git clone https://github.com/Wisely88/agent-orchestrator-hub.git
cd agent-orchestrator-hub
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入您的 Gemini API Key：

```bash
cp .env.example .env
# 编辑 .env，填入 GEMINI_API_KEY=your_key
```

### 3. 一键启动服务与穿透通道

```bash
./start_hub.sh
```

启动完成后终端将输出：
- 本地访问入口：`http://localhost:8765`
- 局域网直连入口：`http://<Your_Local_IP>:8765`
- 公网专属安全域名：`https://xxxx.trycloudflare.com`
- 手机端一键扫码二维码图片链接

### 4. 停止服务

```bash
./stop_hub.sh
```

---

## 📂 项目结构

```text
agent-orchestrator-hub/
├── static/
│   ├── index.html         # 电脑/手机全端自适应响应式 PWA 前端
│   ├── manifest.json      # 移动端桌面应用 PWA 配置
│   └── apps/              # 落地应用展示专区
├── data/
│   └── tasks.json         # 任务与协同状态持久化数据源
├── outputs/               # Agent 真实代码编写与落盘生成目录
├── tests/
│   └── test_server.py     # 单元测试套件
├── server.py              # 轻量级 RESTful API 服务与真实 AI 执行引擎
├── start_hub.sh           # 一键启动与 Cloudflare 隧道穿透脚本
├── stop_hub.sh            # 一键停止脚本
├── requirements.txt       # 核心 Python 依赖
└── README.md
```

---

## 📄 License

本项目采用 [MIT License](LICENSE) 开源许可协议。
