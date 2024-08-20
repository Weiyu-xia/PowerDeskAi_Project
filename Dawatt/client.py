import re
import time
import requests


# 大瓦特接口文档 —— 流式输出
def Call_Dawatt(user_input):
    headers = {'Content-Type': 'application/json;charset=utf-8', 'Accept-Encoding': 'utf-8'}
    url = "http://192.168.210.128:1030/v1/chat/completions"

    # 提示词：请求模型将对话生成一个简明的工单摘要
    prompt = f"""
    请根据以下内容执行相应的操作：
    - 如果内容是与电力故障相关的工单信息，请生成一个简明的工单摘要，格式如下：
    摘要关键信息：
    业务类型
    业务子类
    停电时间
    自查情况（若有）
    用户号码
    用户地址
    用户称呼
    摘要：
    客户反馈
    跟进情况
    用户称呼
    用户号码
    用户地址
    
    - 如果内容是一个日常问题，请根据上下文尽可能详细地回答问题。

    内容：\n\n{user_input}
    """

    is_stream = True

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
        "stream": is_stream
    }

    print("-" * 100)
    print(">>> ", user_input)
    start_time = time.time()

    response = requests.post(url=url, json=params, headers=headers, stream=is_stream)
    words = ""

    if is_stream:
        # 流式输出处理
        for chunk in response.iter_content(1024):
            token_list = re.findall(r'(?<=\"content\":\").*?(?=\"},)', chunk.decode("utf-8", "ignore"), re.DOTALL)
            print("".join(token_list), end="")
            words += "".join(token_list)
    else:
        # 非流式输出处理
        for chunk in response.iter_lines(1024):
            token_list = re.findall(r'(?<=\"content\":\").*?(?=\"},)', chunk.decode("utf-8", "ignore"), re.DOTALL)
            words += "".join(token_list)
            print(words)

    end_time = time.time()
    print("\n>>> Time cost: %s" % round(end_time - start_time, 4))

    # 将 \n 替换为 <br>
    words = words.replace("\\n", "<br>")

    return words