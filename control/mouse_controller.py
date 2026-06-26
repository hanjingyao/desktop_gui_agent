"""鼠标操作功能。

对应 PRD 4.2.1：实现鼠标的基本操作控制。
依赖库：pynput。

业务逻辑（PRD 4.2.1）：
    1. 坐标基于屏幕左上角原点。
    2. 操作之间添加适当延迟，模拟人类操作。
    3. 默认延迟可配置。
"""


class MouseController:
    """封装 pynput 鼠标控制。"""

    def __init__(self, action_delay: float = 0.1):
        """初始化鼠标控制器。

        Args:
            action_delay: 每次操作后的默认延迟（秒），模拟人类操作节奏。
        """
        self.action_delay = action_delay
        # TODO: 初始化 pynput 的 mouse.Controller
        self._mouse = None

    def move_to(self, x: int, y: int) -> None:
        """移动鼠标到指定坐标。

        Raises:
            ControlError: 坐标越界时抛出。
        """
        raise NotImplementedError("待实现：移动鼠标")

    def click(self, x: int | None = None, y: int | None = None,
              button: str = "left") -> None:
        """点击。x/y 为 None 时在当前位置点击。button 取 'left' 或 'right'。"""
        raise NotImplementedError("待实现：鼠标点击")

    def right_click(self, x: int | None = None, y: int | None = None) -> None:
        """右键点击。"""
        raise NotImplementedError("待实现：右键点击")

    def double_click(self, x: int | None = None, y: int | None = None) -> None:
        """双击。"""
        raise NotImplementedError("待实现：双击")

    def drag_from_to(self, x1: int, y1: int, x2: int, y2: int,
                     duration: float = 0.5) -> None:
        """从 (x1, y1) 拖拽到 (x2, y2)，duration 为拖拽耗时（秒）。"""
        raise NotImplementedError("待实现：拖拽")
