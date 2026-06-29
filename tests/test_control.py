"""控制模块单元测试（PRD 6.1）。

测试范围：鼠标、键盘操作。
采用 mock 方式：不真实操作鼠标键盘，只验证代码逻辑是否正确调用底层接口。
运行：python -m pytest tests/test_control.py -v
"""

import pytest

from control.mouse_controller import MouseController
from control.keyboard_controller import KeyboardController
from utils.exceptions import ControlError


# ---------- 鼠标测试 ----------

def test_mouse_move_negative_raises():
    """坐标为负应抛出 ControlError（PRD 4.2.1 异常处理）。"""
    mouse = MouseController(action_delay=0)
    with pytest.raises(ControlError):
        mouse.move_to(-10, 50)


def test_mouse_move_non_integer_raises():
    """坐标不是整数应抛出 ControlError。"""
    mouse = MouseController(action_delay=0)
    with pytest.raises(ControlError):
        mouse.move_to(100, "abc")


def test_mouse_move_valid(monkeypatch):
    """合法坐标应能正常移动（用 mock 替换真实鼠标，不真动）。"""
    mouse = MouseController(action_delay=0)

    # 用一个假的对象替换真实鼠标控制器，记录是否被设置了坐标
    class FakeMouse:
        position = (0, 0)

    fake = FakeMouse()
    mouse._mouse = fake
    mouse.move_to(300, 400)
    assert fake.position == (300, 400)


# ---------- 键盘测试 ----------

def test_keyboard_is_ascii():
    """_is_ascii 应正确区分纯英文和含中文。"""
    kb = KeyboardController(type_delay=0)
    assert kb._is_ascii("hello123") is True
    assert kb._is_ascii("你好") is False


def test_keyboard_type_ascii(monkeypatch):
    """输入纯英文时应逐字符调用 pynput 的 type。"""
    kb = KeyboardController(type_delay=0)
    typed = []

    class FakeKeyboard:
        def type(self, ch):
            typed.append(ch)

    kb._keyboard = FakeKeyboard()
    kb.type("abc")
    assert "".join(typed) == "abc"