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