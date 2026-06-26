"""OCR 文字识别功能。

对应 PRD 4.1.2：识别屏幕截图中的文字内容与位置。
依赖库：PaddleOCR（PP-OCRv4 模型）。

性能要求（PRD 5.1）：单帧 OCR 识别耗时 <= 200ms。
准确率要求（PRD 4.1.2）：清晰屏幕文字识别准确率 >= 90%。
"""

from PIL import Image


class OCRRecognizer:
    """封装 PaddleOCR，提供屏幕文字识别能力。"""

    def __init__(self):
        """初始化并加载 PaddleOCR PP-OCRv4 模型（支持中英文混合）。

        Raises:
            OCRError: 模型加载失败时抛出。
        """
        # TODO: 加载 PaddleOCR 模型，建议只加载一次后复用
        self._ocr = None
        raise NotImplementedError("待实现：初始化 PaddleOCR 模型")

    def recognize(self, image: Image.Image) -> list[dict]:
        """识别图像中的文字。

        Args:
            image: PIL.Image 对象（屏幕截图）。

        Returns:
            识别结果列表，每个元素为字典：
                {
                    "text": str,          # 识别到的文字内容
                    "bbox": (x1, y1, x2, y2),  # 文字区域边界框
                    "confidence": float,  # 识别置信度
                }
            识别结果为空时返回空列表。

        业务逻辑（PRD 4.1.2）：
            1. 自动处理不同分辨率的截图。
            2. 支持中英文混合识别。
        """
        # TODO: 调用 PaddleOCR 识别，整理为上述结构返回
        raise NotImplementedError("待实现：调用 PaddleOCR 并整理输出格式")
