import os, json
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

tools = [{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "현재 날짜와 시각을 반환한다",
        "parameters": {"type": "object", "properties": {}}
    }
}]

messages = [{"role": "user", "content": "지금 몇 시야?"}]

response = client.chat.completions.create(
    model="openrouter/free", messages=messages, tools=tools
)

msg = response.choices[0].message
print(msg.tool_calls)

tool_call = msg.tool_calls[0]
print(tool_call.function.name)

if tool_call.function.name == "get_time":
    result = get_time()
    print(result)

    messages.append(msg)
    messages.append({
        "role": "tool",
        "tool_call_id": "tool_call.id",
        "content": result
    })

    final = client.chat.completions.create(
        model = "openrouter/free",
        messages = messages,
        tools = tools
    )

    print(final.choices[0].message.content)