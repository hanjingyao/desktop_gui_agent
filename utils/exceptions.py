"""自定义异常定义。

集中定义各模块用到的异常类型，便于统一捕获与日志记录。
"""


class GUIAgentError(Exception):
    """项目所有自定义异常的基类。"""


class ScreenshotError(GUIAgentError):
    """截图失败、屏幕不存在或区域越界（PRD 4.1.1）。"""


class OCRError(GUIAgentError):
    """OCR 模型加载或识别失败（PRD 4.1.2）。"""


class ControlError(GUIAgentError):
    """鼠标/键盘操作失败、坐标越界、无效按键（PRD 4.2）。"""


class ModelError(GUIAgentError):
    """模型加载或调用失败（PRD 4.3.1）。"""


class ActionParseError(GUIAgentError):
    """动作指令解析失败（PRD 4.3.3）。"""
