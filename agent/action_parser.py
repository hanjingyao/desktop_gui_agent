"""动作解析功能 + 系统提示词模板。

对应 PRD 4.3.2（系统提示词）与 PRD 4.3.3（动作解析）。

职责：
    1. 提供引导模型输出规范动作指令的系统提示词。
    2. 把模型输出的文本（形如 "Action: click(x=100, y=200)"）
       解析为动作字典 {"action_type": ..., "params": {...}}。
"""

import re

from utils.logger import get_logger

logger = get_logger("agent.action_parser")


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

操作建议：
- 要打开某个程序（如计算器、记事本），严格按这三步，不要做别的：
  第一步：hotkey(key1="win") 打开开始菜单
  第二步：type(text="程序名") 直接输入程序名（开始菜单弹出后焦点已在搜索框，
          不需要也不要去 click 搜索框）
  第三步：输入程序名后，必须用 hotkey(key1="enter") 回车启动，
          绝对不要用 click 去点搜索结果（你无法准确判断图标坐标）。
          只有在 enter 之后、确认目标程序窗口真正出现在屏幕上时，才用 finish。
- click 只在需要点击屏幕上明确可见的图标/按钮时使用，且 x、y 必须是具体整数像素坐标，
  绝对不能把控件名称、文字当作坐标值填入。
- type 只用于在输入框里输入内容，不能用来"打开"程序。
- 执行操作前，先观察当前屏幕处于什么状态，再决定下一步。
- 如果屏幕显示目标已经达成，立刻用 finish 动作结束。

注意事项：
- 每次只输出一个动作
- 坐标必须是整数
- 文本内容用双引号括起来
- 任务完成时必须使用 finish 动作，不要无意义地重复操作
"""

# 支持的动作类型白名单
SUPPORTED_ACTIONS = {"click", "type", "scroll", "hotkey", "finish"}


def build_prompt(user_instruction: str, history: list | None = None) -> str:
    """把系统提示词、历史动作与用户指令拼接成完整 prompt。

    Args:
        user_instruction: 用户的原始指令。
        history: 已执行过的动作列表，让模型知道进展，避免重复。
    """
    history_text = ""
    if history:
        lines = [f"  第{i}步：{a}" for i, a in enumerate(history, 1)]
        history_text = "\n你已经执行过以下动作：\n" + "\n".join(lines) + \
            "\n请根据当前屏幕和上述历史，决定下一步。不要重复已完成的动作。\n"

    return f"{SYSTEM_PROMPT}\n{history_text}\n用户指令：{user_instruction}"


def _parse_params(params_str: str) -> dict:
    """解析括号内的参数字符串，返回参数字典。

    支持的形式：
        x=500, y=300                      -> {"x":500, "y":300}
        text="www.baidu.com"              -> {"text":"www.baidu.com"}
        direction="down", steps=3         -> {"direction":"down", "steps":3}
        key1="ctrl", key2="c"             -> {"key1":"ctrl", "key2":"c"}
    """
    params: dict = {}
    if not params_str.strip():
        return params

    # 用正则逐个匹配 "键=值"，值可能是带引号的字符串或裸数字
    pattern = r'(\w+)\s*=\s*("[^"]*"|\'[^\']*\'|[^,]+)'
    for key, raw_value in re.findall(pattern, params_str):
        value = raw_value.strip()
        # 去掉两端引号 -> 字符串
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            params[key] = value[1:-1]
        else:
            # 尝试转成整数（坐标、步数等）
            try:
                params[key] = int(value)
            except ValueError:
                params[key] = value
    return params


def parse_action(model_output: str) -> dict | None:
    """解析模型输出的动作指令。

    Args:
        model_output: 模型生成的文本，形如 'Action: click(x=100, y=200)'。

    Returns:
        动作字典 {"action_type": str, "params": dict}；
        解析失败或动作类型不支持时返回 None。
    """
    if not model_output:
        return None

    # 匹配 "Action: 动作类型(参数...)"
    match = re.search(r"Action:\s*(\w+)\((.*)\)", model_output, re.DOTALL)
    if not match:
        logger.warning("无法从模型输出中匹配到动作：%s", model_output)
        return None

    action_type = match.group(1)
    params_str = match.group(2)

    if action_type not in SUPPORTED_ACTIONS:
        logger.warning("不支持的动作类型：%s", action_type)
        return None

    params = _parse_params(params_str)
    logger.info("解析动作成功：%s, 参数=%s", action_type, params)
    return {"action_type": action_type, "params": params}


# 直接运行本文件：用几个例子测试解析是否正确
if __name__ == "__main__":
    test_cases = [
        'Action: click(x=500, y=300)',
        'Action: type(text="www.baidu.com")',
        'Action: scroll(direction="down", steps=3)',
        'Action: hotkey(key1="ctrl", key2="c")',
        'Action: finish(result="任务完成")',
        '好的，我认为应该 Action: click(x=100, y=200) 来点击按钮',  # 带多余文字
        'Action: unknown_action(x=1)',   # 不支持的动作
        '这不是一条合法动作',             # 无法匹配
    ]
    print("===== 动作解析测试 =====\n")
    for case in test_cases:
        result = parse_action(case)
        print(f"输入：{case}")
        print(f"解析：{result}\n")