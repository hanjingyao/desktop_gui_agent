"""鼠标操作功能。

对应 PRD 4.2.1：实现鼠标的基本操作控制。
依赖库：pynput。

业务逻辑（PRD 4.2.1）：
    1. 坐标基于屏幕左上角原点。
    2. 操作之间添加适当延迟，模拟人类操作。
    3. 默认延迟可配置。
"""

import time

from pynput.mouse import Button, Controller

from utils.exceptions import ControlError
from utils.logger import get_logger

logger = get_logger("control.mouse_controller")


class MouseController:
    """封装 pynput 鼠标控制。"""

    def __init__(self, action_delay: float = 0.1):
        """初始化鼠标控制器。

        Args:
            action_delay: 每次操作后的默认延迟（秒），模拟人类操作节奏。
        """
        self.action_delay = action_delay
        self._mouse = Controller()

    def _sleep(self) -> None:
        """每次操作后短暂延迟。"""
        time.sleep(self.action_delay)

    def move_to(self, x: int, y: int) -> None:
        """移动鼠标到指定坐标。

        Raises:
            ControlError: 坐标为负等非法值时抛出。
        """
        if x < 0 or y < 0:
            raise ControlError(f"坐标非法：({x}, {y})")
        try:
            self._mouse.position = (x, y)
            logger.info("鼠标移动到 (%d, %d)", x, y)
            self._sleep()
        except Exception as e:
            logger.error("鼠标移动失败：%s", e)
            raise ControlError(f"鼠标移动失败：{e}") from e

    def click(self, x: int | None = None, y: int | None = None,
              button: str = "left") -> None:
        """点击。x/y 为 None 时在当前位置点击。button 取 'left' 或 'right'。"""
        try:
            if x is not None and y is not None:
                self.move_to(x, y)
            btn = Button.left if button == "left" else Button.right
            self._mouse.click(btn, 1)
            logger.info("鼠标%s键点击", "左" if button == "left" else "右")
            self._sleep()
        except ControlError:
            raise
        except Exception as e:
            logger.error("鼠标点击失败：%s", e)
            raise ControlError(f"鼠标点击失败：{e}") from e

    def right_click(self, x: int | None = None, y: int | None = None) -> None:
        """右键点击。"""
        self.click(x, y, button="right")

    def double_click(self, x: int | None = None, y: int | None = None) -> None:
        """双击。"""
        try:
            if x is not None and y is not None:
                self.move_to(x, y)
            self._mouse.click(Button.left, 2)
            logger.info("鼠标双击")
            self._sleep()
        except ControlError:
            raise
        except Exception as e:
            logger.error("鼠标双击失败：%s", e)
            raise ControlError(f"鼠标双击失败：{e}") from e

    def drag_from_to(self, x1: int, y1: int, x2: int, y2: int,
                     duration: float = 0.5) -> None:
        """从 (x1, y1) 拖拽到 (x2, y2)，duration 为拖拽耗时（秒）。"""
        try:
            self.move_to(x1, y1)
            self._mouse.press(Button.left)
            # 分若干小步平滑移动，模拟人类拖拽
            steps = 20
            for i in range(1, steps + 1):
                nx = int(x1 + (x2 - x1) * i / steps)
                ny = int(y1 + (y2 - y1) * i / steps)
                self._mouse.position = (nx, ny)
                time.sleep(duration / steps)
            self._mouse.release(Button.left)
            logger.info("鼠标从 (%d,%d) 拖拽到 (%d,%d)", x1, y1, x2, y2)
            self._sleep()
        except ControlError:
            raise
        except Exception as e:
            logger.error("鼠标拖拽失败：%s", e)
            raise ControlError(f"鼠标拖拽失败：{e}") from e


# 直接运行本文件时做一个安全的小演示：3 秒后把鼠标画一个方形轨迹
if __name__ == "__main__":
    print("3 秒后开始演示鼠标移动，请不要碰鼠标...")
    print("（演示只移动鼠标，不会点击任何东西）")
    time.sleep(3)

    mouse = MouseController(action_delay=0.3)
    # 让鼠标走一个方形的四个角，纯移动、不点击，安全
    corners = [(400, 300), (700, 300), (700, 500), (400, 500), (400, 300)]
    for (x, y) in corners:
        mouse.move_to(x, y)
    print("演示完成：鼠标走了一个方形轨迹。如果你看到鼠标在动，说明控制成功！")