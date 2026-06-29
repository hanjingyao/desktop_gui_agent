"""全局配置。

集中存放可调参数，避免散落在各模块中。
注意：这里不存放任何密钥（如 DASHSCOPE_API_KEY），密钥一律放系统环境变量。
"""

# ---------- 模型配置（PRD 4.3.1） ----------
MODEL_MODE = "api"              # 'api' 或 'local'
API_MODEL_NAME = "qwen3-vl-plus"  # API 模式使用的视觉模型

# ---------- 流程控制配置（PRD 4.4.1） ----------
MAX_STEPS = 10        # 单个任务最大执行步数
RETRY_COUNT = 3       # 单步最大重试次数

# ---------- 控制延迟配置（PRD 4.2） ----------
MOUSE_ACTION_DELAY = 0.1   # 鼠标操作后延迟（秒）
KEYBOARD_TYPE_DELAY = 0.05  # 键盘逐字输入延迟（秒）

# ---------- 日志配置（PRD 4.4.3） ----------
LOG_FILE = "gui_agent.log"
