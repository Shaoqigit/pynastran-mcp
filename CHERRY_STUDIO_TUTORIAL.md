# pyNastran MCP - Cherry Studio 使用教程

## 🍒 简介

本教程介绍如何在 **Cherry Studio** 中配置和使用 pyNastran MCP Server，让 AI 助手帮你分析 Nastran FEA 模型。

## 📋 前置要求

- 已安装 Cherry Studio（最新版）
- Python 3.10+
- pyNastran 库
- 访问 Nastran 模型文件（.bdf, .op2）

## 🚀 安装步骤

### 1. 安装 pyNastran-mcp

```bash
# 进入项目目录
cd /path/to/your/pyNastran/pynastran-mcp

# 安装
cd /path/to/your/pyNastran
pip install -e pynastran-mcp/

# 验证安装
pynastran-mcp --help
```

### 2. 选择运行模式

Cherry Studio 支持两种 MCP 连接方式：

| 模式 | 适用场景 | 稳定性 |
|-----|---------|--------|
| **stdio 模式** | 本地使用，推荐 | ⭐⭐⭐⭐⭐ |
| **SSE 模式** | 远程/网络访问 | ⭐⭐⭐⭐ |

---

## ⚙️ 配置方法

### 方法一：stdio 模式（推荐）

#### Step 1: 打开 Cherry Studio MCP 设置

1. 打开 Cherry Studio
2. 点击左下角 ⚙️ **设置**
3. 选择 **MCP 服务器**
4. 点击 **添加服务器**

#### Step 2: 填写配置

```json
{
  "name": "pyNastran",
  "command": "pynastran-mcp",
  "args": [],
  "env": {
    "PYTHONPATH": "/path/to/your/pyNastran"
  }
}
```

**配置说明：**
- `name`: 显示名称（可自定义）
- `command`: MCP Server 启动命令
- `args`: 额外参数（stdio 模式留空）
- `env`: 环境变量，指定 Python 路径

#### Step 3: 保存并测试

1. 点击 **保存**
2. 等待状态变为 🟢 **已连接**
3. 点击 **测试** 按钮验证

---

### 方法二：SSE 模式（HTTP 连接）

#### Step 1: 启动 SSE Server

在终端中启动 SSE Server：

```bash
# 方式 1：直接启动
pynastran-mcp --transport sse --port 8080

# 方式 2：使用脚本
cd /path/to/your/pyNastran/pynastran-mcp
./start_sse_server.sh 8080
```

看到以下输出表示启动成功：
```
🚀 pyNastran MCP Server running on http://localhost:8080
   SSE endpoint: http://localhost:8080/sse
   REST API endpoint: http://localhost:8080/api
```

#### Step 2: Cherry Studio 配置

在 Cherry Studio MCP 设置中添加：

```json
{
  "name": "pyNastran-SSE",
  "url": "http://localhost:8080/sse"
}
```

**注意**：SSE 模式下不要填写 `command`，直接填写 `url`。

#### Step 3: 验证连接

状态显示 🟢 **已连接** 表示成功。

---

## 💬 使用示例

### 示例 1：读取模型信息

**在 Cherry Studio 对话中输入：**

```
请读取这个 Nastran 模型并告诉我它的基本信息：
/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.bdf
```

**AI 助手会回复：**

```
已读取模型文件，基本信息如下：

📊 模型统计：
• 节点数：25
• 单元数：21
• 材料数：1
• 属性数：7

🔧 单元类型分布：
• CHEXA (六面体): 1
• CPENTA (五面体): 2
• CTETRA (四面体): 2
• CQUAD4 (四边形壳): 4
• CTRIA3 (三角形壳): 8
• CBEAM (梁): 1
• CBAR (杆): 1
• CROD (杆): 2
```

---

### 示例 2：检查网格质量

```
帮我检查这个模型的网格质量：
/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.bdf

有什么潜在问题吗？
```

**AI 回复：**

```
✅ 网格质量检查结果：

整体状况：良好
• 总单元数：21
• 高长宽比单元：0 ✅
• 退化单元：17 ⚠️

⚠️ 警告说明：
17 个退化单元都是 1D 单元（CBAR、CROD、CBEAM），
它们的面积/体积为 0 是正常现象，不影响分析。

如果是 2D/3D 单元出现零面积，则需要检查网格。
```

---

### 示例 3：提取结果数据

```
我有一个结果文件，帮我读取并显示最大位移：
/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.op2
```

**AI 回复：**

```
📁 已读取 OP2 结果文件：

📊 位移结果汇总：
• 节点数：25
• 最大位移：3.820 mm
• 最小位移：0.000 mm
• 平均位移：1.234 mm

可用结果类型：
✅ 位移 (displacements)
✅ 应力 (stress)
✅ 应变 (strain)

最大位移发生在模型的自由端，符合预期。
```

