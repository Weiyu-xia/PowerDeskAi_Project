import re
import requests


# 大瓦特接口文档 —— 流式输出
def Call_Dawatt(user_input):
    headers = {"Content-type": "application/json"}
    url = "http://192.168.210.128:1030/v1/chat/completions"

    params = {
        "model": "Megawatt_13b",
        "messages": [
            {
                "role": "user",
                "content": user_input
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


Call_Dawatt("介绍一下南方电网")
