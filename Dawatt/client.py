import json
import requests
import time
import uuid  # 导入 UUID 模块

# 定义一个全局变量来存储 conversation_id
conversation_id = None

# 定义一个重置 conversation_id 的方法
def reset_conversation_id():
    global conversation_id
    conversation_id = None
    print("会话已重置为新的会话")

def generate_conversation_id():
    """
    发送一条初始消息“你好”，从模型响应中提取 conversation_id 并保存。
    """
    global conversation_id

    # API URL
    api_url = "https://api.dify.ai/v1/chat-messages"
    api_key = "app-EU8DZ6Erz8VvUb55jcH8sfsI"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 初始请求体，发送固定的 "你好" 消息
    request_body = {
        "inputs": {},
        "query": "你好",  # 发送初始消息
        "response_mode": "streaming",
        "conversation_id": None,  # 第一次会话没有 conversation_id
        "user": "abc-123",
    }

    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=request_body, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        partial_data = ""
        for line in response.iter_lines():
            if line:
                event_data = line.decode('utf-8').strip()
                if event_data.startswith("data: "):
                    json_data = event_data[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        event_type = parsed_data.get("event")

                        if event_type == "message":
                            partial_data += parsed_data["answer"]  # 收集大模型的回复内容

                        # 提取 conversation_id 并存储
                        if "conversation_id" in parsed_data:
                            conversation_id = parsed_data["conversation_id"]
                            print(f"新会话ID: {conversation_id}")
                            return conversation_id  # 返回新的 conversation_id

                        elif event_type == "message_end":
                            print("\n对话结束")

                    except json.JSONDecodeError:
                        print("JSON 解析错误:", json_data)
                else:
                    print("接收到非数据行:", event_data)
    else:
        print(f"请求失败，状态码: {response.status_code}, 原因: {response.text}")
        return None

def Call_Dawatt(user_input, conv_id=None):
    global conversation_id  # 声明全局变量
    if conv_id is not None:
        conversation_id = conv_id  # 更新全局的 conversation_id
        print(f"切换到新的会话ID: {conversation_id}")
    else:
        print(f"当前会话ID: {conversation_id if conversation_id else '新会话开始'}")
    # 定义 API URL
    api_url = "https://api.dify.ai/v1/chat-messages"  # 目标 API 地址

    # API Key
    api_key = "app-EU8DZ6Erz8VvUb55jcH8sfsI"

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {api_key}',  # 替换为你的实际 API 密钥
        'Content-Type': 'application/json'
    }

    # 构建请求体
    request_body = {
        "inputs": {},  # 允许传入 App 定义的各变量值
        "query": user_input,  # 用户提问内容
        "response_mode": "streaming",  # 使用流式模式
        "conversation_id": conversation_id,  # 使用传入的会话ID
        "user": "abc-123",  # 用户标识
    }

    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=request_body, stream=True)

    # 检查响应状态
    if response.status_code == 200:
        # 处理流式返回数据
        for line in response.iter_lines():
            if line:
                event_data = line.decode('utf-8').strip()
                if event_data.startswith("data: "):
                    json_data = event_data[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        event_type = parsed_data.get("event")

                        if event_type == "message":
                            answer = parsed_data["answer"]
                            for char in answer:
                                print(char, end="", flush=True)
                                yield char
                                time.sleep(0.1)

                        # 提取 conversation_id 并存储
                        if "conversation_id" in parsed_data:
                            conversation_id = parsed_data["conversation_id"]

                        elif event_type == "message_end":
                            print("\n")

                    except json.JSONDecodeError:
                        print("JSON 解析错误:", json_data)
                else:
                    print("接收到非数据行:", event_data)
    else:
        print(f"请求失败，状态码: {response.status_code}, 原因: {response.text}")
