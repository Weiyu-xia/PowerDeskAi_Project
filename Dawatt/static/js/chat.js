// 获取表单和聊天框元素
const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const welcomeScreen = document.getElementById('welcome-screen');  // 欢迎界面元素
const chatScreen = document.getElementById('chat-screen');        // 聊天界面元素
const newConversationButton = document.getElementById('new-conversation');

let chatHistory = [];

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

function fetchMessageId(userInput, conversationId) {
    // 调用后端获取 message_id 的接口
    const url = `/get_message_id/?user_input=${encodeURIComponent(userInput)}&conversation_id=${conversationId}`;

    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message_id) {
                console.log('Retrieved message_id:', data.message_id); // 调试输出
                return data.message_id;
            } else {
                console.error('Failed to retrieve message_id:', data);
                return null;
            }
        })
        .catch(error => {
            console.error('Error fetching message_id:', error);
            return null;
        });
}

// 表单提交事件处理
form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const userInput = document.getElementById('user_input').value.trim();
    if (!userInput) return;
    // 确保使用当前的会话ID
    const currentConvID = window.currentConversationID || null;  // 如果没有会话ID则传递 null

    // 将用户输入添加到聊天记录
    chatHistory.push({role: 'user', content: userInput});
    // 将用户输入添加到聊天框
    appendMessage('用户', userInput);
    // 清空用户输入框
    document.getElementById('user_input').value = '';

    try {
        // 调用获取 message_id 的接口
        const messageId = await fetchMessageId(userInput, currentConvID);

        if (messageId) {
            // 调用获取下一轮建议问题的接口
            fetchSuggestedQuestions(messageId);
        }
    } catch (error) {
        console.error('Error handling message submission:', error);
    }

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
                reader.read().then(({done, value}) => {
                    if (done) {
                        chatHistory.push({role: 'assistant', content: partialData});
                        return;
                    }

                    // 处理流式传输的数据
                    partialData += decoder.decode(value, {stream: true});
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
        body: JSON.stringify({chat_history: chatHistory})
    })
        .then(response => response.json())  // 解析JSON响应
        .then(data => {
            console.log("情绪识别返回数据: ", data);  // 调试输出
            // 获取情绪识别结果
            let emotionLabel = data.emotion_label;

            // 判断情绪结果，并设置页面显示的情绪
            let emotionText = '';
            if (emotionLabel === "1") {
                emotionText = '正面';
            } else if (emotionLabel === "0") {
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

function fetchSuggestedQuestions(messageID) {
    const url = `/messages/${messageID}/suggested?user=abc-123`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.result === 'success' && Array.isArray(data.data)) {
                appendSuggestedQuestions(data.data);
            } else {
                console.error('Failed to fetch suggested questions:', data);
            }
        })
        .catch(error => console.error('Error fetching suggested questions:', error));
}

