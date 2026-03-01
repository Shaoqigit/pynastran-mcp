# Cherry Studio 使用教程

## 🍒 简介

本教程介绍如何在 **Cherry Studio** 中配置和使用 pyNastran MCP Server。

## 🚀 快速开始

### 1. 安装

```bash
pip install pynastran-mcp
```

### 2. 配置 Cherry Studio

打开 Cherry Studio → 设置 → MCP 服务器 → 添加服务器

```json
{
  "name": "pyNastran",
  "command": "pynastran-mcp"
}
```

### 3. 开始使用

在对话中输入：

```
读取这个模型 /path/to/your/model.bdf
```

## 💬 常用命令

### 读取模型
```
读取 BDF 文件 /path/to/model.bdf
```

### 检查质量
```
检查网格质量 /path/to/model.bdf
```

### 读取结果
```
读取 OP2 结果 /path/to/results.op2
```

## 🌐 高级用法：SSE 模式

如需 HTTP 接口，使用 SSE 模式：

```bash
pynastran-mcp --transport sse --port 8080
```

然后在 Cherry Studio 配置：

```json
{
  "name": "pyNastran-SSE",
  "url": "http://localhost:8080/sse"
}
```

## 📝 更多文档

- [快速上手](CHERRY_STUDIO_QUICKSTART.md)
- [架构说明](ARCHITECTURE.md)
