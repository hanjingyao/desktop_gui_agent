"""程序主入口。

对应 PRD 4.4.1（流程控制）与 PRD 4.4.2（命令行交互界面）。

核心流程（PRD 3.2 / 4.4.1）：
    截屏 -> 调模型生成动作 -> 解析动作 -> 执行动作 -> 检查是否完成 -> 循环
"""

import config
from agent.action_parser import build_prompt, parse_action
from agent.model_client import ModelClient
from agent.task_manager import TaskManager
from utils.logger import get_logger

logger = get_logger("main", config.LOG_FILE)


def run_task(instruction: str) -> str:
    """执行单个自然语言任务（PRD 4.4.1）。

    Args:
        instruction: 用户输入的自然语言指令。

    Returns:
        任务执行结果描述。

    流程：
        1. 初始化任务状态。
        2. 循环直到任务完成或达到 MAX_STEPS：
           a. 截取当前屏幕
           b. 调用模型生成动作指令
           c. 解析动作指令
           d. 执行动作
           e. 检查任务是否完成（finish 动作）
        3. 返回最终结果。
    """
    task = TaskManager(instruction)
    task.start()
    logger.info("开始任务：%s", instruction)

    # TODO: 实例化感知、控制、模型各模块
    # screenshotter = ...
    # mouse, keyboard = ...
    model = ModelClient(mode=config.MODEL_MODE, model_name=config.API_MODEL_NAME)

    for step in range(1, config.MAX_STEPS + 1):
        # a. 截屏
        # image = capture_screen()
        # b. 调模型
        # prompt = build_prompt(instruction)
        # output = model.generate(image, prompt)
        # c. 解析
        # action = parse_action(output)
        # d. 执行（点击/输入/滚动/快捷键）
        # e. 若是 finish，结束循环
        raise NotImplementedError("待实现：端到端循环（截屏->模型->解析->执行）")

    task.finish(success=False, fail_reason="达到最大步数仍未完成")
    return "任务未在最大步数内完成"


def main() -> None:
    """命令行交互界面（PRD 4.4.2）。"""
    print("欢迎使用桌面 GUI 智能体！")
    print("输入 'exit' 退出程序")
    while True:
        instruction = input("请输入指令：").strip()
        if instruction.lower() == "exit":
            print("已退出。")
            break
        if not instruction:
            continue
        try:
            result = run_task(instruction)
            print(result)
        except NotImplementedError as e:
            print(f"[功能开发中] {e}")
        except Exception as e:  # noqa: BLE001 顶层兜底，记录后继续
            logger.error("任务执行出错：%s", e)
            print(f"出错了：{e}")


if __name__ == "__main__":
    main()
