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

    // 获取大瓦特的对话内容（流式传输）
    fetch('/DawattChat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let partialData = '';

        // 逐字显示大模型的回复
        appendMessage('大瓦特', '');

        const replyDiv = chatBox.lastElementChild.querySelector('.reply-content');

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    chatHistory.push({ role: 'assistant', content: partialData });
                    return;
                }

                // 处理流式传输的数据
                partialData += decoder.decode(value, { stream: true });
                replyDiv.innerHTML = parseMarkdown(partialData);
                chatBox.scrollTop = chatBox.scrollHeight;

                readStream();
            }).catch(error => console.error('Error:', error));
        }

        readStream();
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
         console.log("情绪识别返回数据: ", data);  // 调试输出
        // 获取情绪识别结果
        let emotionLabel = data.emotion_label;

        // 判断情绪结果，并设置页面显示的情绪
        let emotionText = '';
        if (emotionLabel === 1) {
            emotionText = '正面';
        } else if (emotionLabel === 0) {
            emotionText = '负面';
        } else {
            emotionText = '平静';  // 处理其他未知情绪标签
        }
        // 更新情绪识别结果显示区域
        const emotionDiv = document.getElementById('emotion-label');
        emotionDiv.innerHTML = `情绪识别结果：${emotionText}`;
    })
    .catch(error => console.error('Error:', error));

});

// 解析并转换Markdown标记
function parseMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 加粗
        .replace(/__(.*?)__/g, '<u>$1</u>')               // 下划线
        .replace(/``(.*?)``/g, '<code>$1</code>')         // 代码块
        .replace(/\n/g, '<br>');                          // 换行
}

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



//优化界面
document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user_input');

    // 处理表单提交
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = userInput.value.trim();

        if (userMessage) {
            appendMessage('用户', userMessage);
            userInput.value = ''; // 清空输入框
            // 模拟响应
            setTimeout(function () {
                appendMessage('客服', '收到您的消息！');
            }, 1000);
        }
    });

    // 添加消息到聊天框
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('border', 'rounded', 'p-2', 'mb-2');
        messageElement.innerHTML = `<strong>${sender}：</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // 保持滚动条在底部
    }
});

