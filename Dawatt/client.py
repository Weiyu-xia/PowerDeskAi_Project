import json
import requests
import time  # 导入时间模块

def Call_Dawatt(chat_history):  # 添加一个 delay 参数，单位为秒
    # 定义 API URL
    api_url = "https://api.dify.ai/v1/chat-messages"  # 目标 API 地址

    # API Key
    api_key = "app-UbvRHc53mtaKn740Ht5SU9aD"

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {api_key}',  # 替换为你的实际 API 密钥
        'Content-Type': 'application/json'
    }

    # 构建请求体
    request_body = {
        "inputs": {},  # 允许传入 App 定义的各变量值
        "query": chat_history,  # 用户提问内容
        "response_mode": "streaming",  # 使用流式模式
        "conversation_id": "",  # （可选）会话 ID
        "user": "abc-123",  # 用户标识
    }

    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=request_body, stream=True)

    # 检查响应状态
    if response.status_code == 200:
        # print("请求成功，开始处理流式返回数据...")  # 调试信息
        # 处理流式返回数据
        for line in response.iter_lines():
            if line:
                # 解析流式块
                event_data = line.decode('utf-8').strip()
                if event_data.startswith("data: "):
                    # 提取 JSON 数据
                    json_data = event_data[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        event_type = parsed_data.get("event")

                        if event_type == "message":
                            # 实时输出到控制台
                            answer = parsed_data["answer"]

                            # 控制逐字输出
                            for char in answer:
                                print(char, end="", flush=True)  # 控制台逐字输出
                                yield char  # 流式输出到前端
                                time.sleep(0.1)  # 添加延迟

                        elif event_type == "message_end":
                            print("\n")

                    except json.JSONDecodeError:
                        print("JSON 解析错误:", json_data)
                else:
                    print("接收到非数据行:", event_data)  # 输出非数据行的内容
    else:
        print(f"请求失败，状态码: {response.status_code}, 原因: {response.text}")
