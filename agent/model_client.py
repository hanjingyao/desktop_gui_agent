"""多模态模型调用接口。

对应 PRD 4.3.1：统一封装通义千问多模态模型的调用，支持本地部署与在线 API 两种模式。

模式说明：
    - 'api'  ：调用阿里云百炼（DashScope）在线接口，无需本地 GPU。【当前主用】
    - 'local'：用 Transformers 加载 Qwen2-VL 在本机运行，需要足够显存。（待实现）

API 模式需在系统环境变量中配置 DASHSCOPE_API_KEY，切勿写入代码或提交仓库。

异常处理（PRD 4.3.1）：
    - API 调用失败时重试最多 3 次。
    - 所有异常均记录日志并返回错误信息。
"""

import base64
import io
import os
import time

from PIL import Image

from utils.exceptions import ModelError
from utils.logger import get_logger

logger = get_logger("agent.model_client")

DEFAULT_API_MODEL = "qwen-vl-plus"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_RETRY = 3  # API 调用失败最多重试次数（PRD 4.3.1）


def _image_to_base64(image: Image.Image) -> str:
    """把 PIL.Image 编码为 base64 字符串。"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class ModelClient:
    """多模态模型调用客户端。"""

    def __init__(self, mode: str = "api", model_name: str = DEFAULT_API_MODEL):
        """初始化模型客户端。

        Args:
            mode: 'api' 或 'local'，默认 'api'。
            model_name: API 模式下使用的模型名称。
        """
        self.mode = mode
        self.model_name = model_name
        self._client = None
        if mode == "api":
            self._init_api_client()
        else:
            self._init_local_model()

    def _init_api_client(self) -> None:
        """初始化 API 客户端（OpenAI 兼容方式调用百炼）。"""
        from openai import OpenAI

        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ModelError("未找到环境变量 DASHSCOPE_API_KEY，请先配置 API Key。")
        self._client = OpenAI(api_key=api_key, base_url=DASHSCOPE_BASE_URL)
        logger.info("API 客户端初始化成功，模型=%s", self.model_name)

    def _init_local_model(self) -> None:
        """初始化本地模型（待实现）。"""
        raise ModelError("本地模式待实现，当前请使用 mode='api'")

    def generate(self, image: Image.Image, prompt: str) -> str:
        """把截图与指令发给模型，返回模型生成的文本响应。

        Args:
            image: PIL.Image 对象（屏幕截图）。
            prompt: 用户指令与系统提示词拼接后的文本。

        Returns:
            模型生成的文本响应。

        Raises:
            ModelError: 重试多次仍失败时抛出。
        """
        if self.mode == "api":
            return self._generate_api(image, prompt)
        return self._generate_local(image, prompt)

    def _generate_api(self, image: Image.Image, prompt: str) -> str:
        """API 模式：上传图片 + 文本，调用千问 VL 模型，失败重试最多 3 次。"""
        b64 = _image_to_base64(image)
        last_error = None

        for attempt in range(1, MAX_RETRY + 1):
            try:
                completion = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{b64}"
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                )
                result = completion.choices[0].message.content
                logger.info("模型调用成功（第 %d 次尝试）", attempt)
                return result
            except Exception as e:
                last_error = e
                logger.warning("模型调用第 %d 次失败：%s", attempt, e)
                time.sleep(1)  # 失败后稍等再重试

        logger.error("模型调用重试 %d 次后仍失败", MAX_RETRY)
        raise ModelError(f"模型调用失败（已重试{MAX_RETRY}次）：{last_error}")

    def _generate_local(self, image: Image.Image, prompt: str) -> str:
        """本地模式推理（待实现）。"""
        raise ModelError("本地模式待实现")


# 直接运行本文件：截一张图，让模型描述屏幕上看到了什么
if __name__ == "__main__":
    from perception.screenshot import capture_screen

    print("正在截图...")
    img = capture_screen()

    print("正在请模型分析屏幕（请稍候，需联网）...")
    client = ModelClient(mode="api")
    answer = client.generate(img, "请简要描述这张屏幕截图上你看到了什么内容。")

    print("\n===== 模型的回答 =====")
    print(answer)
    print("======================")
    print("\n如果上面出现了对你屏幕内容的描述，说明 4.3.1 模型调用接口验证通过！")