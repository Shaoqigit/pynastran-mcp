# SSE 模式启动方法

## 快速启动

### 方法 1：使用启动脚本（推荐）

```bash
cd /path/to/your/pyNastran/pynastran-mcp
./start_sse_server.sh [PORT]

# 示例
./start_sse_server.sh 8080
```

### 方法 2：直接启动

```bash
# 默认端口 8080
pynastran-mcp --transport sse

# 指定端口
pynastran-mcp --transport sse --port 8080

# 指定主机（允许外部访问）
pynastran-mcp --transport sse --port 8080 --host 0.0.0.0
```

## 启动后验证

### 1. 检查服务状态

```bash
# 健康检查
curl http://localhost:8080/api/health

# 预期输出
{
  "status": "ok",
  "server": "pynastran-mcp",
  "version": "0.1.0"
}
```

### 2. 查看可用工具

```bash
curl http://localhost:8080/api/tools
```

### 3. 测试 BDF 读取

```bash
curl -X POST http://localhost:8080/api/bdf/read \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.bdf"}'
```

## 可用的端点

启动后，SSE MCP Server 提供以下端点：

### MCP 协议端点
- `GET /sse` - SSE 连接端点（MCP 协议）
- `POST /messages` - 消息接收端点（MCP 协议）

### REST API 端点（直接 HTTP 调用）
- `GET /api/health` - 健康检查
- `GET /api/tools` - 列出可用工具
- `POST /api/bdf/read` - 读取 BDF 文件
- `POST /api/bdf/info` - 获取模型信息
- `POST /api/bdf/quality` - 检查网格质量
- `POST /api/bdf/bounds` - 获取模型边界
- `POST /api/op2/read` - 读取 OP2 文件
- `POST /api/report` - 生成分析报告

## 后台运行

### 使用 nohup

```bash
nohup pynastran-mcp --transport sse --port 8080 > server.log 2>&1 &
echo $! > server.pid
```

### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/pynastran-mcp.service`：

```ini
[Unit]
Description=pyNastran MCP Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/pyNastran/pynastran-mcp
ExecStart=~/miniconda3/bin/pynastran-mcp --transport sse --port 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用并启动：

```bash
sudo systemctl enable pynastran-mcp
sudo systemctl start pynastran-mcp
sudo systemctl status pynastran-mcp
```

### 使用 Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY . /app
RUN pip install -e .

EXPOSE 8080

CMD ["pynastran-mcp", "--transport", "sse", "--port", "8080"]
```

构建并运行：

```bash
docker build -t pynastran-mcp .
docker run -p 8080:8080 pynastran-mcp
```

## 停止服务

### 前台运行
按 `Ctrl+C`

### 后台运行

```bash
# 如果使用 nohup
kill $(cat server.pid)

# 如果使用 systemd
sudo systemctl stop pynastran-mcp

# 查找并杀死进程
pkill -f "pynastran-mcp"
```

## 环境变量

启动前可以设置以下环境变量：

```bash
# 设置日志级别
export LOG_LEVEL=warning

# 设置模型目录
export MODELS_DIR=/path/to/your/pyNastran/models

# 启动 Server
pynastran-mcp --transport sse --port 8080
```

## 完整启动示例

### 开发环境

```bash
cd /path/to/your/pyNastran/pynastran-mcp
pip install -e .
./start_sse_server.sh 8080
```

### 生产环境

```bash
# 使用生产级 WSGI 服务器
pip install gunicorn

# 启动（需要实现 WSGI 入口）
gunicorn -w 4 -b 0.0.0.0:8080 pynastran_mcp.server:app
```

### 与 AI Agent 集成

启动 SSE Server 后，配置 AI Agent：

**AI Agent Desktop:**
```json
{
  "mcpServers": {
    "pynastran": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

**Cursor:**
```json
{
  "mcpServers": {
    "pynastran": {
      "command": "npx",
      "args": ["mcp-proxy", "http://localhost:8080/sse"]
    }
  }
}
```

**其他 MCP Client:**
直接配置 `http://localhost:8080/sse` 作为 MCP Server URL。

## 故障排除

### 端口被占用

```bash
# 检查端口占用
lsof -i :8080

# 使用其他端口
pynastran-mcp --transport sse --port 8081
```

### 权限不足

```bash
# 检查端口权限（< 1024 需要 root）
# 使用高端口号
pynastran-mcp --transport sse --port 8080
```

### 模块导入错误

```bash
# 确保在正确的目录
export PYTHONPATH=/path/to/your/pyNastran:$PYTHONPATH

# 重新安装
pip install -e /path/to/your/pyNastran/pynastran-mcp
```

## 监控和日志

### 查看日志

```bash
# 前台运行时的输出
pynastran-mcp --transport sse --port 8080

# 后台运行的日志
tail -f server.log
```

### 健康检查脚本

```bash
#!/bin/bash
# health_check.sh

if curl -s http://localhost:8080/api/health | grep -q "ok"; then
    echo "✅ Server is running"
    exit 0
else
    echo "❌ Server is down"
    exit 1
fi
```

### 自动重启脚本

```bash
#!/bin/bash
# restart_if_down.sh

if ! curl -s http://localhost:8080/api/health > /dev/null; then
    echo "$(date): Server down, restarting..."
    pkill -f "pynastran-mcp"
    sleep 2
    nohup pynastran-mcp --transport sse --port 8080 > server.log 2>&1 &
fi
```

添加到 crontab：
```bash
*/5 * * * * /path/to/your/pyNastran/pynastran-mcp/restart_if_down.sh
```
