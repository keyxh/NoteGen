# Markdown编辑器

一个功能丰富的Markdown编辑器，支持AI助手和历史记录，使用Python后端和HTML5前端，通过WebView显示。

## 功能特点

- 实时Markdown预览
- 文档历史记录查看
- AI助手集成（支持OpenAI API）
- 本地数据存储（SQLite）
- 响应式界面设计
- 自动保存功能
- 资源本地化（无需外部CDN）

## 安装与运行

### 环境要求

- Python 3.7+
- pip

### 安装步骤

1. 克隆或下载项目到本地
2. 进入项目目录
3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
4. 运行应用：
   ```
   python main.py
   ```

### 打包应用

项目提供了打包脚本，可以将应用打包为可分发的压缩包：

```
python package.py
```

打包完成后，会在`dist`目录生成可分发的应用文件，以及压缩包文件。

## 使用说明

### 基本功能

1. **新建文档**：点击左侧边栏的"新建文档"按钮
2. **编辑文档**：在左侧编辑器中输入Markdown内容，右侧会实时预览
3. **保存文档**：点击顶部工具栏的"保存"按钮，或等待自动保存
4. **查看历史**：点击"历史记录"按钮查看文档的历史版本

### AI助手

1. **配置AI**：点击"设置"按钮，配置OpenAI API信息
   - API Key：你的OpenAI API密钥
   - Base URL：API基础URL（默认为腾讯混元API）
   - Model：使用的模型名称（默认为hunyuan-lite）

2. **使用AI助手**：
   - 在编辑器中输入`/`键快速打开AI对话
   - 在右侧AI助手面板中输入问题或指令
   - AI可以根据当前文档内容提供帮助

### 快捷键

- `/`：在编辑器中快速打开AI对话
- `Ctrl/Cmd + S`：保存当前文档

## 技术架构

### 后端

- **框架**：Flask
- **数据库**：SQLite
- **AI集成**：OpenAI API
- **WebView**：PyWebView

### 前端

- **技术**：HTML5, CSS3, JavaScript
- **样式**：自定义CSS + GitHub Markdown样式
- **预览**：服务端Markdown渲染

## 配置说明

### 默认AI配置

应用默认使用腾讯混元API：

```json
{
    "api_key": "sk-P8Cm1QYbS0mRPDRl7yCUI0SXC12QQn12BWK0QSnnTo4SWwPc",
    "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
    "model": "hunyuan-lite"
}
```

### 自定义配置

你可以在设置中修改AI配置，支持任何兼容OpenAI API格式的服务。

## 开发说明

### 项目结构

```
mdEditor/
├── backend/           # 后端代码
│   ├── app.py        # Flask应用主文件
│   ├── config.py     # 配置文件
│   ├── database.py   # 数据库管理
│   ├── ai_service.py # AI服务
│   └── config_manager.py # 配置管理
├── static/           # 静态资源
│   ├── css/          # 样式文件
│   └── js/           # JavaScript文件
├── templates/        # HTML模板
├── data/            # 数据存储目录
├── main.py          # 应用入口
├── requirements.txt # Python依赖
├── package.py       # 打包脚本
└── README.md        # 项目说明
```

### 扩展开发

1. **添加新功能**：在`backend/app.py`中添加新的API端点
2. **修改UI**：在`static/css`和`static/js`中修改前端代码
3. **数据库变更**：在`backend/database.py`中修改数据库结构

## 常见问题

### Q: AI助手无法使用？

A: 请检查API配置是否正确，确保API Key有效，网络连接正常。

### Q: 文档无法保存？

A: 请检查`data`目录是否有写入权限，确保应用有足够的存储空间。

### Q: 预览显示异常？

A: 请确保浏览器支持现代CSS特性，或者尝试刷新页面。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！