function appendSuggestedQuestions(questions) {
    // 调试输出建议问题列表
    console.log('Appending suggested questions:', questions);

    // 生成建议问题的按钮 HTML
    const suggestionsHtml = questions.map(q => `
        <button class="btn btn-sm btn-outline-secondary m-1 suggested-question">${q}</button>
    `).join('');

    // 创建包含建议问题的容器
    const suggestionDiv = document.createElement('div');
    suggestionDiv.classList.add('suggested-questions', 'mt-2');
    suggestionDiv.innerHTML = `
        <div>
            ${suggestionsHtml}
        </div>
    `;

    // 找到最近生成的回复气泡
    const lastReplyContent = chatBox.querySelector('.reply-content.bg-primary'); // 大瓦特的回复气泡

    if (lastReplyContent) {
        // 将建议问题插入到回复气泡的后面
        lastReplyContent.parentElement.insertAdjacentElement('afterend', suggestionDiv);
    } else {
        console.warn('No AI reply found to append suggestions.');
    }

    // 将建议问题容器添加到聊天框中
    chatBox.appendChild(suggestionDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // 滚动到底部

    // 为每个按钮绑定点击事件
    suggestionDiv.querySelectorAll('.suggested-question').forEach(button => {
        button.addEventListener('click', function () {
            const question = this.textContent; // 获取按钮的文本内容
            document.getElementById('user_input').value = question; // 将问题填入输入框
        });
    });
}

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 解析并转换Markdown标记
function parseMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 加粗
        .replace(/__(.*?)__/g, '<u>$1</u>')               // 下划线
        .replace(/``(.*?)``/g, '<code>$1</code>')         // 代码块
        .replace(/\n/g, '<br>');                          // 换行
}

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

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

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

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

    // 添加消息到聊天框1
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('border', 'rounded', 'p-2', 'mb-2');
        messageElement.innerHTML = `<strong>${sender}：</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // 保持滚动条在底部
    }
});

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 等待文档加载完成后再执行
document.addEventListener('DOMContentLoaded', function () {

    // 获取所有常见问题按钮
    const commonQuestionButtons = document.querySelectorAll('.common-question');
    const userInput = document.getElementById('user_input');
    const chatForm = document.getElementById('chat-form');

    // 为每个按钮添加点击事件
    commonQuestionButtons.forEach(button => {
        button.addEventListener('click', function () {
            // 获取按钮上的问题内容
            const question = this.getAttribute('data-value');
            // 将内容填入输入框
            userInput.value = question;
        });
    });
});

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 点击会话列表项时获取聊天记录并切换会话 ID
document.getElementById('conversation-list').addEventListener('click', function (e) {
    if (e.target && e.target.matches('li.conversation-item')) {
        // 获取 li 的 data-id 属性作为 conversationID
        let conversationID = e.target.getAttribute('data-id');
        window.currentConversationID = conversationID;  // 将会话ID存储为全局变量

        //隐藏欢迎界面，显示聊天界面
        document.getElementById('welcome-screen').classList.add('d-none');
        document.getElementById('chat-screen').classList.remove('d-none');

        fetch(`/messages/?conversation_id=${conversationID}&user=abc-123&limit=20`)
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
        // 显示用户的 query
        appendMessage('用户', item.query);

        // 显示 AI 的 answer，如果存在的话
        if (item.answer) {
            appendMessage('大瓦特', item.answer);
        }
    });
}

// 添加消息到聊天框2
function appendMessage(sender, message) {
    const messageClass = sender === '用户'
        ? 'bg-success text-white'  // 将用户消息的背景颜色改为绿色（Bootstrap 类 bg-success）
        : 'bg-primary text-white';  // 大瓦特的消息仍为蓝色

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


// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

document.addEventListener('DOMContentLoaded', function () {
    // 页面加载时获取会话列表
    fetchConversations();

    // 点击“新会话”按钮时重置会话并新增到会话列表
    newConversationButton.addEventListener('click', function () {
        // 显示聊天界面，隐藏欢迎界面
        welcomeScreen.classList.add('d-none');
        chatScreen.classList.remove('d-none');

        // 发送请求到后端重置 conversation_id 并创建新会话
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
                    appendConversationToList(data.conversation_id, `New Chat`);
                } else {
                    console.error('无法重置会话');
                }
            })
            .catch(error => console.error('Error:', error));
    });
});

// 获取会话列表
function fetchConversations() {
    fetch(`/conversations?user=abc-123&limit=20`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                renderConversationList(data.data);  // 渲染会话列表
            }
        })
        .catch(error => console.error('Error:', error));
}

// 渲染会话列表
function renderConversationList(conversations) {
    const conversationList = document.getElementById('conversation-list');
    conversationList.innerHTML = '';  // 清空会话列表

    conversations.forEach(conversation => {
        appendConversationToList(conversation.id, conversation.name);
    });
}

// 在会话列表中添加会话项
function appendConversationToList(conversationID, conversationName) {
    const conversationList = document.getElementById('conversation-list');

    // 使用 data-id 存储会话的唯一 ID
    const li = document.createElement('li');
    li.classList.add('conversation-item', 'd-flex', 'justify-content-between', 'align-items-center');
    li.setAttribute('data-id', conversationID);  // 存储会话ID

    // 设置会话名称和操作按钮
    li.innerHTML = `
        <span class="conversation-text"> ${conversationName}</span>
        <div class="button-group">
            <button class="btn btn-sm btn-danger delete-conversation" title="删除">
                <i class="fas fa-trash-alt"></i>
            </button>
            <button class="btn btn-sm btn-secondary rename-conversation" title="重命名">
                <i class="fas fa-edit"></i>
            </button>
        </div>
    `;

    conversationList.appendChild(li);

    // 绑定删除和重命名事件
    bindActionEvents(li);
}

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 绑定删除和重命名事件
function bindActionEvents(conversationItem) {
    const deleteBtn = conversationItem.querySelector('.delete-conversation');
    const renameBtn = conversationItem.querySelector('.rename-conversation');

    // 删除按钮点击事件
    deleteBtn.addEventListener('click', function () {
        const conversationID = conversationItem.getAttribute('data-id');
        // 删除操作
        fetch(`/delete_conversation/${conversationID}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(response => {
                if (response.ok) {
                    conversationItem.remove();  // 成功删除会话项
                } else {
                    console.error('Failed to delete conversation');
                }
            })
            .catch(error => console.error('Error:', error));
    });

    // 重命名按钮点击事件
    renameBtn.addEventListener('click', function () {
        const conversationItem = this.closest('li');  // 获取当前会话项的 li
        const conversationID = conversationItem.getAttribute('data-id');
        const newName = prompt("请输入新的会话名称：");

        console.log("用户输入的新会话名称:", newName);  // 调试信息，查看用户输入

        if (newName && newName.trim()) {
            // 发送重命名请求
            fetch(`/rename_conversation/${conversationID}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    name: newName.trim(),  // 手动设置的名称
                    auto_generate: 'false',  // 禁用自动生成
                    user: 'abc-123'  // 假设用户ID固定为'abc-123'
                })
            })
                .then(response => {
                    if (response.ok) {
                        conversationItem.querySelector('span').innerHTML = `<i class="fas fa-comment-alt"></i> ${newName}`;
                        console.log('会话已成功重命名');
                    } else {
                        console.error('重命名会话失败');
                    }
                })
                .catch(error => console.error('Error:', error));
        } else {
            console.log("请输入有效的会话名称");
        }
    });

}

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 获取按钮和加载动画的DOM元素
const generateTicketButton = document.getElementById('generate-ticket');
const loadingOverlay = document.createElement('div');

// 设置加载动画的样式
loadingOverlay.innerHTML = `
    <div class="loading-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 9999; display: flex; justify-content: center; align-items: center;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
        </div>
    </div>
`;
loadingOverlay.style.display = 'none';  // 初始隐藏
document.body.appendChild(loadingOverlay);

// 隐藏聊天界面，显示工单摘要界面
generateTicketButton.addEventListener('click', function() {
    const conversationID = window.currentConversationID || null;  // 确保有会话ID
    if (!conversationID) {
        alert("请先选择或创建一个会话。");
        return;
    }

    // 显示加载动画
    loadingOverlay.style.display = 'flex';

    // 调用后端获取聊天记录
    fetch(`/messages/?conversation_id=${conversationID}&limit=50`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                loadingOverlay.style.display = 'none';  // 出错时隐藏加载动画
            } else {
                // 提取聊天记录，格式化为示例格式
                const chatHistoryFormatted = data.data.map(item =>
                    `user:${item.query}, assistant:${item.answer}`
                );

                // 调用后端生成工单摘要
                fetch('/generate_ticket/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ chat_history: chatHistoryFormatted })
                })
                .then(response => response.json())
                .then(ticketData => {
                    if (ticketData.error) {
                        console.error(ticketData.error);
                    } else {
                        // 显示工单摘要
                        const cleanSummary = ticketData.summary.replace(/```html/g, '').replace(/```/g, '');
                        document.getElementById('ticket-summary').innerHTML = `
                            <p><strong>工单内容：</strong> ${cleanSummary}</p>`;
                        // 隐藏聊天界面，显示工单窗口
                        document.getElementById('chat-screen').classList.add('d-none');
                        document.getElementById('ticket-screen').classList.remove('d-none');
                    }
                    // 隐藏加载动画
                    loadingOverlay.style.display = 'none';
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingOverlay.style.display = 'none';  // 出错时隐藏加载动画
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingOverlay.style.display = 'none';  // 出错时隐藏加载动画
        });
});

document.getElementById('back-to-chat').addEventListener('click', function() {
    // 返回聊天界面，隐藏工单摘要界面
    document.getElementById('ticket-screen').classList.add('d-none');
    document.getElementById('chat-screen').classList.remove('d-none');
});

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

// 添加语音按钮和事件
const startRecordingBtn = document.getElementById('start-recording');  // 录音按钮
const stopRecordingBtn = document.getElementById('stop-recording');    // 停止录音按钮
const userInput = document.getElementById('user_input');               // 输入框

let mediaRecorder;
let socket;
let audioChunks = [];

startRecordingBtn.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

    // 启动 WebSocket 连接
    socket = new WebSocket('ws://0.0.0.0:8001');

    socket.onopen = () => {
        console.log('WebSocket connected for voice recognition');
    };

    // 当收到 WebSocket 传回的识别结果时，将其填入输入框
    socket.onmessage = (event) => {
        const recognizedText = event.data;
        console.log('Voice recognition result:', recognizedText);

        // 将识别结果填入输入框，等待用户确认
        userInput.value = recognizedText;
    };

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];

        // 将音频数据发送到 WebSocket
        const reader = new FileReader();
        reader.readAsArrayBuffer(audioBlob);
        reader.onloadend = () => {
            socket.send(reader.result);
        };
    };

    mediaRecorder.start();
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = false;
});

stopRecordingBtn.addEventListener('click', () => {
    mediaRecorder.stop();
    startRecordingBtn.disabled = false;
    stopRecordingBtn.disabled = true;
});

// —————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
// 上传文件事件
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const uploadFileButton = document.getElementById('upload-file-btn');
    const fileInput = document.getElementById('file-input');
    const submitButton = form.querySelector('button[type="submit"]');

    // 绑定文件上传按钮事件
    uploadFileButton.addEventListener('click', function () {
        // 打开文件选择框
        fileInput.click();
    });

    // 监听文件选择事件
    fileInput.addEventListener('change', function () {
        const file = fileInput.files[0];
        if (file) {
            // 上传文件
            const formData = new FormData();
            formData.append('file', file);
            formData.append('user', 'abc-123'); // 假设用户ID是 'abc-123'

            fetch('/upload_file/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.result === 'success') {
                    alert('文件上传成功');
                    console.log('上传的文件信息:', data.file);
                } else {
                    console.error('文件上传失败', data.error);
                }
            })
            .catch(error => console.error('错误:', error));
        }
    });
});

