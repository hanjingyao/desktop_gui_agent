"""任务执行状态管理。

对应 PRD 4.3.4：跟踪任务执行的状态与进度。
"""

import time
from enum import Enum


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

    def record_step(self, action: dict, result: str) -> None:
        """记录一步执行的动作与结果。"""
        self.steps.append({"action": action, "result": result})

    def finish(self, success: bool, fail_reason: str | None = None) -> None:
        """标记任务结束。

        Args:
            success: 是否成功。
            fail_reason: 失败原因（仅失败时填写）。
        """
        self.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        self.end_time = time.time()
        self.fail_reason = fail_reason

    @property
    def elapsed(self) -> float:
        """任务总耗时（秒）。未结束时返回 0。"""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time
