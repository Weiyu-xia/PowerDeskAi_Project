import re
import requests


def Call_Dawatt_history(chat_history):
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
    response = requests.post(url=url, json=params, headers=headers)

    words = ""
    for chunk in response.iter_lines():
        if chunk:
            chunk_str = chunk.decode('utf-8')  # 将字节对象转换为字符串
            token_list = re.findall(r'"content":"(.*?)"', chunk_str, re.DOTALL)
            words += "".join(token_list)

    # 将 \n 替换为 <br>
    words = words.replace("\\n", "<br>")
    return words



def generate_sql(query):
    # 调用大模型生成SQL查询语句
    chat_history = [{"role": "system", "content": "请生成一个对应的SQL查询语句：" + query}]
    return Call_Dawatt_history(chat_history)

def Print_Dawatt(chat_history):
    # 将聊天记录转换为格式化字符串
    formatted_history = ""
    for message in chat_history:
        role = '用户' if message['role'] == 'user' else '大瓦特'
        content = message['content']
        formatted_history += f"{role}: {content}；"

    # 输出格式化的聊天记录到控制台
    print('Formatted Chat History:', formatted_history)
