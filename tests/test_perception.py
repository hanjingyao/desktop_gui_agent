"""感知模块单元测试（PRD 6.1）。

测试范围：截图、OCR、UI 定位。
运行：pytest tests/test_perception.py
"""

import pytest


@pytest.mark.skip(reason="待实现")
def test_capture_screen():
    """截图应返回 PIL.Image 对象。"""
    # TODO: 调用 perception.screenshot.capture_screen 并断言返回类型
    pass


@pytest.mark.skip(reason="待实现")
def test_ocr_recognize():
    """OCR 应能识别一张含已知文字的图片。"""
    # TODO
    pass
