// 获取表单和聊天框元素
const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');

// 表单提交事件处理
form.addEventListener('submit', function(event) {
    event.preventDefault(); // 阻止默认表单提交行为

    const userInput = document.getElementById('user_input').value.trim();
    if (!userInput) return; // 确保用户输入不为空

    // 将用户输入添加到聊天框
    appendMessage('用户', userInput);

    // 清空用户输入框
    document.getElementById('user_input').value = '';

    // 发送用户输入到服务器
    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => displayReply(data.reply))
    .catch(error => console.error('Error:', error));
});

// 逐字显示函数
function displayReply(reply) {
    const delay = 50; // 延迟时间，单位是毫秒
    appendMessage('大瓦特', '');

    const replyDiv = chatBox.lastElementChild.querySelector('.reply-content');
    reply = reply.replace(/<br>/g, "\n");

    let index = 0;
    (function type() {
        if (index < reply.length) {
            replyDiv.textContent += reply.charAt(index++);
            setTimeout(type, delay);
        } else {
            chatBox.scrollTop = chatBox.scrollHeight; // 滚动到聊天框底部
        }
    })();
}

// 添加消息到聊天框
function appendMessage(sender, message) {
    // 使用颜色类区分用户与大瓦特的聊天框
    const messageClass = sender === '用户'
        ? 'bg-primary text-white'
        : 'bg-light text-dark';

    const messageHtml = `
        <div class="d-flex ${sender === '用户' ? 'justify-content-end' : 'justify-content-start'} mb-2">
            <div>
                <strong>${sender}:</strong>
                <div class="reply-content p-2 rounded ${messageClass}" style="max-width: 500px;">${message}</div>
            </div>
        </div>
    `;
    chatBox.insertAdjacentHTML('beforeend', messageHtml);
    chatBox.scrollTop = chatBox.scrollHeight; // 滚动到聊天框底部
}

