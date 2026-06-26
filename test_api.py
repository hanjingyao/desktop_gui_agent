import os
from openai import OpenAI

# 从环境变量读取 API Key，不在代码里写死密钥
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-vl-plus",   # 多模态视觉模型，能看图
    messages=[
        {"role": "user", "content": "你好，请回复一句话确认API连接成功"}
    ],
)

print(completion.choices[0].message.content)
print("API 连接成功！")