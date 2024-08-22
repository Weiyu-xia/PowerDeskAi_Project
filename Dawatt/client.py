import re
import requests


def Call_Dawatt(chat_history):
    url = "http://192.168.210.128:1030/v1/chat/completions"
    params = {
        "model": "Megawatt_13b",
        "messages": chat_history,
        "max_tokens": 2048,
        "presence_penalty": 1.1,
        "temperature": 0.5,
        "stream": True
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, json=params, headers=headers)

    words = ""
    for chunk in response.iter_lines():
        if chunk:
            chunk_str = chunk.decode('utf-8')  # 将字节对象转换为字符串
            token_list = re.findall(r'"content":"(.*?)"', chunk_str, re.DOTALL)
            words += "".join(token_list)
    return words
