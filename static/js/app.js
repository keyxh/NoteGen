// Markdown编辑器应用
class MarkdownEditor {
    constructor() {
        this.currentDocumentId = null;
        this.documents = [];
        this.autoSaveTimer = null;
        
        this.initElements();
        this.bindEvents();
        this.initializePanelSizes(); // 初始化面板大小
        this.loadDocuments();
        this.loadConfig();
    }
    
    // 初始化面板大小
    initializePanelSizes() {
        // 确保编辑器和预览区能够正确填充容器
        const editorPanel = document.getElementById('editor-panel');
        const previewPanel = document.getElementById('preview-panel');
        const editorContainer = document.querySelector('.editor-container');
        
        if (editorPanel && previewPanel && editorContainer) {
            // 设置容器高度
            const toolbarHeight = document.querySelector('.toolbar').offsetHeight;
            const docTitleHeight = document.querySelector('.doc-title').offsetHeight;
            const totalHeight = toolbarHeight + docTitleHeight;
            
            editorContainer.style.height = `calc(100vh - ${totalHeight}px)`;
            
            // 确保CodeMirror编辑器正确初始化大小
            setTimeout(() => {
                this.editor.refresh();
            }, 100);
        }
    }
    
    // 初始化DOM元素
    initElements() {
        // 初始化CodeMirror编辑器
        const editorElement = document.getElementById('markdown-editor');
        this.editor = CodeMirror.fromTextArea(editorElement, {
            mode: 'markdown',
            lineNumbers: true,
            lineWrapping: true,
            autofocus: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            showCursorWhenSelecting: true,
            theme: 'default',
            extraKeys: {
                "Ctrl-B": "insertBold",
                "Cmd-B": "insertBold",
                "Ctrl-I": "insertItalic",
                "Cmd-I": "insertItalic",
                "Ctrl-K": "insertLink",
                "Cmd-K": "insertLink",
                "Ctrl-Shift-C": "insertInlineCode",
                "Cmd-Shift-C": "insertInlineCode",
                "Ctrl-Shift-Alt-C": "insertCodeBlock",
                "Cmd-Shift-Alt-C": "insertCodeBlock",
                "Ctrl-G": "insertImage",
                "Cmd-G": "insertImage",
                "Ctrl-Alt-1": "insertHeader1",
                "Cmd-Alt-1": "insertHeader1",
                "Ctrl-Alt-2": "insertHeader2",
                "Cmd-Alt-2": "insertHeader2",
                "Ctrl-Alt-3": "insertHeader3",
                "Cmd-Alt-3": "insertHeader3",
                "Ctrl-Alt-U": "insertUnorderedList",
                "Cmd-Alt-U": "insertUnorderedList",
                "Ctrl-Alt-O": "insertOrderedList",
                "Cmd-Alt-O": "insertOrderedList",
                "Ctrl-Alt-Q": "insertBlockquote",
                "Cmd-Alt-Q": "insertBlockquote",
                "Ctrl-Alt-T": "insertTable",
                "Cmd-Alt-T": "insertTable",
                "Ctrl-Alt-R": "insertHorizontalRule",
                "Cmd-Alt-R": "insertHorizontalRule",
                "Ctrl-S": () => this.saveCurrentDocument(),
                "Cmd-S": () => this.saveCurrentDocument(),
                "Ctrl-F": "findPersistent",
                "Cmd-F": "findPersistent"
            }
        });

        // 初始化工具栏
        this.initToolbar();
        
        // 文档相关
        this.documentList = document.getElementById('document-list');
        this.newDocBtn = document.getElementById('new-doc-btn');
        this.docTitle = document.getElementById('doc-title');
        this.saveBtn = document.getElementById('save-btn');
        this.historyBtn = document.getElementById('history-btn');
        
        // 侧边栏切换
        this.sidebar = document.getElementById('sidebar');
        this.toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
        this.sidebarToggleIcon = document.getElementById('sidebar-toggle-icon');
        
        // 编辑器相关
        this.markdownEditor = this.editor;
        this.markdownPreview = document.getElementById('markdown-preview');
        this.previewPanel = document.getElementById('preview-panel');
        this.togglePreviewBtn = document.getElementById('toggle-preview-btn');
        
        // 设置相关
        this.settingsBtn = document.getElementById('settings-btn');
        this.aboutBtn = document.getElementById('about-btn');
        this.settingsModal = document.getElementById('settings-modal');
        this.historyModal = document.getElementById('history-modal');
        
        // 模态框
        this.modals = document.querySelectorAll('.modal');
        this.modalCloses = document.querySelectorAll('.modal-close');
    }
    
