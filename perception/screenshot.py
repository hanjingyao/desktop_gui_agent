"""屏幕截图功能。

对应 PRD 4.1.1：实现跨平台（Windows / macOS / Linux）的屏幕实时截图能力。
依赖库：mss、Pillow。

性能要求（PRD 5.1）：单帧截图耗时 <= 50ms。
"""

import mss
from PIL import Image

from utils.exceptions import ScreenshotError
from utils.logger import get_logger

logger = get_logger("perception.screenshot")


def capture_screen(screen_id: int = 0, region: tuple | None = None) -> Image.Image:
    """截取屏幕画面。

    Args:
        screen_id: 屏幕编号，多屏环境下指定截哪块屏，默认 0（主屏）。
        region: 截图区域，格式 (left, top, width, height)。
                为 None 时截取整块屏幕。

    Returns:
        PIL.Image 对象（截图）。

    Raises:
        ScreenshotError: 截图失败、屏幕不存在或区域越界时抛出。
    """
    try:
        with mss.mss() as sct:
            # sct.monitors 是一个列表：
            #   下标 0 = 所有屏幕拼成的虚拟大屏
            #   下标 1 = 第一块物理屏，2 = 第二块，以此类推
            # 我们约定 screen_id=0 表示主屏，对应 monitors[1]
            monitor_index = screen_id + 1

            if monitor_index >= len(sct.monitors):
                raise ScreenshotError(
                    f"屏幕 {screen_id} 不存在，当前共检测到 "
                    f"{len(sct.monitors) - 1} 块屏幕"
                )

            monitor = sct.monitors[monitor_index]

            # 如果指定了区域，把 (left, top, width, height) 转成 mss 需要的格式
            if region is not None:
                left, top, width, height = region
                if width <= 0 or height <= 0:
                    raise ScreenshotError(f"区域尺寸非法：{region}")
                grab_area = {
                    "left": monitor["left"] + left,
                    "top": monitor["top"] + top,
                    "width": width,
                    "height": height,
                }
            else:
                grab_area = monitor

            # 真正抓屏
            raw = sct.grab(grab_area)

        # 把 mss 的原始像素转成 PIL.Image（mss 的像素顺序是 BGRA）
        image = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        logger.info("截图成功，尺寸 %sx%s", image.width, image.height)
        return image

    except ScreenshotError:
        # 我们自己抛的异常，记录后原样向上抛
        logger.error("截图失败：参数错误")
        raise
    except Exception as e:
        # 其他意外错误，包装成 ScreenshotError 再抛
        logger.error("截图失败：%s", e)
        raise ScreenshotError(f"截图时发生错误：{e}") from e


# 直接运行本文件时，做一次截图并存盘，方便快速验证
if __name__ == "__main__":
    img = capture_screen()
    img.save("screenshot_test.png")
    print(f"已截图并保存为 screenshot_test.png，尺寸 {img.width}x{img.height}")