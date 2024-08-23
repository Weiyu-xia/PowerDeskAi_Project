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

    // 发送用户输入和历史记录到服务器
    fetch('/DawattChat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ chat_history: chatHistory })
    })
    .then(response => response.json())
    .then(data => {
        displayReply(data.reply);
        // 将大模型的回复添加到聊天记录
        chatHistory.push({ role: 'assistant', content: data.reply });
    })
    .catch(error => console.error('Error:', error));
});

// 逐字显示函数
function displayReply(reply) {
    const delay = 50; // 延迟时间，单位是毫秒
    appendMessage('大瓦特', '');

    const replyDiv = chatBox.lastElementChild.querySelector('.reply-content');

    let index = 0;
    (function type() {
        if (index < reply.length) {
            replyDiv.innerHTML += reply.charAt(index++);
            setTimeout(type, delay);
        } else {
            chatBox.scrollTop = chatBox.scrollHeight; // 滚动到聊天框底部
        }
    })();
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



