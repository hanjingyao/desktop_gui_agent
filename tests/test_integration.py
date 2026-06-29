"""集成测试（PRD 6.2）。

测试模块之间的接口与数据交互是否正确衔接：
    1. 感知模块 -> UI标注模块 的数据交互
    2. Agent模块（解析）-> 控制模块 的数据交互
    3. 端到端流程的连通性（不真实操作，用 mock）
运行：python -m pytest tests/test_integration.py -v
"""

from PIL import Image

from perception.ui_locator import annotate_elements
from agent.action_parser import parse_action, build_prompt, SYSTEM_PROMPT
from control.mouse_controller import MouseController
from control.keyboard_controller import KeyboardController


# ---------- 1. 感知 -> 标注 的数据交互 ----------

def test_perception_output_feeds_annotator():
    """OCR 输出的元素格式，应能直接被 UI 标注模块接收并处理。"""
    img = Image.new("RGB", (300, 200))
    # 模拟一条 OCR 输出（格式与 OCRRecognizer.recognize 返回一致）
    ocr_output = [
        {"text": "确定", "bbox": (50, 60, 120, 90), "confidence": 0.98},
        {"text": "取消", "bbox": (150, 60, 220, 90), "confidence": 0.97},
    ]
    # 标注模块能接住这个格式、正常返回图像，即说明接口对接成功
    result = annotate_elements(img, ocr_output)
    assert isinstance(result, Image.Image)


# ---------- 2. Agent解析 -> 控制 的数据交互 ----------

def test_parse_output_feeds_mouse():
    """动作解析输出的 click 动作，应能正确驱动鼠标控制器。"""
    # 模型输出 -> 解析
    action = parse_action("Action: click(x=200, y=300)")
    assert action["action_type"] == "click"

    # 解析结果 -> 控制模块（用假鼠标，不真动）
    mouse = MouseController(action_delay=0)

    class FakeMouse:
        position = (0, 0)
        def click(self, btn, n): pass

    mouse._mouse = FakeMouse()
    # 用解析出的参数驱动鼠标，能正常执行不报错即接口通畅
    mouse.click(action["params"]["x"], action["params"]["y"])
    assert mouse._mouse.position == (200, 300)


def test_parse_output_feeds_keyboard():
    """动作解析输出的 type 动作，应能正确驱动键盘控制器。"""
    action = parse_action('Action: type(text="hello")')
    assert action["action_type"] == "type"

    kb = KeyboardController(type_delay=0)
    typed = []

    class FakeKeyboard:
        def type(self, ch): typed.append(ch)

    kb._keyboard = FakeKeyboard()
    kb.type(action["params"]["text"])
    assert "".join(typed) == "hello"


# ---------- 3. 端到端流程连通性 ----------

def test_prompt_contains_instruction_and_system():
    """build_prompt 应把系统提示词和用户指令正确拼接（流程起点连通）。"""
    prompt = build_prompt("打开计算器")
    assert "打开计算器" in prompt
    assert SYSTEM_PROMPT[:10] in prompt  # 系统提示词也在


def test_full_chain_parse_to_action_dict():
    """端到端关键链路：模型输出文本 -> 解析 -> 可执行动作字典。"""
    # 模拟模型返回一条带多余文字的输出
    model_output = "好的，下一步 Action: double_click(x=55, y=138) 打开图标"
    action = parse_action(model_output)
    # 解析后应得到结构完整、可被控制模块使用的动作
    assert action is not None
    assert action["action_type"] == "double_click"
    assert action["params"]["x"] == 55
    assert action["params"]["y"] == 138