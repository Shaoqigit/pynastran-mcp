#!/usr/bin/env python3
"""
pyNastran MCP Server

MCP (Model Context Protocol) Server for pyNastran, providing AI agents
with tools to interact with Nastran FEA models.

Usage:
    pynastran-mcp  # Run as stdio server (for AI Agent Desktop)
    pynastran-mcp --transport sse --port 8080  # Run as SSE server
"""

import asyncio
import argparse
import json
import logging
import sys
from typing import Any
import argparse
import logging
import sys
from typing import Any

# =============================================================================
# CRITICAL: Configure logging BEFORE any pyNastran imports
# MCP uses stdout for JSON-RPC communication, so we must ensure
# no debug/info logs go to stdout
# =============================================================================

# Disable all logging to stdout by setting up a null handler for root logger
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Remove all existing handlers and add null handler
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(NullHandler())
root_logger.setLevel(logging.ERROR)

# Specifically disable pyNastran loggers
for logger_name in list(logging.root.manager.loggerDict.keys()):
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.addHandler(NullHandler())
    logger.setLevel(logging.ERROR)
    logger.propagate = False

# Also configure any new loggers that might be created
logging.disable(logging.CRITICAL)

# Now import MCP and tools
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import Resource, Tool, TextContent, ImageContent

from pynastran_mcp.tools.bdf_tools import BdfTools
from pynastran_mcp.tools.op2_tools import Op2Tools
from pynastran_mcp.tools.geometry_tools import GeometryTools
from pynastran_mcp.tools.analysis_tools import AnalysisTools

# Server instance
app = Server("pynastran-mcp")

