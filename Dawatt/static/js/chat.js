// 获取表单和聊天框元素
const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');

let chatHistory = [];

// 表单提交事件处理
form.addEventListener('submit', function(event) {
    event.preventDefault();
    const userInput = document.getElementById('user_input').value.trim();
    if (!userInput) return;
    // 将用户输入添加到聊天记录
    chatHistory.push({ role: 'user', content: userInput });
    // 将用户输入添加到聊天框
    appendMessage('用户', userInput);
    // 清空用户输入框
    document.getElementById('user_input').value = '';

    // 发送用户输入和历史记录到服务器并流式接收大模型的输出
    fetch('/DawattChat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ chat_history: chatHistory })
    })
    .then(response => {if (!response.ok) {throw new Error('Network response was not ok');}

        // 逐字显示大模型的回复
        appendMessage('大瓦特', '');

    })
    .catch(error => console.error('Error:', error));


    // 第二个请求：获取情绪识别结果
    fetch('/DawattChat/emotion/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ chat_history: chatHistory })
    })
    .then(response => response.json())  // 解析JSON响应
    .then(data => {
        console.log("情绪识别返回数据: ", data);
        // 更新情绪识别结果显示区域
        const emotionDiv = document.getElementById('emotion-label');
        emotionDiv.innerHTML = `情绪识别结果：${data.emotion_label}`;
    })
    .catch(error => console.error('Error:', error));

});

// 添加消息到聊天框
function appendMessage(sender, message) {
    const messageClass = sender === '用户'
        ? 'bg-light text-dark'
        : 'bg-primary text-white';

    const avatarSrc = sender === '用户'
        ? '/static/images/User.png'
        : '/static/images/AI.png';

    const messageHtml = `
        <div class="d-flex ${sender === '用户' ? 'justify-content-end' : 'justify-content-start'} mb-2 align-items-start">
            ${sender === '用户' ? '' : `<img src="${avatarSrc}" alt="${sender} Avatar" class="rounded-circle me-2" style="width: 40px; height: 40px;">`}
            <div>
                <strong>${sender}:</strong>
                <div class="reply-content p-2 rounded ${messageClass}" style="max-width: 400px;">${message}</div>
            </div>
            ${sender === '用户' ? `<img src="${avatarSrc}" alt="${sender} Avatar" class="rounded-circle ms-2" style="width: 40px; height: 40px;">` : ''}
        </div>
    `;
    chatBox.insertAdjacentHTML('beforeend', messageHtml);
    chatBox.scrollTop = chatBox.scrollHeight;
}
