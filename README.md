# 桌面 GUI 智能体（desktop_gui_agent）

基于多模态大模型的桌面 GUI 智能体原型系统。能够"看懂屏幕、操作电脑"，实现
「感知 → 思考 → 执行 → 反馈」的完整闭环。

> 本仓库对应《桌面 GUI 智能体开发需求文档(PRD)》v1.1。

## 当前进度

- 已完成开发环境搭建（API 在线模式）
- 已完成项目目录结构初始化（本次提交）
- API 连接已验证通过（见 `test_api.py`）

## 运行模式

本项目支持两种模型调用模式：

- **API 模式（当前主用）**：调用阿里云百炼（DashScope）的通义千问 VL 模型，
  无需本地 GPU。需在系统环境变量中配置 `DASHSCOPE_API_KEY`。
- **本地模式**：用 Transformers 加载 Qwen2-VL 在本机运行，需要足够显存。（待实现）

## 环境配置

```bash
# 1. 创建并激活虚拟环境
conda create -n gui_agent python=3.10 -y
conda activate gui_agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key（环境变量，切勿写入代码）
#    Windows：在「编辑系统环境变量」中新建 DASHSCOPE_API_KEY

# 4. 验证 API 连接
python test_api.py
```

## 目录结构

```
desktop_gui_agent/
├── README.md
├── requirements.txt
├── config.py              # 全局配置（不含密钥）
├── main.py                # 主入口 + 命令行界面 + 端到端流程
├── test_api.py            # API 连接验证脚本
├── perception/            # 感知模块（PRD 4.1）
│   ├── screenshot.py      # 屏幕截图
│   ├── ocr_recognizer.py  # OCR 文字识别
│   └── ui_locator.py      # UI 元素定位与可视化
├── control/               # 控制模块（PRD 4.2）
│   ├── mouse_controller.py
│   └── keyboard_controller.py
├── agent/                 # Agent 核心（PRD 4.3）
│   ├── model_client.py    # 多模态模型调用（API/本地）
│   ├── action_parser.py   # 系统提示词 + 动作解析
│   └── task_manager.py    # 任务状态管理
├── utils/                 # 工具
│   ├── logger.py          # 日志
│   └── exceptions.py      # 自定义异常
└── tests/                 # 单元测试（PRD 6.1）
    ├── test_perception.py
    ├── test_control.py
    └── test_agent.py
```

## 安全提醒

API Key（`sk-` 开头）等同账户钥匙，**绝不写入代码、绝不提交到仓库**，
一律通过系统环境变量 `DASHSCOPE_API_KEY` 读取。
