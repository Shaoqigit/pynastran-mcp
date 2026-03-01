# pyNastran MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)

A Model Context Protocol (MCP) Server for pyNastran, built with **FastMCP**. Enables AI agents to interact with Nastran FEA models.

## Features

- 🔧 **BDF Tools**: Read, write, and analyze Nastran input files
- 📊 **OP2 Tools**: Extract results from Nastran output files  
- 🔍 **Geometry Tools**: Mesh quality checks and geometric analysis
- 📝 **Analysis Tools**: Automated report generation
- 🚀 **FastMCP**: Built with modern FastMCP framework
- 🌐 **Multiple Transports**: stdio, SSE, and streamable-http

## Installation

```bash
pip install pynastran-mcp
```

Or install from source:

```bash
git clone https://github.com/Shaoqigit/pynastran-mcp.git
cd pynastran-mcp
pip install -e .
```

## Quick Start

### Stdio Transport (Default)

For MCP clients like Cherry Studio, Claude Desktop:

```bash
pynastran-mcp
```

### SSE Transport

```bash
# Default: host=127.0.0.1, port=8080
pynastran-mcp --transport sse

# Custom host and port
pynastran-mcp --transport sse --host 0.0.0.0 --port 8080
```

### Streamable HTTP Transport (Production)

```bash
# Default: host=127.0.0.1, port=8080
pynastran-mcp --transport streamable-http

# Custom host and port
pynastran-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

## MCP Client Configuration

### Cherry Studio / Cursor / Claude Desktop

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "pynastran": {
      "command": "pynastran-mcp"
    }
  }
}
```

See [CHERRY_STUDIO_TUTORIAL.md](CHERRY_STUDIO_TUTORIAL.md) for detailed setup instructions.

## Available Tools

### BDF Tools

| Tool | Description |
|------|-------------|
| `read_bdf` | Read BDF file and return model summary |
| `get_model_info` | Get detailed model information |
| `write_bdf` | Write model to new BDF file |
| `get_nodes` | Get node coordinates |
| `get_elements` | Get element connectivity |
| `get_materials` | Get material properties |
| `get_properties` | Get property definitions |

### OP2 Tools

| Tool | Description |
|------|-------------|
| `read_op2` | Read OP2 result file |
| `get_result_cases` | List available result cases |
| `get_stress` | Extract stress results |
| `get_displacement` | Extract displacement results |

### Geometry Tools

| Tool | Description |
|------|-------------|
| `check_mesh_quality` | Check mesh quality metrics |
| `get_model_bounds` | Get model bounding box |

### Analysis Tools

| Tool | Description |
|------|-------------|
| `generate_report` | Generate comprehensive analysis report |

## Usage Examples

### With AI Agents

Once configured, you can ask your AI assistant:

```
"Read the BDF file at /path/to/model.bdf and tell me about the mesh"
"Analyze the stress results from /path/to/results.op2"
"Check the mesh quality and suggest improvements"
"Generate a report for my Nastran model"
```

### Programmatic Usage

```python
from pynastran_mcp.tools.bdf_tools import BdfTools
from pynastran_mcp.tools.op2_tools import Op2Tools

async def analyze_model():
    # BDF Analysis
    bdf_tools = BdfTools()
    summary = await bdf_tools.read_bdf("wing.bdf")
    print(summary)
    
    # OP2 Results
    op2_tools = Op2Tools()
    stresses = await op2_tools.get_stress("results.op2", element_type="CQUAD4")
    print(stresses)
```

## Project Structure

```
pynastran-mcp/
├── pynastran_mcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP server with all tools
│   └── tools/
│       ├── __init__.py
│       ├── bdf_tools.py   # BDF file operations
│       ├── op2_tools.py   # OP2 result operations
│       ├── geometry_tools.py  # Mesh quality checks
│       └── analysis_tools.py  # Report generation
├── pyproject.toml
├── README.md
└── examples/
    └── example_usage.py
```

## Requirements

- Python 3.10+
- pyNastran >= 1.4.0
- mcp >= 1.0.0 (with FastMCP)

## Development

```bash
# Setup
git clone https://github.com/Shaoqigit/pynastran-mcp.git
cd pynastran-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black pynastran_mcp/
```

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- [pyNastran](https://github.com/SteveDoyle2/pyNastran) - The underlying Nastran interface library
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - FastMCP framework