# Tool handlers
bdf_tools = BdfTools()
op2_tools = Op2Tools()
geometry_tools = GeometryTools()
analysis_tools = AnalysisTools()


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="pynastran://docs/bdf",
            name="BDF Documentation",
            description="Nastran BDF file format documentation",
            mimeType="text/markdown"
        ),
        Resource(
            uri="pynastran://docs/op2",
            name="OP2 Documentation",
            description="Nastran OP2 result file format documentation",
            mimeType="text/markdown"
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "pynastran://docs/bdf":
        return _get_bdf_docs()
    elif uri == "pynastran://docs/op2":
        return _get_op2_docs()
    raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    tools = []
    
    # BDF Tools
    tools.extend([
        Tool(
            name="read_bdf",
            description="Read a Nastran BDF input file and return model summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: latin-1)",
                        "default": "latin-1"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_model_info",
            description="Get detailed information about a loaded BDF model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="write_bdf",
            description="Write BDF model to file",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to input BDF file"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output BDF file"
                    }
                },
                "required": ["input_path", "output_path"]
            }
        ),
        Tool(
            name="get_nodes",
            description="Get node information from BDF model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    },
                    "node_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific node IDs to retrieve (optional)"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_elements",
            description="Get element information from BDF model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    },
                    "element_type": {
                        "type": "string",
                        "description": "Filter by element type (e.g., 'CQUAD4', 'CTETRA')"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_materials",
            description="Get material properties from BDF model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_properties",
            description="Get property definitions from BDF model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    }
                },
                "required": ["filepath"]
            }
        ),
    ])
    
    # OP2 Tools
    tools.extend([
        Tool(
            name="read_op2",
            description="Read a Nastran OP2 result file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the OP2 file"
                    },
                    "combine": {
                        "type": "boolean",
                        "description": "Combine results (default: true)",
                        "default": True
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_result_cases",
            description="Get list of available result cases from OP2 file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the OP2 file"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_stress",
            description="Extract stress results from OP2 file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the OP2 file"
                    },
                    "element_type": {
                        "type": "string",
                        "description": "Element type (e.g., 'CQUAD4', 'CTRIA3')"
                    },
                    "subcase_id": {
                        "type": "integer",
                        "description": "Subcase ID (default: 1)"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_displacement",
            description="Extract displacement results from OP2 file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the OP2 file"
                    },
                    "subcase_id": {
                        "type": "integer",
                        "description": "Subcase ID (default: 1)"
                    }
                },
                "required": ["filepath"]
            }
        ),
    ])
    
    # Geometry Tools
    tools.extend([
        Tool(
            name="check_mesh_quality",
            description="Check mesh quality metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_model_bounds",
            description="Get bounding box of the model",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    }
                },
                "required": ["filepath"]
            }
        ),
    ])
    
    # Analysis Tools
    tools.extend([
        Tool(
            name="generate_report",
            description="Generate analysis report for BDF/OP2 files",
            inputSchema={
                "type": "object",
                "properties": {
                    "bdf_path": {
                        "type": "string",
                        "description": "Path to the BDF file"
                    },
                    "op2_path": {
                        "type": "string",
                        "description": "Path to the OP2 file (optional)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output report"
                    }
                },
                "required": ["bdf_path", "output_path"]
            }
        ),
    ])
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    """Call a tool by name."""
    try:
        if name == "read_bdf":
            result = await bdf_tools.read_bdf(arguments["filepath"], arguments.get("encoding", "latin-1"))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_model_info":
            result = await bdf_tools.get_model_info(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "write_bdf":
            result = await bdf_tools.write_bdf(arguments["input_path"], arguments["output_path"])
            return [TextContent(type="text", text=result)]
        
        elif name == "get_nodes":
            result = await bdf_tools.get_nodes(arguments["filepath"], arguments.get("node_ids"))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_elements":
            result = await bdf_tools.get_elements(arguments["filepath"], arguments.get("element_type"))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_materials":
            result = await bdf_tools.get_materials(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "get_properties":
            result = await bdf_tools.get_properties(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "read_op2":
            result = await op2_tools.read_op2(arguments["filepath"], arguments.get("combine", True))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_result_cases":
            result = await op2_tools.get_result_cases(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "get_stress":
            result = await op2_tools.get_stress(
                arguments["filepath"],
                arguments.get("element_type"),
                arguments.get("subcase_id", 1)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "get_displacement":
            result = await op2_tools.get_displacement(arguments["filepath"], arguments.get("subcase_id", 1))
            return [TextContent(type="text", text=result)]
        
        elif name == "check_mesh_quality":
            result = await geometry_tools.check_mesh_quality(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "get_model_bounds":
            result = await geometry_tools.get_model_bounds(arguments["filepath"])
            return [TextContent(type="text", text=result)]
        
        elif name == "generate_report":
            result = await analysis_tools.generate_report(
                arguments["bdf_path"],
                arguments.get("op2_path"),
                arguments["output_path"]
            )
            return [TextContent(type="text", text=result)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _get_bdf_docs() -> str:
    """Get BDF documentation."""
    return """
# Nastran BDF File Format

The Bulk Data File (BDF) is the primary input file for Nastran FEA analysis.

## Key Cards

### Geometry
- GRID: Defines nodal points
- CQUAD4: 4-node quadrilateral shell element
- CTRIA3: 3-node triangular shell element
- CTETRA: Tetrahedral solid element
- CHEXA: Hexahedral solid element

### Properties
- PSHELL: Shell property
- PSOLID: Solid property
- PBAR: Bar property
- PBEAM: Beam property

### Materials
- MAT1: Isotropic material
- MAT8: Orthotropic material
- MAT9: Anisotropic material

### Loads & BCs
- FORCE: Concentrated force
- PLOAD4: Pressure load
- SPC: Single point constraint
- MPC: Multi-point constraint

## pyNastran BDF Class

```python
from pyNastran.bdf.bdf import BDF

model = BDF()
model.read_bdf('model.bdf')

# Access data
nodes = model.nodes
elements = model.elements
materials = model.materials
```
"""


def _get_op2_docs() -> str:
    """Get OP2 documentation."""
    return """
# Nastran OP2 Result File Format

The OP2 file contains binary results from Nastran analysis.

## Result Types

### Displacements
- OUGV1: Displacement vector
- OUGV2: Velocity vector
- OUGV3: Acceleration vector

### Stresses
- OES1X: Element stress
- OES1C: Composite stress
- OESNLXD: Nonlinear stress

### Strains
- OSTR1X: Element strain
- OSTR1C: Composite strain

### Forces
- OEF1X: Element force

## pyNastran OP2 Class

```python
from pyNastran.op2.op2 import OP2

model = OP2()
model.read_op2('results.op2')

# Access results
displacements = model.displacements
stresses = model.stress
```
"""


async def run_stdio():
    """Run server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def run_sse(port: int = 8080):
    """Run server with SSE transport and REST API."""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import JSONResponse
    from starlette.middleware.cors import CORSMiddleware
    import uvicorn
    
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
    
    # Simple REST API endpoints for direct testing
    async def api_health(request):
        """Health check endpoint."""
        return JSONResponse({"status": "ok", "server": "pynastran-mcp", "version": "0.1.0"})
    
    async def api_tools(request):
        """List available tools via REST API."""
        tools = await list_tools()
        return JSONResponse({
            "tools": [{
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            } for tool in tools]
        })
    
    async def api_read_bdf(request):
        """Read BDF file via REST API."""
        try:
            data = await request.json()
            filepath = data.get("filepath")
            if not filepath:
                return JSONResponse({"error": "filepath is required"}, status_code=400)
            
            result = await bdf_tools.read_bdf(filepath)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_model_info(request):
        """Get model info via REST API."""
        try:
            data = await request.json()
            filepath = data.get("filepath")
            if not filepath:
                return JSONResponse({"error": "filepath is required"}, status_code=400)
            
            result = await bdf_tools.get_model_info(filepath)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_check_quality(request):
        """Check mesh quality via REST API."""
        try:
            data = await request.json()
            filepath = data.get("filepath")
            if not filepath:
                return JSONResponse({"error": "filepath is required"}, status_code=400)
            
            result = await geometry_tools.check_mesh_quality(filepath)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_get_bounds(request):
        """Get model bounds via REST API."""
        try:
            data = await request.json()
            filepath = data.get("filepath")
            if not filepath:
                return JSONResponse({"error": "filepath is required"}, status_code=400)
            
            result = await geometry_tools.get_model_bounds(filepath)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_read_op2(request):
        """Read OP2 file via REST API."""
        try:
            data = await request.json()
            filepath = data.get("filepath")
            if not filepath:
                return JSONResponse({"error": "filepath is required"}, status_code=400)
            
            result = await op2_tools.read_op2(filepath)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def api_generate_report(request):
        """Generate report via REST API."""
        try:
            data = await request.json()
            bdf_path = data.get("bdf_path")
            op2_path = data.get("op2_path")
            output_path = data.get("output_path", "/tmp/report.txt")
            
            if not bdf_path:
                return JSONResponse({"error": "bdf_path is required"}, status_code=400)
            
            result = await analysis_tools.generate_report(bdf_path, op2_path, output_path)
            return JSONResponse(json.loads(result))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    
    # Build routes
    routes = [
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        # REST API routes
        Route("/api/health", endpoint=api_health, methods=["GET"]),
        Route("/api/tools", endpoint=api_tools, methods=["GET"]),
        Route("/api/bdf/read", endpoint=api_read_bdf, methods=["POST"]),
        Route("/api/bdf/info", endpoint=api_model_info, methods=["POST"]),
        Route("/api/bdf/quality", endpoint=api_check_quality, methods=["POST"]),
        Route("/api/bdf/bounds", endpoint=api_get_bounds, methods=["POST"]),
        Route("/api/op2/read", endpoint=api_read_op2, methods=["POST"]),
        Route("/api/report", endpoint=api_generate_report, methods=["POST"]),
    ]
    
    starlette_app = Starlette(routes=routes)
    
    # Add CORS middleware
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = uvicorn.Config(starlette_app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)
    print(f"🚀 pyNastran MCP Server running on http://localhost:{port}")
    print(f"   SSE endpoint: http://localhost:{port}/sse")
    print(f"   REST API endpoint: http://localhost:{port}/api")
    await server.serve()
    """Run server with SSE transport."""
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn
    
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
    
    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )
    
    config = uvicorn.Config(starlette_app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="pyNastran MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE transport (default: 8080)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        asyncio.run(run_stdio())
    else:
        asyncio.run(run_sse(args.port))


if __name__ == "__main__":
    main()
