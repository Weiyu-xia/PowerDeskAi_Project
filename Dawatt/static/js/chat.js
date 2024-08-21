// 获取表单和聊天框元素
        const form = document.getElementById('chat-form');
        const chatBox = document.getElementById('chat-box');

        // 表单提交事件处理
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // 阻止默认表单提交行为

            const userInput = document.getElementById('user_input').value;
            if (userInput.trim() === '') return; // 确保用户输入不为空

            // 将用户输入添加到聊天框
            chatBox.innerHTML += `<div><strong>用户:</strong></div>`;
            chatBox.innerHTML += `<div>${userInput}</div>`;

            // 清空用户输入框
            document.getElementById('user_input').value = '';

            // 发送用户输入到服务器，调用 Call_Dawatt 方法
            fetch('/api/chat/', { // 根路径
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ user_input: userInput })
            })
            .then(response => response.json())
            .then(data => {
                const reply = data.reply; // 根据 JSON 响应字段调整
                // 将模型回复逐字显示
                displayReply(reply);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });

        // 逐字显示函数
        function displayReply(reply) {
            const delay = 50; // 延迟时间，单位是毫秒
            let index = 0;
            chatBox.innerHTML += `<div><strong>大瓦特:</strong></div>`;
            const replyDiv = document.createElement('div');
            replyDiv.className = 'reply-content';
            chatBox.appendChild(replyDiv);

            // 替换 <br> 为换行符
            reply = reply.replace(/<br>/g, "\n");

            function type() {
                if (index < reply.length) {
                    replyDiv.innerHTML += reply.charAt(index);
                    index++;
                    setTimeout(type, delay);
                } else {
                    chatBox.scrollTop = chatBox.scrollHeight; // 滚动到聊天框底部
                }
            }
            type(); // 启动逐字显示
        }