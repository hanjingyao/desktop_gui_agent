"""UI 元素定位与可视化功能。

对应 PRD 4.1.3：在截图上标注识别到的 UI 元素与坐标，便于调试观察。
依赖库：Pillow。

业务逻辑（PRD 4.1.3）：
    1. 用矩形框标注每个 UI 元素的边界。
    2. 在每个元素附近标注其序号与文本内容。
    3. 不同元素循环使用不同颜色标注。
    4. 输入元素为空时返回原始图像。
"""

from PIL import Image, ImageDraw, ImageFont

from utils.logger import get_logger

logger = get_logger("perception.ui_locator")

# 循环使用的标注颜色（不同元素换色，便于区分）
_COLORS = [
    (255, 0, 0),    # 红
    (0, 128, 255),  # 蓝
    (0, 200, 0),    # 绿
    (255, 128, 0),  # 橙
    (160, 0, 255),  # 紫
]


def _load_font(size: int = 16) -> ImageFont.FreeTypeFont:
    """加载一个能显示中文的字体，失败则退回默认字体。"""
    # Windows 常见中文字体候选
    candidates = ["simhei.ttf", "msyh.ttc", "simsun.ttc"]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    # 都加载不到就用 PIL 默认字体（中文可能显示为方框，但不报错）
    logger.warning("未找到中文字体，标注中文可能显示异常")
    return ImageFont.load_default()


def annotate_elements(image: Image.Image, elements: list[dict]) -> Image.Image:
    """在截图上标注 UI 元素。

    Args:
        image: 原始屏幕截图（PIL.Image）。
        elements: OCR 识别结果列表，每个元素含 text / bbox / confidence。

    Returns:
        标注后的 PIL.Image 对象；elements 为空时返回原始图像。
    """
    if not elements:
        return image

    # 复制一份再画，不破坏原图
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    font = _load_font(16)

    for idx, elem in enumerate(elements, 1):
        x1, y1, x2, y2 = elem["bbox"]
        color = _COLORS[idx % len(_COLORS)]

        # 1) 画边界矩形
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        # 2) 在框左上角标注「序号: 文本」
        label = f"{idx}: {elem['text']}"
        # 标签画在框的上方，太靠顶就改画在框内
        text_y = y1 - 18 if y1 - 18 > 0 else y1
        draw.text((x1, text_y), label, fill=color, font=font)

    logger.info("已标注 %d 个元素", len(elements))
    return annotated


# 直接运行本文件时：截图 -> OCR -> 标注 -> 存盘，串起整个感知流程
if __name__ == "__main__":
    from perception.screenshot import capture_screen
    from perception.ocr_recognizer import OCRRecognizer

    print("正在截图...")
    img = capture_screen()

    print("正在识别文字...")
    recognizer = OCRRecognizer()
    items = recognizer.recognize(img)

    print(f"识别到 {len(items)} 个元素，正在标注...")
    result_img = annotate_elements(img, items)
    result_img.save("annotated_test.png")
    print("已保存标注结果为 annotated_test.png，打开它就能看到识别框")