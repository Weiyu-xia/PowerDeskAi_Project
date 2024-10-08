// 获取表单和聊天框元素
const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const welcomeScreen = document.getElementById('welcome-screen');  // 欢迎界面元素
const chatScreen = document.getElementById('chat-screen');        // 聊天界面元素
const newConversationButton = document.getElementById('new-conversation');

let chatHistory = [];


// 表单提交事件处理
form.addEventListener('submit', function(event) {
    event.preventDefault();
    const userInput = document.getElementById('user_input').value.trim();
    if (!userInput) return;
    // 确保使用当前的会话ID
    const currentConvID = window.currentConversationID || null;  // 如果没有会话ID则传递 null

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
        body: JSON.stringify({
            user_input: userInput,
            conversation_id: currentConvID  // 发送当前会话ID
        })
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



// 等待文档加载完成后再执行
document.addEventListener('DOMContentLoaded', function () {

    // 获取所有常见问题按钮
    const commonQuestionButtons = document.querySelectorAll('.common-question');
    const userInput = document.getElementById('user_input');
    const chatForm = document.getElementById('chat-form');

    // 为每个按钮添加点击事件
    commonQuestionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 获取按钮上的问题内容
            const question = this.getAttribute('data-value');
            // 将内容填入输入框
            userInput.value = question;
        });
    });
});



// 点击“新会话”按钮时
newConversationButton.addEventListener('click', function() {
    // 显示聊天界面，隐藏欢迎界面
    welcomeScreen.classList.add('d-none');
    chatScreen.classList.remove('d-none');

    // 发送一个请求到后端重置 conversation_id
    fetch('/DawattChat/new-conversation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === '会话已重置') {
            console.log('会话已重置');
            window.currentConversationID = data.conversation_id; // 存储新的会话 ID
            chatHistory = []; // 清空聊天记录
            document.getElementById('chat-box').innerHTML = '';  // 清空聊天界面

            // 在侧边栏新增会话条目
            const newSessionItem = document.createElement('li');
            newSessionItem.classList.add('list-group-item', 'conversation-item');
            newSessionItem.innerHTML = `<i class="fas fa-comment-alt"></i> ${data.conversation_id}`;
            document.getElementById('conversation-list').appendChild(newSessionItem);
        } else {
            console.error('无法重置会话');
        }
    })
    .catch(error => console.error('Error:', error));
});


// 点击会话列表项时获取聊天记录并切换会话 ID
document.getElementById('conversation-list').addEventListener('click', function(e) {
    if (e.target && e.target.matches('li.conversation-item')) {
        let conversationID = e.target.textContent.trim();
        window.currentConversationID = conversationID;  // 将会话ID存储为全局变量

        fetch(`/messages/?conversation_id=${conversationID}&limit=20`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                } else {
                    renderChatHistory(data.data);  // 渲染聊天历史
                }
            })
            .catch(error => console.error('Error:', error));
    }
});

function renderChatHistory(history) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';  // 清空聊天框
    history.forEach(item => {
        appendMessage(item.belongs_to === 'user' ? '用户' : '大瓦特', item.query || item.answer);
    });
}

