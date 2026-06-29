"""键盘操作功能。

对应 PRD 4.2.2：实现键盘的基本操作控制。
依赖库：pynput、pyperclip。

业务逻辑（PRD 4.2.2）：
    1. 支持中英文输入（中文通过剪贴板粘贴实现，规避 pynput 中文限制）。
    2. 支持常见快捷键。
    3. 输入速度模拟人类操作。
"""

import time

import pyperclip
from pynput.keyboard import Controller, Key

from utils.exceptions import ControlError
from utils.logger import get_logger

logger = get_logger("control.keyboard_controller")

# 特殊键名 -> pynput 的 Key 映射，便于用字符串调用
_SPECIAL_KEYS = {
    "enter": Key.enter,
    "tab": Key.tab,
    "space": Key.space,
    "backspace": Key.backspace,
    "esc": Key.esc,
    "ctrl": Key.ctrl,
    "shift": Key.shift,
    "alt": Key.alt,
    "cmd": Key.cmd,
    "win": Key.cmd,
    "delete": Key.delete,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
}


def _to_key(key: str):
    """把字符串键名转成 pynput 能用的键对象。"""
    k = key.lower()
    if k in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[k]
    # 普通单字符（如 'a'、'c'）直接返回字符本身
    return key


class KeyboardController:
    """封装 pynput 键盘控制。"""

    def __init__(self, type_delay: float = 0.05):
        """初始化键盘控制器。

        Args:
            type_delay: 每个字符输入之间的延迟（秒），模拟人类打字速度。
        """
        self.type_delay = type_delay
        self._keyboard = Controller()

    def _is_ascii(self, text: str) -> bool:
        """判断文本是否全是 ASCII（英文/数字/符号）。"""
        return all(ord(c) < 128 for c in text)

    def type(self, text: str) -> None:
        """输入文本（支持中英文）。

        英文/数字/符号逐字符输入；含中文则走剪贴板粘贴。

        Raises:
            ControlError: 输入失败时抛出。
        """
        try:
            if self._is_ascii(text):
                # 纯英文：逐字符输入，模拟打字
                for ch in text:
                    self._keyboard.type(ch)
                    time.sleep(self.type_delay)
            else:
                # 含中文：写入剪贴板再 Ctrl+V 粘贴
                pyperclip.copy(text)
                time.sleep(0.1)
                self.hotkey("ctrl", "v")
            logger.info("输入文本：%s", text)
        except Exception as e:
            logger.error("输入文本失败：%s", e)
            raise ControlError(f"输入文本失败：{e}") from e

    def press(self, key: str) -> None:
        """按下单个键（不释放）。"""
        try:
            self._keyboard.press(_to_key(key))
            logger.info("按下键：%s", key)
        except Exception as e:
            logger.error("按键失败：%s", e)
            raise ControlError(f"按键失败：{e}") from e

    def release(self, key: str) -> None:
        """释放单个键。"""
        try:
            self._keyboard.release(_to_key(key))
            logger.info("释放键：%s", key)
        except Exception as e:
            logger.error("释放键失败：%s", e)
            raise ControlError(f"释放键失败：{e}") from e

    def hotkey(self, *keys: str) -> None:
        """按下组合键，例如 hotkey('ctrl', 'c')。

        Raises:
            ControlError: 无效按键时抛出。
        """
        try:
            key_objs = [_to_key(k) for k in keys]
            # 依次按下所有键，再逆序释放
            for k in key_objs:
                self._keyboard.press(k)
            for k in reversed(key_objs):
                self._keyboard.release(k)
            logger.info("组合键：%s", "+".join(keys))
            time.sleep(self.type_delay)
        except Exception as e:
            logger.error("组合键失败：%s", e)
            raise ControlError(f"组合键失败：{e}") from e

    def scroll(self, direction: str, steps: int) -> None:
        """滚动屏幕。direction 取 'up' 或 'down'，steps 为滚动步数。"""
        try:
            from pynput.mouse import Controller as MouseCtrl
            mouse = MouseCtrl()
            # pynput 滚动：向上为正、向下为负
            dy = steps if direction == "up" else -steps
            mouse.scroll(0, dy)
            logger.info("滚动 %s %d 步", direction, steps)
            time.sleep(self.type_delay)
        except Exception as e:
            logger.error("滚动失败：%s", e)
            raise ControlError(f"滚动失败：{e}") from e


# 直接运行本文件时做一个安全演示：5 秒后在你聚焦的输入框里打一段中英文
if __name__ == "__main__":
    print("演示将在 5 秒后开始。")
    print("请在这 5 秒内，把鼠标点进一个可以打字的地方")
    print("（比如打开记事本并点进去），演示会自动输入一段文字。")
    time.sleep(5)

    kb = KeyboardController()
    kb.type("Hello 你好 GUI Agent 123")
    print("\n演示完成：如果你聚焦的输入框里出现了那段中英文，说明键盘控制成功！")