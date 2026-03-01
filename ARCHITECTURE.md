# pyNastran MCP Server 架构说明

## 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Agent (AI Agent/Cursor)                    │
│  "分析这个Nastran模型并生成报告"                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ MCP Protocol
                                  │ (stdio / SSE)
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     pyNastran MCP Server                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      server.py                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │   Tools     │  │  Resources  │  │      Prompts        │   │  │
│  │  │  Registry   │  │   Registry  │  │    (Future)         │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┼───────────────────────────────────┐  │
│  │                           ▼                                    │  │
│  │  ┌────────────────────────────────────────────────────────┐   │  │
│  │  │                    Tools 模块                           │   │  │
│  │  ├────────────────┬────────────────┬──────────────────────┤   │  │
│  │  │   bdf_tools    │   op2_tools    │   geometry_tools     │   │  │
│  │  │   ─────────    │   ─────────    │   ──────────────     │   │  │
│  │  │ • read_bdf     │ • read_op2     │ • check_mesh_quality │   │  │
│  │  │ • write_bdf    │ • get_stress   │ • get_model_bounds   │   │  │
│  │  │ • get_nodes    │ • get_disp     │                      │   │  │
│  │  │ • get_elements │ • get_results  │                      │   │  │
│  │  └────────────────┴────────────────┴──────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ pyNastran API
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          pyNastran Library                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  BDF Module  │  │  OP2 Module  │  │      GUI Module          │  │
│  │  ──────────  │  │  ──────────  │  │      ──────────          │  │
│  │ • GRID cards │  │ • Results    │  │ • VTK Rendering          │  │
│  │ • Elements   │  │ • Stress     │  │ • Qt Interface           │  │
│  │ • Materials  │  │ • Displacement│  │ • Visualization          │  │
│  │ • Properties │  │ • Strain     │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ File I/O
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Nastran Files                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  model.bdf   │  │ results.op2  │  │      model.f06           │  │
│  │  (Input)     │  │  (Binary     │  │      (Text Output)       │  │
│  │              │  │   Results)   │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Server Layer (`server.py`)
- **MCP Protocol Handler**: 处理 MCP 协议的初始化、请求和响应
- **Tool Registry**: 注册和管理所有可用的 Tools
- **Resource Registry**: 提供文档等静态资源
- **Transport Layer**: 支持 stdio 和 SSE 两种传输方式

### 2. Tools Layer (`tools/`)

#### BdfTools (`bdf_tools.py`)
```python
class BdfTools:
    - read_bdf(filepath)           # 读取BDF文件
    - get_model_info(filepath)     # 获取模型信息
    - write_bdf(input, output)     # 写入BDF文件
    - get_nodes(filepath, ids)     # 获取节点信息
    - get_elements(filepath, type) # 获取单元信息
    - get_materials(filepath)      # 获取材料属性
    - get_properties(filepath)     # 获取属性定义
```

#### Op2Tools (`op2_tools.py`)
```python
class Op2Tools:
    - read_op2(filepath)           # 读取OP2文件
    - get_result_cases(filepath)   # 获取结果工况
    - get_stress(filepath, type)   # 获取应力结果
    - get_displacement(filepath)   # 获取位移结果
```

#### GeometryTools (`geometry_tools.py`)
```python
class GeometryTools:
    - check_mesh_quality(filepath) # 检查网格质量
    - get_model_bounds(filepath)   # 获取模型边界
```

#### AnalysisTools (`analysis_tools.py`)
```python
class AnalysisTools:
    - generate_report(bdf, op2, output)  # 生成分析报告
```

### 3. Data Flow

```
用户请求 → MCP Server → Tool Router → pyNastran API → 文件操作
                ↓            ↓              ↓
           协议解析    工具选择      BDF/OP2读写
                ↓            ↓              ↓
           JSON响应 ← 结果封装 ← 数据处理 ← 原始数据
```

## 工具清单

### BDF Tools (7个)

