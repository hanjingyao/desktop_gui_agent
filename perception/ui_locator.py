"""UI 元素定位与可视化功能。

对应 PRD 4.1.3：在截图上标注识别到的 UI 元素与坐标，便于调试观察。
依赖库：OpenCV、Pillow。
"""

from PIL import Image


def annotate_elements(image: Image.Image, elements: list[dict]) -> Image.Image:
    """在截图上标注 UI 元素。

    Args:
        image: 原始屏幕截图。
        elements: 识别到的 UI 元素列表（结构见 OCRRecognizer.recognize 的返回）。

    Returns:
        标注后的 PIL.Image 对象。输入 elements 为空时返回原始图像。

    业务逻辑（PRD 4.1.3）：
        1. 用矩形框标注每个 UI 元素的边界。
        2. 在每个元素附近标注其序号与文本内容。
        3. 不同类型元素使用不同颜色标注。
    """
    if not elements:
        return image
    # TODO: 用 OpenCV / PIL 在图上画框、写序号与文本
    raise NotImplementedError("待实现：在截图上绘制元素边框与标注")