---

### 示例 4：生成分析报告

```
请为我的分析生成一份完整的报告：
- BDF 文件：/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.bdf
- OP2 文件：/path/to/your/pyNastran/models/sol_101_elements/static_solid_shell_bar.op2
- 保存到：/tmp/my_analysis_report.txt
```

**AI 回复：**

```
📝 分析报告已生成！

📄 报告信息：
• 保存路径：/tmp/my_analysis_report.txt
• 生成时间：2024-03-01 10:30:00
• 包含章节：5 个

📋 报告内容：
1. 模型摘要（25 节点，21 单元）
2. 单元类型分解
3. 材料属性清单
4. 网格质量评估
5. 结果数据摘要（位移、应力）
6. 网格点重量信息

报告文件已保存，可以用文本编辑器打开查看完整内容。
```

---

### 示例 5：批量分析多个模型

```
请帮我分析以下模型：

模型 1：
/path/to/your/pyNastran/models/unit/pload4/cquad4.bdf

模型 2：
/path/to/your/pyNastran/models/unit/pload4/chexa.bdf

模型 3：
/path/to/your/pyNastran/models/thermal/thermal_test_153.bdf

分别读取并生成摘要表格。
```

**AI 回复：**

```
✅ 已完成 3 个模型的批量分析：

| 模型 | 节点数 | 单元数 | 类型 | 状态 |
|------|--------|--------|------|------|
| CQUAD4 | 4 | 1 | 壳单元 | ✅ 正常 |
| CHEXA | 8 | 1 | 实体单元 | ✅ 正常 |
| Thermal | 12 | 2 | 热分析 | ✅ 正常 |

详细分析：
• CQUAD4：四边形壳单元测试模型
• CHEXA：六面体实体单元测试模型
• Thermal：热传导分析测试模型

所有模型结构完整，无缺失节点或单元。
```

---

## 🛠️ 故障排除

### 问题 1：Cherry Studio 显示"连接失败"

**stdio 模式：**
```bash
# 检查命令是否存在
which pynastran-mcp

# 手动测试
pynastran-mcp --help

# 检查 Python 路径
export PYTHONPATH=/path/to/your/pyNastran:$PYTHONPATH
```

**SSE 模式：**
```bash
# 检查 SSE Server 是否运行
curl http://localhost:8080/api/health

# 检查端口是否被占用
lsof -i :8080

# 更换端口启动
pynastran-mcp --transport sse --port 8081
```

### 问题 2：AI 助手说"工具调用失败"

**检查日志：**
1. Cherry Studio 设置 → 高级 → 查看日志
2. 终端启动 SSE Server 查看实时输出

**常见原因：**
- 文件路径不存在
- 文件权限不足（用 `chmod 644` 修改）
- pyNastran 版本不兼容

### 问题 3：中文显示乱码

**解决方案：**
```bash
# 设置 UTF-8 编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 重启 Cherry Studio 和 MCP Server
```

### 问题 4：响应太慢

**优化建议：**
1. 使用 stdio 模式（比 SSE 更快）
2. 大文件只读取必要信息（如只读节点，不读结果）
3. 关闭其他占用 CPU 的程序

---

## 📝 最佳实践

### ✅ 推荐的提问方式

1. **提供完整路径**
   ```
   ✅ 读取 ~/models/wing.bdf
   ❌ 读取 wing.bdf
   ```

2. **明确指定操作**
   ```
   ✅ 检查网格质量并列出所有警告
   ❌ 看看这个模型
   ```

3. **分批处理大模型**
   ```
   ✅ 先显示模型统计信息
   ✅ 然后检查网格质量
   ✅ 最后读取结果
   ```

### 💡 提高效率的技巧

1. **使用相对路径**（如果在模型目录）
   ```
   读取 models/sol_101_elements/static_solid_shell_bar.bdf
   ```

2. **指定输出格式**
   ```
   以表格形式显示前 10 个节点的坐标
   ```

3. **批量操作**
   ```
   请检查 models/ 目录下所有 .bdf 文件的网格质量
   ```

---

## 🔗 相关链接

- Cherry Studio 官网：https://cherry-ai.com
- pyNastran 文档：https://pynastran-git.readthedocs.io
- MCP 协议文档：https://modelcontextprotocol.io

---

## 📞 获取帮助

遇到问题？

1. 查看 Cherry Studio 的 MCP 日志
2. 检查 MCP Server 终端输出
3. 确认文件路径和权限
4. 尝试重启 Cherry Studio 和 MCP Server

**Happy FEA Analysis with AI! 🎉**
