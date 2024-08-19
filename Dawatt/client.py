import re
import requests


# 大瓦特接口文档 —— 流式输出
def Call_Dawatt(user_input):
    headers = {"Content-type": "application/json"}
    url = "http://192.168.210.128:1030/v1/chat/completions"

    # 提示词：请求模型将对话生成一个简明的工单摘要
    prompt = f"请根据以下对话生成一个工单摘要：\n\n{user_input}\n\n要求总结为简洁的工单任务描述。"

    params = {
        "model": "Megawatt_13b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2048,
        "presence_penalty": 1.1,
        "temperature": 0.5,
        "stream": True
    }

    response = requests.post(url=url, json=params, headers=headers, stream=True)
    words = ""
    for chunk in response.iter_lines():
        if chunk:
            token_list = re.findall(r'"content":"(.*?)"', chunk.decode('utf-8'), re.DOTALL)
            words += "".join(token_list)

    print("generate result: {}".format(words))
    return words


Call_Dawatt("介绍一下南方电网")
