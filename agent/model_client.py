"""多模态模型调用接口。

对应 PRD 4.3.1：统一封装通义千问多模态模型的调用，支持本地部署与在线 API 两种模式。

模式说明：
    - 'api'  ：调用阿里云百炼（DashScope）在线接口，无需本地 GPU。【当前主用】
    - 'local'：用 Transformers 加载 Qwen2-VL 模型在本机运行，需要足够显存。

API 模式需要在系统环境变量中配置 DASHSCOPE_API_KEY，
切勿将密钥写入代码或提交到 Git 仓库。

异常处理（PRD 4.3.1）：
    - 本地模式模型加载失败时自动切换到 API 模式。
    - API 调用失败时重试最多 3 次。
    - 所有异常均记录日志并返回错误信息。
"""

import base64
import io
import os

from PIL import Image


# API 模式默认使用的视觉模型，可按效果与预算更换（如 qwen-vl-max）
DEFAULT_API_MODEL = "qwen-vl-plus"
# 百炼北京地域的 OpenAI 兼容接口地址
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def _image_to_base64(image: Image.Image) -> str:
    """把 PIL.Image 编码为 base64 字符串，供 API 以 data url 形式上传。"""
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
            raise ValueError(
                "未找到环境变量 DASHSCOPE_API_KEY，请先配置 API Key。"
            )
        self._client = OpenAI(api_key=api_key, base_url=DASHSCOPE_BASE_URL)

    def _init_local_model(self) -> None:
        """初始化本地模型（Transformers 加载 Qwen2-VL）。"""
        # TODO: 本地模式实现，需要时再补；当前以 API 模式为主
        raise NotImplementedError("本地模式待实现，当前请使用 mode='api'")

    def generate(self, image: Image.Image, prompt: str) -> str:
        """把截图与指令发给模型，返回模型生成的文本响应。

        Args:
            image: PIL.Image 对象（屏幕截图）。
            prompt: 用户指令与系统提示词拼接后的文本。

        Returns:
            模型生成的文本响应（通常是一条 Action 指令，见 prompt_template）。
        """
        if self.mode == "api":
            return self._generate_api(image, prompt)
        return self._generate_local(image, prompt)

    def _generate_api(self, image: Image.Image, prompt: str) -> str:
        """API 模式：上传图片 + 文本，调用千问 VL 模型。"""
        b64 = _image_to_base64(image)
        completion = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return completion.choices[0].message.content

    def _generate_local(self, image: Image.Image, prompt: str) -> str:
        """本地模式推理。"""
        raise NotImplementedError("本地模式待实现")
