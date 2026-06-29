"""程序主入口。

对应 PRD 4.4.1（流程控制）与 PRD 4.4.2（命令行交互界面）。

核心流程（PRD 3.2 / 4.4.1）：
    截屏 -> 调模型生成动作 -> 解析动作 -> 执行动作 -> 检查是否完成 -> 循环
"""

import time

import config
from perception.screenshot import capture_screen
from perception.ocr_recognizer import OCRRecognizer
from control.mouse_controller import MouseController
from control.keyboard_controller import KeyboardController
from agent.model_client import ModelClient
from agent.action_parser import build_prompt, parse_action
from agent.task_manager import TaskManager
from utils.logger import get_logger

logger = get_logger("main", config.LOG_FILE)


def execute_action(action: dict, mouse: MouseController,
                   keyboard: KeyboardController) -> bool:
    """根据解析出的动作，调用对应的鼠标/键盘方法。

    Args:
        action: parse_action 返回的动作字典。
        mouse / keyboard: 控制器实例。

    Returns:
        是否为 finish 动作（True 表示任务结束）。
    """
    atype = action["action_type"]
    params = action["params"]

    if atype == "click":
        mouse.click(params["x"], params["y"])
    elif atype == "double_click":
        mouse.double_click(params["x"], params["y"])
    elif atype == "type":
        keyboard.type(params["text"])
    elif atype == "scroll":
        keyboard.scroll(params["direction"], int(params.get("steps", 3)))
    elif atype == "hotkey":
        # hotkey 参数形如 key1="ctrl", key2="c"，按顺序取出所有值
        keys = [v for k, v in sorted(params.items()) if k.startswith("key")]
        keyboard.hotkey(*keys)
    elif atype == "finish":
        return True  # 任务完成

    return False


def run_task(instruction: str) -> str:
    """执行单个自然语言任务（PRD 4.4.1）。

    Args:
        instruction: 用户输入的自然语言指令。

    Returns:
        任务执行结果描述。
    """
    task = TaskManager(instruction)
    task.start()

    # 初始化各模块
    mouse = MouseController(action_delay=config.MOUSE_ACTION_DELAY)
    keyboard = KeyboardController(type_delay=config.KEYBOARD_TYPE_DELAY)
    model = ModelClient(mode=config.MODEL_MODE, model_name=config.API_MODEL_NAME)
    print("正在加载 OCR 模型（首次较慢）...")
    ocr = OCRRecognizer()

    for step in range(1, config.MAX_STEPS + 1):
        print(f"\n[步骤 {step}] 截图并请模型决策...")

    history = []  # 记录已执行的动作，给模型当记忆

    for step in range(1, config.MAX_STEPS + 1):
        print(f"\n[步骤 {step}] 截图并请模型决策...")

# a. 截屏
        image = capture_screen()

        # a2. OCR 识别屏幕元素及其坐标，供模型精确点击
        elements = ocr.recognize(image)
        # 把每个元素整理成「文字 -> 中心坐标」清单
        elem_lines = []
        for e in elements:
            x1, y1, x2, y2 = e["bbox"]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # 中心点坐标
            elem_lines.append(f'  "{e["text"]}" 中心坐标=({cx}, {cy})')
        elements_text = "\n".join(elem_lines)

        # b. 调模型生成动作（带上历史动作 + 屏幕元素坐标）
        prompt = build_prompt(instruction, history, elements_text)
        try:
            output = model.generate(image, prompt)
        except Exception as e:
            logger.error("模型调用失败：%s", e)
            task.finish(success=False, fail_reason=f"模型调用失败：{e}")
            return f"任务失败：模型调用出错（{e}）"

        print(f"  模型输出：{output.strip()}")

        # c. 解析动作
        action = parse_action(output)
        if action is None:
            print("  解析失败，跳过本步")
            task.add_retry()
            continue

        # d. 执行动作
        print(f"  执行动作：{action['action_type']}({action['params']})")
        try:
            is_finish = execute_action(action, mouse, keyboard)
        except Exception as e:
            logger.error("动作执行失败：%s", e)
            task.record_step(action, f"执行失败：{e}")
            task.add_retry()
            continue

        task.record_step(action, "成功")
        history.append(f"{action['action_type']}({action['params']})")

        # e. 检查是否完成
        if is_finish:
            result = action["params"].get("result", "任务完成")
            task.finish(success=True)
            return f"任务执行成功：{result}"

        # 等屏幕响应后再进入下一轮
        time.sleep(1)

    task.finish(success=False, fail_reason="达到最大步数仍未完成")
    return "任务未在最大步数内完成"


def main() -> None:
    """命令行交互界面（PRD 4.4.2）。"""
    print("=" * 40)
    print("欢迎使用桌面 GUI 智能体！")
    print("输入自然语言指令，我会自动操作电脑完成。")
    print("输入 'exit' 退出程序")
    print("=" * 40)

    while True:
        instruction = input("\n请输入指令：").strip()
        if instruction.lower() == "exit":
            print("已退出。")
            break
        if not instruction:
            continue

        print("\n任务开始，请不要操作鼠标键盘，3 秒后启动...")
        time.sleep(3)
        try:
            result = run_task(instruction)
            print("\n" + "=" * 40)
            print(result)
            print("=" * 40)
        except Exception as e:
            logger.error("任务执行出错：%s", e)
            print(f"出错了：{e}")


if __name__ == "__main__":
    main()