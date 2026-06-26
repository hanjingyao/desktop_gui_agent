"""键盘操作功能。

对应 PRD 4.2.2：实现键盘的基本操作控制。
依赖库：pynput。

业务逻辑（PRD 4.2.2）：
    1. 支持中英文输入。
    2. 支持常见快捷键。
    3. 输入速度模拟人类操作。
"""


class KeyboardController:
    """封装 pynput 键盘控制。"""

    def __init__(self, type_delay: float = 0.05):
        """初始化键盘控制器。

        Args:
            type_delay: 每个字符输入之间的延迟（秒），模拟人类打字速度。
        """
        self.type_delay = type_delay
        # TODO: 初始化 pynput 的 keyboard.Controller
        self._keyboard = None

    def type(self, text: str) -> None:
        """输入文本（支持中英文）。

        Raises:
            ControlError: 输入失败时抛出。
        """
        raise NotImplementedError("待实现：输入文本")

    def press(self, key: str) -> None:
        """按下单个键（不释放）。"""
        raise NotImplementedError("待实现：按下按键")

    def release(self, key: str) -> None:
        """释放单个键。"""
        raise NotImplementedError("待实现：释放按键")

    def hotkey(self, *keys: str) -> None:
        """按下组合键，例如 hotkey('ctrl', 'c')。

        Raises:
            ControlError: 无效按键时抛出。
        """
        raise NotImplementedError("待实现：组合键")

    def scroll(self, direction: str, steps: int) -> None:
        """滚动屏幕。direction 取 'up' 或 'down'，steps 为滚动步数。"""
        raise NotImplementedError("待实现：滚动")
