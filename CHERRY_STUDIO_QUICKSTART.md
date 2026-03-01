# Cherry Studio + pyNastran MCP 快速上手指南

## 🚀 5 分钟快速开始

### 1️⃣ 安装

```bash
pip install pynastran-mcp
```

或者从源码安装：

```bash
git clone https://github.com/Shaoqigit/pynastran-mcp.git
cd pynastran-mcp
pip install -e .
```

### 2️⃣ 配置 Cherry Studio

打开 Cherry Studio → 设置 → MCP 服务器 → 添加服务器

**选择模式 A：stdio（推荐）**

```json
{
  "name": "pyNastran",
  "command": "pynastran-mcp",
  "args": [],
  "env": {}
}
```

**选择模式 B：SSE（HTTP）**

先启动 Server：

```bash
pynastran-mcp --transport sse --port 8080
```

再配置：

```json
{
  "name": "pyNastran-SSE",
  "url": "http://localhost:8080/sse"
}
```

### 3️⃣ 开始使用

在 Cherry Studio 对话中输入：

```
读取这个模型 /path/to/your/model.bdf
```

---

## 📚 常用命令速查

### 🔍 读取模型
```
读取 BDF 文件 /path/to/model.bdf
```

### 🔍 检查质量
```
检查网格质量 /path/to/model.bdf
```

### 🔍 获取节点
```
显示前 10 个节点的坐标 /path/to/model.bdf
```

### 🔍 获取单元
```
列出所有的 CQUAD4 单元 /path/to/model.bdf
```

### 🔍 读取结果
```
读取 OP2 结果 /path/to/results.op2
```

### 🔍 生成报告
```
生成分析报告，BDF: /path/to/model.bdf, OP2: /path/to/results.op2
```

---

## ⚡ 高级用法

### 批量分析
```
请分析以下 3 个模型并对比：
1. /path/to/model1.bdf
2. /path/to/model2.bdf
3. /path/to/model3.bdf
```

### 复杂工作流
```
请执行完整分析流程：
1. 读取 /path/to/model.bdf
2. 检查网格质量
3. 获取模型边界尺寸
4. 读取 /path/to/results.op2
5. 生成完整报告保存到 /tmp/report.txt
```

### 特定分析
```
分析这个模型的应力分布，找出应力大于 100MPa 的单元
```

---

## 🐛 常见问题

### ❌ 连接失败
```bash
# 检查安装
pynastran-mcp --help

# 检查 pyNastran 是否安装
python -c "import pyNastran; print(pyNastran.__version__)"
```

### ❌ 文件找不到
- 使用绝对路径（以 / 开头）
- 检查文件权限：`ls -la /path/to/file`

### ❌ 响应慢
- 使用 stdio 模式（比 SSE 快）
- 大文件分批处理

---

## 📖 完整文档

详细教程见：`CHERRY_STUDIO_TUTORIAL.md`
