# pyNastran MCP Server

MCP (Model Context Protocol) Server for pyNastran, enabling AI agents to interact with Nastran FEA models.

## Features

- 🔧 **BDF Tools**: Read, write, and analyze Nastran input files
- 📊 **OP2 Tools**: Extract results from Nastran output files
- 🔍 **Geometry Tools**: Mesh quality checks and geometric analysis
- 📝 **Analysis Tools**: Automated report generation
- 🎯 **MCP Protocol**: Native integration with AI Agent Desktop, Cursor, and other MCP clients

## Installation

### From Source

```bash
git clone https://github.com/yourusername/pynastran-mcp.git
cd pynastran-mcp
pip install -e .
```

### Requirements

- Python 3.10+
- pyNastran >= 1.4.0
- mcp >= 1.0.0

## Quick Start

### Run as Stdio Server

```bash
pynastran-mcp
```

### Run as SSE Server

```bash
pynastran-mcp --transport sse --port 8080
```

## MCP Client Configuration

### Cherry Studio / AI Agent Desktop / Cursor

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
pos#old_content=

### Run as Stdio Server (for AI Agent Desktop)

```bash
pynastran-mcp
```

### Run as SSE Server

```bash
pynastran-mcp --transport sse --port 8080
```

## AI Agent Desktop Configuration

Add to your `mcp-client_desktop_config.json`:

```json
{
  "mcpServers": {
    "pynastran": {
      "command": "pynastran-mcp",
      "env": {
        "PYTHONPATH": "/path/to/your/python/packages"
      }
    }
  }
}
```

On macOS, the config is at:
- `~/Library/Application Support/AI Agent/mcp-client_desktop_config.json`

On Windows:
- `%APPDATA%/AI Agent/mcp-client_desktop_config.json`

## Available Tools

### BDF Tools

| Tool | Description |
|------|-------------|
| `read_bdf` | Read BDF file and return model summary |
| `get_model_info` | Get detailed model information |
| `write_bdf` | Write model to new BDF file |
| `get_nodes` | Get node coordinates and IDs |
| `get_elements` | Get element connectivity and types |
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

Once configured with your AI agent, you can ask:

```
"Read the BDF file at /path/to/model.bdf and tell me about the mesh"
"Analyze the stress results from /path/to/results.op2"
"Check the mesh quality and suggest improvements"
"Generate a report for my Nastran model"
```

pos#old_content=

### With AI Agent Desktop

Once configured, you can ask AI Agent:

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
│   ├── server.py          # Main MCP server
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

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/pynastran-mcp.git
cd pynastran-mcp
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black pynastran_mcp/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [pyNastran](https://github.com/SteveDoyle2/pyNastran) - The underlying Nastran interface library
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol enabling AI agent integration
