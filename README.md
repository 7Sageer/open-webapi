# Open WebAPI

这是一个简单的API代理服务，用于转发请求到Open WebUI API服务。该代理提供了兼容OpenAI API格式的接口，允许客户端使用标准的OpenAI API调用方式与Open WebUI进行交互。

> ⚠️特别提醒：如果您的组织使用Open WebUI且您不理解这个项目的用途，请务必不要使用这个项目，你可能会无意间白嫖了您的组织资源！

## 功能特性

- 支持OpenAI兼容的API路由：`/v1/chat/completions`和`/v1/models`
- 支持流式响应（streaming）
- 内置重试机制和错误处理
- 通过API密钥进行身份验证

## 环境变量

启动服务前需要设置以下环境变量：

- `OPENWEBUI_BASE_URL`: OpenWebUI服务的基础URL
- `OPENWEBUI_API_KEY`: 用于访问OpenWebUI的API密钥
- `API_KEY`: 此代理服务的API密钥，用于验证客户端请求

## 部署方法

### 使用Docker

1. 构建Docker镜像:

```bash
docker build -t openwebapi .
```

2. 运行容器:

```bash
docker run -p 3001:3001 \
  -e OPENWEBUI_BASE_URL="https://your-openwebui-instance.com" \
  -e OPENWEBUI_API_KEY="your-openwebui-api-key" \
  -e API_KEY="your-proxy-api-key" \
  openwebapi
```

### 直接运行

1. 安装依赖:

```bash
pip install -r requirements.txt
```

2. 设置环境变量:

```bash
export OPENWEBUI_BASE_URL="https://your-openwebui-instance.com"
export OPENWEBUI_API_KEY="your-openwebui-api-key"
export API_KEY="your-proxy-api-key"
```

3. 启动服务:

```bash
python app.py
```

## 使用方法

服务启动后，可以像使用OpenAI API一样使用此代理：

```bash
curl http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-proxy-api-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## 限制与注意事项

- 只支持基础OpenAI API端点
- 需要有效的OpenWebUI实例和API密钥
- 默认在3001端口运行

## 免责声明

- 本项目仅供学习和研究目的，不得用于商业用途
