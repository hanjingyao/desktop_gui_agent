"""屏幕截图功能。

对应 PRD 4.1.1：实现跨平台（Windows / macOS / Linux）的屏幕实时截图能力。
依赖库：mss、Pillow。

性能要求（PRD 5.1）：单帧截图耗时 <= 50ms。
"""

from PIL import Image


def capture_screen(screen_id: int = 0, region: tuple | None = None) -> Image.Image:
    """截取屏幕画面。

    Args:
        screen_id: 屏幕编号，多屏环境下指定截哪块屏，默认 0（主屏）。
        region: 截图区域，格式 (left, top, width, height)。
                为 None 时截取全屏。

    Returns:
        PIL.Image 对象（截图）。

    Raises:
        ScreenshotError: 截图失败、屏幕不存在或区域越界时抛出。

    业务逻辑（PRD 4.1.1）：
        1. 支持 Windows / macOS / Linux 三大系统。
        2. 自动适配不同分辨率与 DPI 缩放。
        3. 单帧截图耗时 <= 50ms。
        4. 支持多屏环境下指定屏幕截图。
    """
    # TODO: 用 mss 抓取屏幕，转换为 PIL.Image 返回
    raise NotImplementedError("待实现：使用 mss 截图并转为 PIL.Image")
