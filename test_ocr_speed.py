"""单独测 OCR 速度，定位慢的原因。"""

import time
from perception.screenshot import capture_screen
from perception.ocr_recognizer import OCRRecognizer

print("===== OCR 速度测试 =====\n")

# 1. 测模型加载耗时
t0 = time.time()
ocr = OCRRecognizer()
print(f"模型加载耗时：{time.time() - t0:.1f} 秒\n")

# 2. 截一张图
img = capture_screen()
print(f"截图尺寸：{img.width} x {img.height}\n")

# 3. 连续测 3 次识别，看每次耗时
for i in range(1, 4):
    t1 = time.time()
    results = ocr.recognize(img)
    elapsed = time.time() - t1
    print(f"第 {i} 次识别：{elapsed:.1f} 秒，识别到 {len(results)} 条文字")

print("\n如果每次都 30 秒以上，说明 mobile 模型没生效或图太大。")