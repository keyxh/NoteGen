/**
 * AI助手模块
 * 负责处理与AI交互相关的所有功能
 */
class AIAssistant {
    constructor(app) {
        this.app = app; // 主应用实例的引用
        this.aiSidebarVisible = true;
        this.pendingAIResponse = null; // 存储待处理的AI响应
        this.aiMode = 'chat'; // AI模式：'chat' 或 'edit'
        
        // DOM元素引用
        this.aiSidebar = null;
        this.toggleAiBtn = null;
        this.aiModeToggleBtn = null;
        this.aiMessages = null;
        this.aiInput = null;
        this.sendAiBtn = null;
        
        this.init();
    }
    
    /**
     * 初始化AI助手
     */
    init() {
        // 获取DOM元素引用
        this.aiSidebar = document.getElementById('ai-sidebar');
        this.toggleAiBtn = document.getElementById('toggle-ai-btn');
        this.aiModeToggleBtn = document.getElementById('ai-mode-toggle');
        this.aiMessages = document.getElementById('ai-messages');
        this.aiInput = document.getElementById('ai-input');
        this.sendAiBtn = document.getElementById('send-ai-btn');
        
        // 初始化UI
        this.updateAIModeUI();
        
        // 绑定事件
        this.bindEvents();
    }
    
