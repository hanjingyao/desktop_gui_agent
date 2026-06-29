"""OCR 文字识别功能。

对应 PRD 4.1.2：识别屏幕截图中的文字内容与位置。
依赖库：PaddleOCR（PP-OCRv6，本机已装 paddleocr 3.x）。

注意：PaddleOCR 3.x 的用法与旧版不同——
    - 用 ocr.predict(图片) 而非旧的 ocr.ocr()
    - 返回结果中文字在 rec_texts、置信度在 rec_scores、框在 rec_polys
    - enable_mkldnn=False：关闭 oneDNN 加速，规避其在本机的算子兼容问题
"""

import numpy as np
from PIL import Image

from utils.exceptions import OCRError
from utils.logger import get_logger

logger = get_logger("perception.ocr_recognizer")


def _poly_to_bbox(poly) -> tuple:
    """把四角点多边形转成外接矩形 (x1, y1, x2, y2)。

    PaddleOCR 给的是文字框的四个角点（可应对倾斜文字），
    PRD 4.1.2 要求的 bbox 是矩形，这里取四点的最小/最大值。
    """
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))


class OCRRecognizer:
    """封装 PaddleOCR，提供屏幕文字识别能力。"""

    def __init__(self):
        """初始化并加载 PaddleOCR 模型（支持中英文混合）。

        Raises:
            OCRError: 模型加载失败时抛出。
        """
        try:
            from paddleocr import PaddleOCR

            # 关掉对截屏没必要的额外模块；关掉 mkldnn 规避算子兼容问题
            self._ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
            )
            logger.info("PaddleOCR 模型加载成功")
        except Exception as e:
            logger.error("PaddleOCR 模型加载失败：%s", e)
            raise OCRError(f"PaddleOCR 模型加载失败：{e}") from e

    def recognize(self, image: Image.Image) -> list[dict]:
        """识别图像中的文字。

        Args:
            image: PIL.Image 对象（屏幕截图）。

        Returns:
            识别结果列表，每个元素为字典：
                {"text": str, "bbox": (x1, y1, x2, y2), "confidence": float}
            识别结果为空时返回空列表。
        """
# 大图 OCR 很慢，先缩小再识别，识别后把坐标按比例还原
        scale = 0.5  # 缩小到一半
        small = image.resize(
            (int(image.width * scale), int(image.height * scale))
        )
        try:
            img_array = np.array(small)
            result = self._ocr.predict(img_array)
        except Exception as e:
            logger.error("OCR 识别出错：%s", e)
            raise OCRError(f"OCR 识别出错：{e}") from e

        results: list[dict] = []
        for res in result:
            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            polys = res.get("rec_polys", [])
        for text, score, poly in zip(texts, scores, polys):
                x1, y1, x2, y2 = _poly_to_bbox(poly)
                # 坐标按缩放比例还原到原图尺寸
                bbox = (int(x1 / scale), int(y1 / scale),
                        int(x2 / scale), int(y2 / scale))
                results.append({
                    "text": text,
                    "bbox": bbox,
                    "confidence": float(score),
                })

        logger.info("OCR 识别完成，共 %d 条文字", len(results))
        return results


if __name__ == "__main__":
    import sys

    img_path = sys.argv[1] if len(sys.argv) > 1 else "screenshot_test.png"
    test_image = Image.open(img_path).convert("RGB")
    recognizer = OCRRecognizer()
    items = recognizer.recognize(test_image)
    print(f"\n共识别到 {len(items)} 条文字：\n")
    for i, item in enumerate(items, 1):
        print(f"[{i}] \"{item['text']}\"  "
              f"置信度={item['confidence']:.2f}  "
              f"位置={item['bbox']}")