import openai

client = openai.OpenAI(
    api_key="sk-0f7f1821377c4de3ae1bf166175673b6",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.chat.completions.create(
    model="qwen3-max",  # 你可以替换为其他模型，如qwen-max
    messages=[{"role": "user", "content": "Hello, world!"}],
)

print(response.choices[0].message.content)
s