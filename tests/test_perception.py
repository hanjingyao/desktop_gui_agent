"""感知模块单元测试（PRD 6.1）。

测试范围：截图、OCR、UI 定位。
运行：python -m pytest tests/test_perception.py -v
"""

from PIL import Image

from perception.screenshot import capture_screen
from perception.ocr_recognizer import OCRRecognizer
from perception.ui_locator import annotate_elements


def test_capture_screen_returns_image():
    """截图应返回一个 PIL.Image 对象，且尺寸大于 0。"""
    img = capture_screen()
    assert isinstance(img, Image.Image)
    assert img.width > 0 and img.height > 0


def test_annotate_empty_returns_original():
    """传入空元素列表时，标注函数应原样返回图像（PRD 4.1.3）。"""
    img = Image.new("RGB", (100, 100))
    result = annotate_elements(img, [])
    assert result is img


def test_annotate_draws_without_error():
    """传入元素时，标注应正常完成并返回一张图（不报错）。"""
    img = Image.new("RGB", (200, 200))
    elements = [{"text": "测试", "bbox": (10, 10, 80, 30), "confidence": 0.95}]
    result = annotate_elements(img, elements)
    assert isinstance(result, Image.Image)


def test_ocr_recognize_returns_list():
    """OCR 识别一张纯色图（无文字）应返回列表（可能为空），不报错。

    说明：加载 OCR 模型较慢，此测试会耗时较长，属正常现象。
    """
    recognizer = OCRRecognizer()
    img = Image.new("RGB", (300, 100), color="white")
    results = recognizer.recognize(img)
    assert isinstance(results, list)