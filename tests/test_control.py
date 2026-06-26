"""控制模块单元测试（PRD 6.1）。

测试范围：鼠标、键盘操作。
注意：控制类测试会真实移动鼠标/输入，建议在隔离环境或用 mock 进行。
运行：pytest tests/test_control.py
"""

import pytest


@pytest.mark.skip(reason="待实现")
def test_mouse_move():
    """鼠标应能移动到指定坐标。"""
    # TODO: 建议用 mock 验证调用，避免真实操作干扰
    pass


@pytest.mark.skip(reason="待实现")
def test_keyboard_type():
    """键盘应能输入指定文本。"""
    # TODO
    pass