    /**
     * 绑定事件处理器
     */
    bindEvents() {
        // AI助手切换按钮
        if (this.toggleAiBtn) {
            this.toggleAiBtn.addEventListener('click', () => this.toggleAISidebar());
        }
        
        // AI模式切换按钮
        if (this.aiModeToggleBtn) {
            this.aiModeToggleBtn.addEventListener('click', () => this.toggleAIMode());
        }
        
        // 发送AI消息按钮
        if (this.sendAiBtn) {
            this.sendAiBtn.addEventListener('click', () => this.sendAIMessage());
        }
        
        // AI输入框事件
        if (this.aiInput) {
            this.aiInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendAIMessage();
                }
            });
        }
    }
    
    /**
     * 切换AI模式（对话/编辑）
     */
    toggleAIMode() {
        this.aiMode = this.aiMode === 'chat' ? 'edit' : 'chat';
        this.updateAIModeUI();
        this.app.showMessage(`已切换到${this.aiMode === 'chat' ? '对话' : '编辑'}模式`, 'info');
    }
    
    /**
     * 更新AI模式UI
     */
    updateAIModeUI() {
        const modeText = this.aiMode === 'chat' ? '切换到编辑模式' : '切换到对话模式';
        if (this.aiModeToggleBtn) {
            this.aiModeToggleBtn.textContent = modeText;
        }
        
        // 清空输入框
        if (this.aiInput) {
            this.aiInput.value = '';
        }
        
        // 显示模式切换消息
        this.addAIMessage(`当前为${this.aiMode === 'chat' ? '对话' : '编辑'}模式`, 'system');
    }
    
    /**
     * 切换AI助手侧边栏
     */
    toggleAISidebar() {
        this.aiSidebarVisible = !this.aiSidebarVisible;
        if (this.aiSidebar) {
            this.aiSidebar.classList.toggle('hidden', !this.aiSidebarVisible);
        }
        
        // 更新机器人图标
        const aiToggleIcon = document.getElementById('ai-toggle-icon');
        if (aiToggleIcon) {
            aiToggleIcon.textContent = this.aiSidebarVisible ? '🤖' : '🤖‍📝';
        }
    }
    
    /**
     * 发送AI消息
     */
    async sendAIMessage() {
        const message = this.aiInput.value.trim();
        if (!message) return;
        
        // 添加用户消息
        this.addAIMessage(message, 'user');
        this.aiInput.value = '';
        
        // 显示加载中消息
        const loadingId = this.addAIMessage('AI正在思考中...', 'assistant');
        
        try {
            let response;
            
            if (this.aiMode === 'chat') {
                // 对话模式：发送消息和当前文档内容
                const currentContent = this.app.editor.getValue();
                response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        context: currentContent
                    })
                });
            } else {
                // 编辑模式：发送编辑指令
                const currentContent = this.app.editor.getValue();
                console.log('发送编辑请求:', message);
                response = await fetch('/api/edit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        context: currentContent
                    })
                });
            }
            
            // 检查响应状态
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
            }
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // 如果不是JSON，可能是HTML错误页面
                const text = await response.text();
                console.error('服务器返回非JSON响应:', text.substring(0, 200));
                throw new Error('服务器返回了非预期的响应格式');
            }
            
            const data = await response.json();
            console.log('AI响应:', data);
            
            // 移除加载中消息
            this.removeAIMessage(loadingId);
            
            if (data.success) {
                if (this.aiMode === 'chat') {
                    // 对话模式：显示回复
                    this.addAIMessage(data.response, 'assistant');
                } else {
                    // 编辑模式：显示编辑选项
                    console.log('显示编辑选项:', data.response);
                    this.addAIResponseWithActions(data.response);
                }
            } else {
                this.addAIMessage(`错误: ${data.error}`, 'assistant');
            }
        } catch (error) {
            console.error('AI请求失败:', error);
            this.removeAIMessage(loadingId);
            this.addAIMessage(`请求失败: ${error.message}`, 'assistant');
        }
    }
    
    /**
     * 添加AI响应和操作按钮
     */
    addAIResponseWithActions(message) {
        // 创建消息容器
        const messageContainer = document.createElement('div');
        messageContainer.className = 'ai-message-container';
        
        // 创建消息元素
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ai-message assistant';
        
        // 创建预览区域，显示Markdown原始内容
        const previewDiv = document.createElement('div');
        previewDiv.className = 'ai-message-preview';
        previewDiv.style.whiteSpace = 'pre-wrap';
        previewDiv.style.fontFamily = 'monospace';
        previewDiv.style.backgroundColor = '#f6f8fa';
        previewDiv.style.padding = '10px';
        previewDiv.style.borderRadius = '4px';
        previewDiv.style.marginBottom = '10px';
        previewDiv.style.maxHeight = '200px';
        previewDiv.style.overflow = 'auto';
        previewDiv.textContent = message;
        
        messageDiv.appendChild(previewDiv);
        
        // 创建操作按钮容器
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ai-message-actions';
        actionsDiv.style.display = 'flex';
        actionsDiv.style.gap = '10px';
        actionsDiv.style.marginTop = '10px';
        
        // 创建保留按钮
        const keepBtn = document.createElement('button');
        keepBtn.textContent = '保留';
        keepBtn.className = 'btn btn-small btn-primary';
        keepBtn.addEventListener('click', () => {
            this.applyAIResponse(message);
            messageContainer.remove();
        });
        
        // 创建舍弃按钮
        const discardBtn = document.createElement('button');
        discardBtn.textContent = '舍弃';
        discardBtn.className = 'btn btn-small btn-secondary';
        discardBtn.addEventListener('click', () => {
            messageContainer.remove();
        });
        
        // 创建插入到光标位置按钮
        const insertBtn = document.createElement('button');
        insertBtn.textContent = '插入到光标位置';
        insertBtn.className = 'btn btn-small btn-info';
        insertBtn.addEventListener('click', () => {
            this.insertAIResponseAtCursor(message);
            messageContainer.remove();
        });
        
        actionsDiv.appendChild(keepBtn);
        actionsDiv.appendChild(insertBtn);
        actionsDiv.appendChild(discardBtn);
        
        messageContainer.appendChild(messageDiv);
        messageContainer.appendChild(actionsDiv);
        
        this.aiMessages.appendChild(messageContainer);
        this.aiMessages.scrollTop = this.aiMessages.scrollHeight;
    }
    
    /**
     * 应用AI响应到编辑器
     */
    applyAIResponse(message) {
        this.app.editor.setValue(message);
        this.app.updatePreview();
        this.app.startAutoSave();
        this.app.showMessage('已应用AI生成的内容', 'success');
    }
    
    /**
     * 在光标位置插入AI响应
     */
    insertAIResponseAtCursor(message) {
        // 确保编辑器获得焦点
        this.app.editor.focus();
        
        // 在当前光标位置插入内容
        this.app.editor.replaceSelection(message);
        
        // 更新预览和自动保存
        this.app.updatePreview();
        this.app.startAutoSave();
        this.app.showMessage('已插入AI生成的内容到光标位置', 'success');
    }
    
    /**
     * 添加AI消息
     */
    addAIMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${type}`;
        messageDiv.textContent = message;
        
        const messageId = Date.now().toString();
        messageDiv.dataset.id = messageId;
        
        this.aiMessages.appendChild(messageDiv);
        this.aiMessages.scrollTop = this.aiMessages.scrollHeight;
        
        return messageId;
    }
    
    /**
     * 移除AI消息
     */
    removeAIMessage(messageId) {
        const message = this.aiMessages.querySelector(`[data-id="${messageId}"]`);
        if (message) {
            message.remove();
        }
    }
    
    /**
     * 激活AI对话（通过"/"键触发）
     */
    activateAIChat() {
        if (this.aiInput) {
            this.aiInput.focus();
            this.aiInput.value = '';
            this.app.showMessage('已切换到AI对话模式，输入您的问题后按Enter发送', 'info');
        }
    }
    
    /**
     * 测试API连接
     */
    async testAPIConnection() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                return { success: true, message: 'API连接成功', data: data.config };
            } else {
                return { success: false, message: 'API连接失败', error: data.error };
            }
        } catch (error) {
            return { success: false, message: 'API连接错误', error: error.message };
        }
    }
    
    /**
     * 测试AI对话功能
     */
    async testAIChat(message) {
        if (!message) {
            return { success: false, message: '请输入测试消息' };
        }
        
        try {
            // 检查响应状态
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: ''
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
            }
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // 如果不是JSON，可能是HTML错误页面
                const text = await response.text();
                console.error('服务器返回非JSON响应:', text.substring(0, 200));
                throw new Error('服务器返回了非预期的响应格式');
            }
            
            const data = await response.json();
            
            if (data.success) {
                return { success: true, message: 'AI对话成功', response: data.response };
            } else {
                return { success: false, message: 'AI对话失败', error: data.error };
            }
        } catch (error) {
            return { success: false, message: 'AI对话错误', error: error.message };
        }
    }
    
    /**
     * 测试AI编辑功能
     */
    async testAIEdit(instruction, content) {
        if (!instruction) {
            return { success: false, message: '请输入编辑指令' };
        }
        
        try {
            // 检查响应状态
            const response = await fetch('/api/edit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: instruction,
                    context: content || ''
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
            }
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // 如果不是JSON，可能是HTML错误页面
                const text = await response.text();
                console.error('服务器返回非JSON响应:', text.substring(0, 200));
                throw new Error('服务器返回了非预期的响应格式');
            }
            
            const data = await response.json();
            
            if (data.success) {
                return { success: true, message: 'AI编辑成功', response: data.response };
            } else {
                return { success: false, message: 'AI编辑失败', error: data.error };
            }
        } catch (error) {
            return { success: false, message: 'AI编辑错误', error: error.message };
        }
    }
}