    // 初始化工具栏
    initToolbar() {
        // 绑定工具栏按钮事件
        const toolbarButtons = {
            'btn-bold': 'insertBold',
            'btn-italic': 'insertItalic',
            'btn-strikethrough': 'insertStrikethrough',
            'btn-h1': 'insertHeader1',
            'btn-h2': 'insertHeader2',
            'btn-h3': 'insertHeader3',
            'btn-link': 'insertLink',
            'btn-image': 'insertImage',
            'btn-code': 'insertInlineCode',
            'btn-codeblock': 'insertCodeBlock',
            'btn-ul': 'insertUnorderedList',
            'btn-ol': 'insertOrderedList',
            'btn-quote': 'insertBlockquote',
            'btn-table': 'insertTable',
            'btn-hr': 'insertHorizontalRule'
        };

        Object.keys(toolbarButtons).forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => {
                    this.editor.execCommand(toolbarButtons[btnId]);
                });
            }
        });
    }
    
    // 绑定事件
    bindEvents() {
        // 文档相关事件
        if (this.newDocBtn) {
            this.newDocBtn.addEventListener('click', () => this.createNewDocument());
        }
        if (this.saveBtn) {
            this.saveBtn.addEventListener('click', () => this.saveCurrentDocument());
        }
        if (this.historyBtn) {
            this.historyBtn.addEventListener('click', () => this.showHistory());
        }
        
        // 侧边栏切换事件
        if (this.toggleSidebarBtn) {
            this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        }
        
        // 编辑器事件
        if (this.editor) {
            this.editor.on('change', () => {
                this.updatePreview();
                this.startAutoSave();
            });
            
            // 检测"/"键触发AI对话
            this.editor.on('keydown', (instance, e) => {
                // 当编辑器为空且按下"/"键时，触发AI对话
                if (e.key === '/' && this.editor.getSelection() === '') {
                    e.preventDefault();
                    // 使用AI助手实例的方法
                    if (this.aiAssistant) {
                        this.aiAssistant.activateAIChat();
                    }
                }
            });
        }
        
        if (this.docTitle) {
            this.docTitle.addEventListener('input', () => {
                this.startAutoSave();
            });
        }
        
        // 预览切换
        if (this.togglePreviewBtn) {
            this.togglePreviewBtn.addEventListener('click', () => this.togglePreview());
        }
        
        // 设置和关于按钮
        if (this.settingsBtn) {
            this.settingsBtn.addEventListener('click', () => this.showSettings());
        }
        if (this.aboutBtn) {
            this.aboutBtn.addEventListener('click', () => this.showAbout());
        }
        
        // 模态框关闭事件
        this.modalCloses.forEach(close => {
            close.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.hideModal(modal.id);
                }
            });
        });
        
        // 点击模态框外部关闭
        this.modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
        
        // 可调整大小的分隔条
        this.initResizableSeparator();
        
        // 图片上传
        this.initImageUpload();
        
        // 导出功能
        this.initExport();
    }
    
    // 初始化可调整大小的分隔条
    initResizableSeparator() {
        const separator = document.getElementById('resize-separator');
        const editorPanel = document.getElementById('editor-panel');
        const previewPanel = document.getElementById('preview-panel');
        
        if (!separator || !editorPanel || !previewPanel) return;
        
        let isResizing = false;
        
        separator.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            const container = document.querySelector('.editor-container');
            const containerRect = container.getBoundingClientRect();
            const separatorPosition = e.clientX - containerRect.left;
            const containerWidth = containerRect.width;
            
            // 计算编辑器宽度百分比（最小20%，最大80%）
            const editorWidthPercent = Math.max(20, Math.min(80, (separatorPosition / containerWidth) * 100));
            
            // 设置面板宽度
            editorPanel.style.width = `${editorWidthPercent}%`;
            editorPanel.style.flex = 'none'; // 覆盖flex属性
            previewPanel.style.width = `${100 - editorWidthPercent}%`;
            previewPanel.style.flex = 'none'; // 覆盖flex属性
            
            // 刷新编辑器
            setTimeout(() => {
                this.editor.refresh();
            }, 10);
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }
    
    // 初始化图片上传
    initImageUpload() {
        const imageUploadInput = document.getElementById('image-upload-input');
        
        imageUploadInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('image', file);
            
            try {
                const response = await fetch('/api/upload/image', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 在编辑器中插入图片链接
                    const cursor = this.editor.getCursor();
                    const imageMarkdown = `![${file.name}](${data.url})`;
                    this.editor.replaceRange(imageMarkdown, cursor);
                    this.updatePreview();
                    this.showMessage('图片上传成功', 'success');
                } else {
                    this.showMessage(`图片上传失败: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('图片上传失败:', error);
                this.showMessage('图片上传失败，请稍后再试', 'error');
            }
            
            // 清空文件输入
            e.target.value = '';
        });
    }
    
    // 初始化导出功能
    initExport() {
        const exportMdBtn = document.getElementById('export-md-btn');
        
        if (exportMdBtn) {
            exportMdBtn.addEventListener('click', () => {
                this.exportMarkdown();
            });
        }
    }
    
    // 切换侧边栏显示
    toggleSidebar() {
        const isHidden = this.sidebar.classList.contains('hidden');
        this.sidebar.classList.toggle('hidden');
        
        // 更新按钮图标
        if (this.sidebarToggleIcon) {
            this.sidebarToggleIcon.textContent = isHidden ? '📋' : '📂';
        }
        
        // 刷新编辑器，确保布局正确
        setTimeout(() => {
            this.editor.refresh();
        }, 300); // 等待过渡动画完成
    }
    
    // 切换预览显示
    togglePreview() {
        const isHidden = this.previewPanel.classList.contains('hidden');
        this.previewPanel.classList.toggle('hidden');
        
        // 更新按钮图标
        const icon = document.getElementById('preview-toggle-icon');
        if (icon) {
            icon.textContent = isHidden ? '👁️' : '👁️‍🗨️';
        }
        
        // 调整编辑器宽度
        if (isHidden) {
            // 显示预览，恢复分隔条
            document.getElementById('resize-separator').style.display = 'block';
            // 恢复编辑器宽度为初始比例（2:1）
            document.getElementById('editor-panel').style.width = '66.67%';
            document.getElementById('editor-panel').style.flex = 'none';
            document.getElementById('preview-panel').style.width = '33.33%';
            document.getElementById('preview-panel').style.flex = 'none';
        } else {
            // 隐藏预览，编辑器占满宽度
            document.getElementById('resize-separator').style.display = 'none';
            document.getElementById('editor-panel').style.width = '100%';
            document.getElementById('editor-panel').style.flex = 'none';
        }
        
        // 刷新编辑器
        setTimeout(() => {
            this.editor.refresh();
        }, 100);
    }
    
    // 更新预览
    updatePreview() {
        const content = this.editor.getValue();
        
        // 使用marked.js渲染Markdown
        const html = marked.parse(content);
        
        // 使用DOMPurify清理HTML
        const cleanHtml = DOMPurify.sanitize(html);
        
        // 更新预览区域
        this.markdownPreview.innerHTML = cleanHtml;
    }
    
    // 高亮代码块
    highlightCode() {
        // 如果有highlight.js，则使用它高亮代码
        if (typeof hljs !== 'undefined') {
            this.markdownPreview.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
    }
    
    // 创建新文档
    async createNewDocument() {
        try {
            const response = await fetch('/api/documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: '新文档',
                    content: ''
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.loadDocuments();
                this.loadDocument(data.document_id);
                this.showMessage('文档创建成功', 'success');
            } else {
                this.showMessage(`创建文档失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('创建文档失败:', error);
            this.showMessage('创建文档失败，请稍后再试', 'error');
        }
    }
    
    // 加载文档列表
    async loadDocuments() {
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();
            
            if (data.success) {
                this.documents = data.documents;
                this.renderDocumentList();
                
                // 如果没有当前文档，加载第一个文档
                if (!this.currentDocumentId && this.documents.length > 0) {
                    this.loadDocument(this.documents[0].id);
                }
            } else {
                this.showMessage(`加载文档列表失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('加载文档列表失败:', error);
            this.showMessage('加载文档列表失败，请稍后再试', 'error');
        }
    }
    
    // 渲染文档列表
    renderDocumentList() {
        if (!this.documentList) return;
        
        this.documentList.innerHTML = '';
        
        this.documents.forEach(doc => {
            const docItem = document.createElement('div');
            docItem.className = 'document-item';
            docItem.dataset.id = doc.id;
            
            const docTitle = document.createElement('div');
            docTitle.className = 'document-title';
            docTitle.textContent = doc.title;
            
            const docDate = document.createElement('div');
            docDate.className = 'document-date';
            docDate.textContent = new Date(doc.updated_at).toLocaleString();
            
            docItem.appendChild(docTitle);
            docItem.appendChild(docDate);
            
            docItem.addEventListener('click', () => {
                this.loadDocument(doc.id);
            });
            
            this.documentList.appendChild(docItem);
        });
    }
    
    // 加载文档
    async loadDocument(docId) {
        try {
            const response = await fetch(`/api/documents/${docId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentDocumentId = docId;
                this.editor.setValue(data.document.content);
                this.docTitle.value = data.document.title;
                this.updatePreview();
                
                // 更新文档列表中的选中状态
                document.querySelectorAll('.document-item').forEach(item => {
                    item.classList.toggle('active', item.dataset.id === docId.toString());
                });
            } else {
                this.showMessage(`加载文档失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('加载文档失败:', error);
            this.showMessage('加载文档失败，请稍后再试', 'error');
        }
    }
    
    // 保存当前文档
    async saveCurrentDocument() {
        if (!this.currentDocumentId) return;
        
        try {
            const response = await fetch(`/api/documents/${this.currentDocumentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: this.docTitle.value,
                    content: this.editor.getValue()
                })
            });
            
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
            
            if (data.success) {
                this.loadDocuments();
                this.showMessage('文档保存成功', 'success');
            } else {
                this.showMessage(`保存文档失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('保存文档失败:', error);
            this.showMessage(`保存文档失败: ${error.message}`, 'error');
        }
    }
    
    // 开始自动保存
    startAutoSave() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }
        
        // 30秒后自动保存
        this.autoSaveTimer = setTimeout(() => {
            this.saveCurrentDocument();
        }, 30000);
    }
    
    // 显示历史记录
    async showHistory() {
        if (!this.currentDocumentId) {
            this.showMessage('请先选择一个文档', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/documents/${this.currentDocumentId}/history`);
            const data = await response.json();
            
            if (data.success) {
                this.renderHistory(data.history);
                this.showModal('history-modal');
            } else {
                this.showMessage(`加载历史记录失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
            this.showMessage('加载历史记录失败，请稍后再试', 'error');
        }
    }
    
    // 渲染历史记录
    renderHistory(history) {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;
        
        historyList.innerHTML = '';
        
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const historyDate = document.createElement('div');
            historyDate.className = 'history-date';
            historyDate.textContent = new Date(item.created_at).toLocaleString();
            
            const historyContent = document.createElement('div');
            historyContent.className = 'history-content';
            historyContent.textContent = item.content.substring(0, 100) + (item.content.length > 100 ? '...' : '');
            
            historyItem.appendChild(historyDate);
            historyItem.appendChild(historyContent);
            
            historyItem.addEventListener('click', () => {
                this.editor.setValue(item.content);
                this.updatePreview();
                this.hideModal('history-modal');
                this.showMessage('已恢复到历史版本', 'success');
            });
            
            historyList.appendChild(historyItem);
        });
    }
    
    // 显示设置
    showSettings() {
        // 获取当前配置
        fetch('/api/settings')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 填充AI配置
                    document.getElementById('api-key').value = data.settings.api_key || '';
                    document.getElementById('base-url').value = data.settings.base_url || 'https://api.openai.com/v1';
                    document.getElementById('model').value = data.settings.model || 'gpt-3.5-turbo';
                    document.getElementById('temperature').value = data.settings.temperature || 0.7;
                    document.getElementById('temperature-value').textContent = data.settings.temperature || 0.7;
                    document.getElementById('max-tokens').value = data.settings.max_tokens || 1000;
                    
                    // 填充应用配置
                    document.getElementById('app-port').value = data.settings.port || 5000;
                    document.getElementById('auto-save').checked = data.settings.auto_save !== false;
                    document.getElementById('auto-save-interval').value = data.settings.auto_save_interval || 30;
                    
                    // 填充预览配置
                    document.getElementById('preview-theme').value = data.settings.preview_theme || 'github';
                    document.getElementById('sync-scroll').checked = data.settings.sync_scroll !== false;
                    
                    this.showModal('settings-modal');
                    this.bindSettingsEvents();
                }
            })
            .catch(error => {
                console.error('获取设置失败:', error);
                this.showMessage('加载配置失败，请稍后再试', 'error');
            });
    }
    
    // 绑定设置事件
    bindSettingsEvents() {
        // 温度滑块值显示
        const temperatureSlider = document.getElementById('temperature');
        const temperatureValue = document.getElementById('temperature-value');
        
        temperatureSlider.addEventListener('input', function() {
            temperatureValue.textContent = this.value;
        });
        
        // 保存设置按钮
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            this.saveSettings();
        });
        
        // 测试连接按钮
        document.getElementById('test-connection-btn').addEventListener('click', () => {
            this.testConnection();
        });
    }
    
    // 保存设置
    async saveSettings() {
        try {
            // 收集表单数据
            const settings = {
                // AI配置
                api_key: document.getElementById('api-key').value,
                base_url: document.getElementById('base-url').value,
                model: document.getElementById('model').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: parseInt(document.getElementById('max-tokens').value),
                
                // 应用配置
                port: parseInt(document.getElementById('app-port').value),
                auto_save: document.getElementById('auto-save').checked,
                auto_save_interval: parseInt(document.getElementById('auto-save-interval').value),
                
                // 预览配置
                preview_theme: document.getElementById('preview-theme').value,
                sync_scroll: document.getElementById('sync-scroll').checked
            };
            
            // 发送设置到服务器
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('设置保存成功', 'success');
                this.hideModal('settings-modal');
                
                // 如果端口改变，提示用户重启应用
                if (data.restart_required) {
                    this.showMessage('端口已更改，请重启应用以使设置生效', 'warning');
                }
                
                // 应用预览主题
                this.applyPreviewTheme(settings.preview_theme);
            } else {
                this.showMessage(`保存设置失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('保存设置失败:', error);
            this.showMessage('保存设置失败，请稍后再试', 'error');
        }
    }
    
    // 测试AI连接
    async testConnection() {
        try {
            // 获取当前配置
            const config = {
                api_key: document.getElementById('api-key').value,
                base_url: document.getElementById('base-url').value,
                model: document.getElementById('model').value
            };
            
            // 显示测试中状态
            const testBtn = document.getElementById('test-connection-btn');
            const originalText = testBtn.textContent;
            testBtn.textContent = '测试中...';
            testBtn.disabled = true;
            
            // 发送测试请求
            const response = await fetch('/api/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            // 恢复按钮状态
            testBtn.textContent = originalText;
            testBtn.disabled = false;
            
            if (data.success) {
                this.showMessage('连接测试成功', 'success');
            } else {
                this.showMessage(`连接测试失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('连接测试失败:', error);
            this.showMessage('连接测试失败，请稍后再试', 'error');
            
            // 恢复按钮状态
            const testBtn = document.getElementById('test-connection-btn');
            testBtn.textContent = '测试连接';
            testBtn.disabled = false;
        }
    }
    
    // 应用主题
    applyTheme(theme) {
        // 这里可以实现主题切换逻辑
        console.log(`应用主题: ${theme}`);
    }
    
    // 应用预览主题
    applyPreviewTheme(theme) {
        const previewElement = document.getElementById('markdown-preview');
        if (!previewElement) return;
        
        // 移除所有可能的主题类
        previewElement.classList.remove('github-markdown', 'default-theme');
        
        // 添加新主题类
        if (theme === 'github') {
            previewElement.classList.add('github-markdown');
        } else if (theme === 'default') {
            previewElement.classList.add('default-theme');
        }
        
        // 更新预览内容以应用新主题
        this.updatePreview();
    }
    
    // 应用编辑器设置
    applyEditorSettings(config) {
        if (config.font_size) {
            this.editor.getWrapperElement().style.fontSize = `${config.font_size}px`;
        }
        
        if (config.tab_size) {
            this.editor.setOption('tabSize', config.tab_size);
        }
        
        if (config.word_wrap !== undefined) {
            this.editor.setOption('lineWrapping', config.word_wrap);
        }
        
        // 刷新编辑器
        this.editor.refresh();
    }
    
    // 加载配置
    async loadConfig() {
        try {
            // 加载合并后的配置
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.success) {
                const config = data.settings;
                
                // 应用配置
                this.applyTheme(config.theme);
                this.applyEditorSettings(config);
                
                // 应用预览主题
                if (config.preview_theme) {
                    this.applyPreviewTheme(config.preview_theme);
                }
            }
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }
    
    // 显示关于页面
    async showAbout() {
        this.showModal('about-modal');
        this.updateSystemInfo();
        this.bindAboutEvents();
    }
    
    // 更新系统信息
    async updateSystemInfo() {
        try {
            // 获取版本信息
            const versionResponse = await fetch('/api/version');
            const versionData = await versionResponse.json();
            
            if (versionData.success) {
                const versionInfo = versionData.version_info;
                document.getElementById('app-version').textContent = versionInfo.version || '未知版本';
                
                // 更新关于页面的标题
                const aboutTitle = document.querySelector('#about-modal h4');
                if (aboutTitle) {
                    aboutTitle.textContent = `Markdown 编辑器 v${versionInfo.version || '1.0.0'}`;
                }
            }
            
            // 获取日志文件信息
            const logResponse = await fetch('/api/logs');
            const logData = await logResponse.json();
            
            if (logData.success) {
                let totalSize = 0;
                logData.log_files.forEach(file => {
                    totalSize += file.size || 0;
                });
                
                // 格式化文件大小
                const formattedSize = this.formatFileSize(totalSize);
                document.getElementById('log-size').textContent = formattedSize;
            }
            
            // 计算运行时间（这里简单模拟，实际应该从服务器获取）
            const startTime = localStorage.getItem('app_start_time') || Date.now();
            const uptime = Date.now() - parseInt(startTime);
            const formattedUptime = this.formatUptime(uptime);
            document.getElementById('app-uptime').textContent = formattedUptime;
            
        } catch (error) {
            console.error('更新系统信息失败:', error);
        }
    }
    
    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 格式化运行时间
    formatUptime(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) {
            return `${days}天 ${hours % 24}小时 ${minutes % 60}分钟`;
        } else if (hours > 0) {
            return `${hours}小时 ${minutes % 60}分钟`;
        } else if (minutes > 0) {
            return `${minutes}分钟 ${seconds % 60}秒`;
        } else {
            return `${seconds}秒`;
        }
    }
    
    // 绑定关于页面事件
    bindAboutEvents() {
        // 检查更新按钮
        const checkUpdateBtn = document.getElementById('check-update-btn');
        checkUpdateBtn.onclick = () => this.checkUpdate();
        
        // 查看日志按钮
        const viewLogsBtn = document.getElementById('view-logs-btn');
        viewLogsBtn.onclick = () => this.showLogs();
        
        // 打包日志按钮
        const packLogsBtn = document.getElementById('pack-logs-btn');
        packLogsBtn.onclick = () => this.packLogs();
    }
    
    // 检查更新
    checkUpdate() {
        this.showMessage('检查更新功能暂未实现', 'info');
    }
    
    // 显示日志页面
    async showLogs() {
        this.hideModal('about-modal');
        this.showModal('logs-modal');
        
        // 加载日志文件列表
        await this.loadLogFiles();
        
        // 延迟绑定事件，确保DOM已加载
        setTimeout(() => {
            this.bindLogsEvents();
        }, 100);
    }
    
    // 加载日志文件列表
    async loadLogFiles() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            if (data.success) {
                const logFileSelect = document.getElementById('log-file-select');
                logFileSelect.innerHTML = '';
                
                data.log_files.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file.name;
                    option.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
                    logFileSelect.appendChild(option);
                });
                
                // 默认加载第一个日志文件
                if (data.log_files.length > 0) {
                    await this.loadLogContent(data.log_files[0].name);
                }
            } else {
                this.showMessage('加载日志文件列表失败', 'error');
            }
        } catch (error) {
            console.error('加载日志文件列表失败:', error);
            this.showMessage('加载日志文件列表失败', 'error');
        }
    }
    
    // 加载日志内容
    async loadLogContent(fileName, lines = 100) {
        try {
            const response = await fetch(`/api/logs/${fileName}?lines=${lines}`);
            const data = await response.json();
            
            if (data.success) {
                const logContent = document.getElementById('log-content');
                logContent.textContent = data.content;
            } else {
                this.showMessage(`加载日志内容失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('加载日志内容失败:', error);
            this.showMessage('加载日志内容失败', 'error');
        }
    }
    
    // 绑定日志页面事件
    bindLogsEvents() {
        // 日志文件选择
        const logFileSelect = document.getElementById('log-file-select');
        if (!logFileSelect) return;
        
        logFileSelect.onchange = async () => {
            const fileName = logFileSelect.value;
            if (fileName) {
                const lines = document.getElementById('log-lines-count').value;
                await this.loadLogContent(fileName, lines);
            }
        };
        
        // 刷新按钮
        const logRefreshBtn = document.getElementById('log-refresh-btn');
        if (logRefreshBtn) {
            logRefreshBtn.onclick = async () => {
                const fileName = logFileSelect.value;
                if (fileName) {
                    const lines = document.getElementById('log-lines-count').value;
                    await this.loadLogContent(fileName, lines);
                    this.showMessage('日志已刷新', 'success');
                }
            };
        }
        
        // 搜索按钮
        const logSearchBtn = document.getElementById('log-search-btn');
        if (logSearchBtn) {
            logSearchBtn.onclick = async () => {
                const keyword = document.getElementById('log-search-input').value.trim();
                const fileName = logFileSelect.value;
                
                if (!keyword) {
                    this.showMessage('请输入搜索关键词', 'warning');
                    return;
                }
                
                try {
                    const response = await fetch('/api/logs/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            keyword: keyword,
                            file_name: fileName,
                            max_results: 100
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const logContent = document.getElementById('log-content');
                        logContent.textContent = data.results.join('\n');
                        this.showMessage(`找到 ${data.total} 条匹配结果`, 'success');
                    } else {
                        this.showMessage(`搜索失败: ${data.error}`, 'error');
                    }
                } catch (error) {
                    console.error('搜索日志失败:', error);
                    this.showMessage('搜索日志失败', 'error');
                }
            };
        }
        
        // 清空日志按钮
        const logClearBtn = document.getElementById('log-clear-btn');
        if (logClearBtn) {
            logClearBtn.onclick = async () => {
                const fileName = logFileSelect.value;
                
                if (!fileName) {
                    this.showMessage('请选择要清空的日志文件', 'warning');
                    return;
                }
                
                if (!confirm(`确定要清空日志文件 "${fileName}" 吗？此操作不可撤销。`)) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/logs/clear', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            file_name: fileName
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showMessage(`日志文件 "${fileName}" 已清空`, 'success');
                        await this.loadLogContent(fileName);
                    } else {
                        this.showMessage(`清空日志失败: ${data.error}`, 'error');
                    }
                } catch (error) {
                    console.error('清空日志失败:', error);
                    this.showMessage('清空日志失败', 'error');
                }
            };
        }
        
        // 删除日志按钮
        const logDeleteBtn = document.getElementById('log-delete-btn');
        if (logDeleteBtn) {
            logDeleteBtn.onclick = async () => {
                const fileName = logFileSelect.value;
                
                if (!fileName) {
                    this.showMessage('请选择要删除的日志文件', 'warning');
                    return;
                }
                
                if (!confirm(`确定要删除日志文件 "${fileName}" 吗？此操作不可撤销。`)) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/logs/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            file_name: fileName
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showMessage(`日志文件 "${fileName}" 已删除`, 'success');
                        await this.loadLogFiles();
                    } else {
                        this.showMessage(`删除日志失败: ${data.error}`, 'error');
                    }
                } catch (error) {
                    console.error('删除日志失败:', error);
                    this.showMessage('删除日志失败', 'error');
                }
            };
        }
        
        // 打包日志按钮
        const logPackBtn = document.getElementById('log-pack-btn');
        if (logPackBtn) {
            logPackBtn.onclick = async () => {
                try {
                    const response = await fetch('/api/logs/pack', {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showMessage(`日志打包成功: ${data.message}`, 'success');
                    } else {
                        this.showMessage(`日志打包失败: ${data.error}`, 'error');
                    }
                } catch (error) {
                    console.error('打包日志失败:', error);
                    this.showMessage('打包日志失败', 'error');
                }
            };
        }
    }
    
    // 打包日志
    async packLogs() {
        try {
            const response = await fetch('/api/logs/pack', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage(`日志打包成功: ${data.message}`, 'success');
            } else {
                this.showMessage(`日志打包失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('打包日志失败:', error);
            this.showMessage('打包日志失败', 'error');
        }
    }
    
    // 导出Markdown
    exportMarkdown() {
        const content = this.editor.getValue();
        const title = this.docTitle.value || '未命名文档';
        
        // 创建Blob对象
        const blob = new Blob([content], { type: 'text/markdown' });
        
        // 创建下载链接
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title}.md`;
        
        // 触发下载
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // 释放URL对象
        URL.revokeObjectURL(url);
        
        this.showMessage('文档导出成功', 'success');
    }
    
    // 显示模态框
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'flex';
        }
    }
    
    // 隐藏模态框
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
        }
    }
    
    // 显示消息提示
    showMessage(message, type = 'info') {
        // 创建消息元素
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        // 添加到页面
        document.body.appendChild(messageDiv);
        
        // 显示动画
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            messageDiv.classList.remove('show');
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 创建主应用实例
    window.app = new MarkdownEditor();
    
    // 创建AI助手实例
    window.app.aiAssistant = new AIAssistant(window.app);
    
    // 记录应用启动时间
    localStorage.setItem('app_start_time', Date.now().toString());
});