| 工具名 | 输入 | 输出 | 描述 |
|--------|------|------|------|
| read_bdf | filepath | ModelSummary | 读取并解析BDF文件 |
| get_model_info | filepath | DetailedInfo | 获取详细模型信息 |
| write_bdf | input_path, output_path | SuccessMsg | 写入BDF文件 |
| get_nodes | filepath, [node_ids] | NodeList | 获取节点信息 |
| get_elements | filepath, [element_type] | ElementList | 获取单元信息 |
| get_materials | filepath | MaterialList | 获取材料属性 |
| get_properties | filepath | PropertyList | 获取属性定义 |

### OP2 Tools (4个)

| 工具名 | 输入 | 输出 | 描述 |
|--------|------|------|------|
| read_op2 | filepath | ResultSummary | 读取OP2结果文件 |
| get_result_cases | filepath | CaseList | 获取可用结果工况 |
| get_stress | filepath, element_type, subcase | StressData | 提取应力结果 |
| get_displacement | filepath, subcase | DisplacementData | 提取位移结果 |

### Geometry Tools (2个)

| 工具名 | 输入 | 输出 | 描述 |
|--------|------|------|------|
| check_mesh_quality | filepath | QualityReport | 网格质量检查报告 |
| get_model_bounds | filepath | BoundingBox | 模型边界框信息 |

### Analysis Tools (1个)

| 工具名 | 输入 | 输出 | 描述 |
|--------|------|------|------|
| generate_report | bdf_path, [op2_path], output_path | ReportPath | 生成综合分析报告 |

## 使用场景

### 场景1: 快速模型检查
```
用户: "请检查 model.bdf 文件"
AI: 调用 read_bdf → 返回模型摘要
    调用 get_model_info → 返回详细信息
    调用 check_mesh_quality → 返回质量报告
```

### 场景2: 结果分析
```
用户: "分析 results.op2 的应力分布"
AI: 调用 read_op2 → 读取结果文件
    调用 get_result_cases → 获取工况列表
    调用 get_stress → 提取应力数据
    分析并可视化结果
```

### 场景3: 报告生成
```
用户: "生成完整的分析报告"
AI: 调用 read_bdf + read_op2 → 读取输入和结果
    调用 generate_report → 生成报告文件
    返回报告摘要
```

## 扩展计划

### Phase 2: 增强功能
- [ ] 模型修改工具 (add_node, add_element, modify_material)
- [ ] 高级结果处理 (combine_results, compare_cases)
- [ ] 可视化导出 (export_vtk, export_stl)

### Phase 3: GUI 集成
- [ ] pyNastran GUI AI Assistant
- [ ] 实时可视化反馈
- [ ] 交互式模型编辑

### Phase 4: 工作流自动化
- [ ] Multi-agent 协作
- [ ] 参数化研究自动化
- [ ] 优化工作流集成

## 技术细节

### MCP 协议实现
```python
# Tool Definition
Tool(
    name="read_bdf",
    description="Read a Nastran BDF input file",
    inputSchema={
        "type": "object",
        "properties": {
            "filepath": {"type": "string"},
            "encoding": {"type": "string", "default": "latin-1"}
        },
        "required": ["filepath"]
    }
)

# Tool Call
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_bdf":
        result = await bdf_tools.read_bdf(arguments["filepath"])
        return [TextContent(type="text", text=result)]
```

### 缓存策略
- **内存缓存**: 已加载的 BDF/OP2 模型缓存在内存中
- **键值**: 文件路径作为缓存键
- **失效**: 重启服务器时缓存清空

### 错误处理
```python
try:
    model = read_bdf(filepath)
    return json.dumps({"success": True, "data": ...})
except Exception as e:
    return json.dumps({"error": str(e)})
```

## 配置示例

### AI Agent Desktop
```json
{
  "mcpServers": {
    "pynastran": {
      "command": "pynastran-mcp",
      "env": {
        "PYTHONPATH": "/path/to/site-packages"
      }
    }
  }
}
```

### SSE 模式
```bash
pynastran-mcp --transport sse --port 8080
```

然后配置 MCP Client:
```json
{
  "mcpServers": {
    "pynastran": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```
