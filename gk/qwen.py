from openai import OpenAI

client = OpenAI(
	base_url="https://router.huggingface.co/novita",
	api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxx"
)

messages = [
	{
		"role": "user",
		"content": "What is the capital of France?"
	}
]

stream = client.chat.completions.create(
    model="qwen/qwen-2.5-72b-instruct", 
	messages=messages, 
	max_tokens=500,
	stream=True
)

for chunk in stream:
	print(chunk.choices[0].delta.content, end="")