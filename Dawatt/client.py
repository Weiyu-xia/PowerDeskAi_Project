import re
import requests


def Call_Dawatt(chat_history):
    url = "http://192.168.210.128:1060/v1/chat/completions"
    params = {
        "model": "Megawatt_13b",
        "messages": chat_history,
        "max_tokens": 2048,
        "presence_penalty": 1.1,
        "temperature": 0.5,
        "stream": True
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, json=params, stream=True, headers=headers)
    words = ""
    for chunk in response.iter_content(1024):
        chunk = chunk.decode('utf-8', 'ignore')
        if chunk:
            token_list = re.findall(r'"content":"(.*?)"', chunk, re.DOTALL)
            content = "".join(token_list)
            content = content.replace("\\n", "<br>")
            print(content, end="")  # 实时打印输出
            yield f"{content}"  # 流式输出到前端
    #         words += "".join(token_list)
    #
    # # 将 \n 替换为 <br>
    # words = words.replace("\\n", "<br>")
    # return words

