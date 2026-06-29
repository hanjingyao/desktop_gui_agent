"""任务执行状态管理。

对应 PRD 4.3.4：跟踪任务执行的状态与进度。
"""

import time
from enum import Enum

from utils.logger import get_logger

logger = get_logger("agent.task_manager")


class TaskStatus(Enum):
    """任务状态定义（PRD 4.3.4）。"""

    PENDING = "pending"   # 待执行
    RUNNING = "running"   # 执行中
    SUCCESS = "success"   # 执行成功
    FAILED = "failed"     # 执行失败


class TaskManager:
    """记录单个任务的执行状态、步骤、耗时与失败原因。"""

    def __init__(self, instruction: str):
        """Args: instruction: 本次任务的用户指令。"""
        self.instruction = instruction
        self.status = TaskStatus.PENDING
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.steps: list[dict] = []      # 每步执行的动作与结果
        self.retry_count = 0             # 累计重试次数
        self.fail_reason: str | None = None

    def start(self) -> None:
        """标记任务开始，记录开始时间戳。"""
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        logger.info("任务开始：%s", self.instruction)

    def record_step(self, action: dict, result: str) -> None:
        """记录一步执行的动作与结果。"""
        self.steps.append({"action": action, "result": result})
        logger.info("第 %d 步：%s -> %s", len(self.steps), action, result)

    def add_retry(self) -> None:
        """累加一次重试计数。"""
        self.retry_count += 1

    def finish(self, success: bool, fail_reason: str | None = None) -> None:
        """标记任务结束。

        Args:
            success: 是否成功。
            fail_reason: 失败原因（仅失败时填写）。
        """
        self.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        self.end_time = time.time()
        self.fail_reason = fail_reason
        logger.info("任务结束：%s，耗时 %.2f 秒", self.status.value, self.elapsed)

    @property
    def step_count(self) -> int:
        """已执行的步数。"""
        return len(self.steps)

    @property
    def elapsed(self) -> float:
        """任务总耗时（秒）。未结束时返回 0。"""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    def summary(self) -> str:
        """返回一段任务执行摘要，便于打印查看。"""
        lines = [
            f"指令：{self.instruction}",
            f"状态：{self.status.value}",
            f"步数：{self.step_count}，重试：{self.retry_count}",
            f"耗时：{self.elapsed:.2f} 秒",
        ]
        if self.fail_reason:
            lines.append(f"失败原因：{self.fail_reason}")
        return "\n".join(lines)


# 直接运行本文件：模拟一个任务的生命周期，验证状态管理正常
if __name__ == "__main__":
    print("===== 模拟一个任务的执行过程 =====\n")
    task = TaskManager("打开计算器并计算 1+1")

    task.start()
    print("当前状态：", task.status.value)        # running

    # 模拟执行两步动作
    task.record_step({"action_type": "click", "params": {"x": 500, "y": 300}}, "成功")
    time.sleep(0.5)
    task.record_step({"action_type": "type", "params": {"text": "1+1"}}, "成功")

    task.finish(success=True)
    print("\n===== 任务摘要 =====")
    print(task.summary())
    print("\n如果上面显示状态=success、步数=2，说明 4.3.4 任务状态管理验证通过！")