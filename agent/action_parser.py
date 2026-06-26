"""动作解析功能 + 系统提示词模板。

对应 PRD 4.3.2（系统提示词）与 PRD 4.3.3（动作解析）。

职责：
    1. 提供引导模型输出规范动作指令的系统提示词。
    2. 把模型输出的文本（形如 "Action: click(x=100, y=200)"）
       解析为可执行的动作字典 {"action_type": ..., "params": {...}}。
"""

import re


# 系统提示词（PRD 4.3.2）。会与用户指令拼接后发给模型。
SYSTEM_PROMPT = """你是一个桌面 GUI 操作智能体，请根据当前屏幕截图和用户指令，生成下一步要执行的动作。
请严格按照以下格式输出你的回答，不要添加任何额外内容：

Action: 动作类型(参数)

支持的动作类型及参数：
1. click(x=<横坐标>, y=<纵坐标>) - 点击指定坐标
2. type(text="<输入文本>") - 输入指定文本
3. scroll(direction="<up/down>", steps=<步数>) - 滚动屏幕
4. hotkey(key1="<按键1>", key2="<按键2>", ...) - 按下组合键
5. finish(result="<结果描述>") - 任务完成，返回结果

注意事项：
- 每次只输出一个动作
- 坐标必须是整数
- 文本内容用双引号括起来
- 如果任务已经完成，使用 finish 动作
"""

# 支持的动作类型白名单
SUPPORTED_ACTIONS = {"click", "type", "scroll", "hotkey", "finish"}


def build_prompt(user_instruction: str) -> str:
    """把系统提示词与用户指令拼接成完整 prompt。"""
    return f"{SYSTEM_PROMPT}\n\n用户指令：{user_instruction}"


def parse_action(model_output: str) -> dict | None:
    """解析模型输出的动作指令。

    Args:
        model_output: 模型生成的文本，形如 'Action: click(x=100, y=200)'。

    Returns:
        动作字典 {"action_type": str, "params": dict}；
        解析失败或动作类型不支持时返回 None。

    业务逻辑（PRD 4.3.3）：
        1. 用正则匹配动作类型与参数。
        2. 验证参数合法性与完整性。
        3. 转换参数类型（如字符串转整数）。
    """
    if not model_output:
        return None

    # 匹配 "Action: 动作类型(参数...)"
    match = re.search(r"Action:\s*(\w+)\((.*)\)", model_output, re.DOTALL)
    if not match:
        return None

    action_type = match.group(1)
    if action_type not in SUPPORTED_ACTIONS:
        return None

    # TODO: 解析括号内参数为字典，并做类型转换与合法性校验
    params: dict = {}
    raise NotImplementedError("待实现：解析括号内的参数并校验")
