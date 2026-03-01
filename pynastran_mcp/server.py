#!/usr/bin/env python3
"""
pyNastran MCP Server - FastMCP Implementation

A Model Context Protocol (MCP) Server for pyNastran using FastMCP.
Supports stdio, SSE, and streamable-http transports.

Usage:
    pynastran-mcp                          # stdio (default)
    pynastran-mcp --transport sse          # SSE transport
    pynastran-mcp --transport streamable-http  # HTTP transport
"""

import argparse
import json
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("pyNastran").setLevel(logging.ERROR)

from mcp.server.fastmcp import FastMCP
from pynastran_mcp.tools.bdf_tools import BdfTools
from pynastran_mcp.tools.op2_tools import Op2Tools
from pynastran_mcp.tools.geometry_tools import GeometryTools
from pynastran_mcp.tools.analysis_tools import AnalysisTools

# Create FastMCP server instance
mcp = FastMCP("pynastran-mcp")

# Initialize tools
bdf_tools = BdfTools()
op2_tools = Op2Tools()
geometry_tools = GeometryTools()
analysis_tools = AnalysisTools()

# ============================================================================
# Tools - BDF Operations
# ============================================================================


@mcp.tool()
async def read_bdf(filepath: str, encoding: str = "latin-1") -> str:
    """
    Read a Nastran BDF input file and return model summary.
    
    Args:
        filepath: Path to the BDF file
        encoding: File encoding (default: latin-1)
    
    Returns:
        JSON string with model summary including node count, element count, etc.
    """
    result = await bdf_tools.read_bdf(filepath, encoding)
    return result


@mcp.tool()
async def get_model_info(filepath: str) -> str:
    """
    Get detailed information about a loaded BDF model.
    
    Args:
        filepath: Path to the BDF file
    
    Returns:
        Detailed model information as JSON string
    """
    result = await bdf_tools.get_model_info(filepath)
    return result


@mcp.tool()
async def write_bdf(input_path: str, output_path: str) -> str:
    """
    Write BDF model to a new file.
    
    Args:
        input_path: Path to input BDF file
        output_path: Path for output BDF file
    
    Returns:
        Success message with output path
    """
    result = await bdf_tools.write_bdf(input_path, output_path)
    return result


@mcp.tool()
async def get_nodes(filepath: str, node_ids: list = None) -> str:
    """
    Get node information from BDF model.
    
    Args:
        filepath: Path to the BDF file
        node_ids: Specific node IDs to retrieve (optional, gets first 100 if not specified)
    
    Returns:
        Node information including coordinates
    """
    result = await bdf_tools.get_nodes(filepath, node_ids)
    return result


@mcp.tool()
async def get_elements(filepath: str, element_type: str = None) -> str:
    """
    Get element information from BDF model.
    
    Args:
        filepath: Path to the BDF file
        element_type: Filter by element type (e.g., 'CQUAD4', 'CTETRA')
    
    Returns:
        Element connectivity and type information
    """
    result = await bdf_tools.get_elements(filepath, element_type)
    return result


@mcp.tool()
async def get_materials(filepath: str) -> str:
    """
    Get material properties from BDF model.
    
    Args:
        filepath: Path to the BDF file
    
    Returns:
        Material properties including E, nu, rho, etc.
    """
    result = await bdf_tools.get_materials(filepath)
    return result


@mcp.tool()
async def get_properties(filepath: str) -> str:
    """
    Get property definitions from BDF model.
    
    Args:
        filepath: Path to the BDF file
    
    Returns:
        Property definitions for elements
    """
    result = await bdf_tools.get_properties(filepath)
    return result


# ============================================================================
# Tools - OP2 Results
# ============================================================================


@mcp.tool()
async def read_op2(filepath: str, combine: bool = True) -> str:
    """
    Read a Nastran OP2 result file.
    
    Args:
        filepath: Path to the OP2 file
        combine: Combine results flag (default: True)
    
    Returns:
        Result summary including available result types
    """
    result = await op2_tools.read_op2(filepath, combine)
    return result


@mcp.tool()
async def get_result_cases(filepath: str) -> str:
    """
    Get list of available result cases from OP2 file.
    
    Args:
        filepath: Path to the OP2 file
    
    Returns:
        List of result cases (displacement, stress, etc.)
    """
    result = await op2_tools.get_result_cases(filepath)
    return result


@mcp.tool()
async def get_stress(filepath: str,
                     element_type: str = None,
                     subcase_id: int = 1) -> str:
    """
    Extract stress results from OP2 file.
    
    Args:
        filepath: Path to the OP2 file
        element_type: Filter by element type (e.g., 'CQUAD4')
        subcase_id: Subcase ID (default: 1)
    
    Returns:
        Stress results with statistics (max, min, mean)
    """
    result = await op2_tools.get_stress(filepath, element_type, subcase_id)
    return result


@mcp.tool()
async def get_displacement(filepath: str, subcase_id: int = 1) -> str:
    """
    Extract displacement results from OP2 file.
    
    Args:
        filepath: Path to the OP2 file
        subcase_id: Subcase ID (default: 1)
    
    Returns:
        Displacement results with magnitude statistics
    """
    result = await op2_tools.get_displacement(filepath, subcase_id)
    return result


# ============================================================================
# Tools - Geometry Analysis
# ============================================================================


@mcp.tool()
async def check_mesh_quality(filepath: str) -> str:
    """
    Check mesh quality metrics.
    
    Args:
        filepath: Path to the BDF file
    
    Returns:
        Quality report including aspect ratio, element quality, and recommendations
    """
    result = await geometry_tools.check_mesh_quality(filepath)
    return result


@mcp.tool()
async def get_model_bounds(filepath: str) -> str:
    """
    Get bounding box of the model.
    
    Args:
        filepath: Path to the BDF file
    
    Returns:
        Bounding box dimensions and center coordinates
    """
    result = await geometry_tools.get_model_bounds(filepath)
    return result


# ============================================================================
# Tools - Analysis & Reporting
# ============================================================================


@mcp.tool()
async def generate_report(bdf_path: str,
                          op2_path: str = None,
                          output_path: str = None) -> str:
    """
    Generate analysis report for BDF/OP2 files.
    
    Args:
        bdf_path: Path to the BDF file
        op2_path: Path to the OP2 file (optional)
        output_path: Path for output report (optional, defaults to /tmp/report.txt)
    
    Returns:
        Report summary and file path
    """
    if output_path is None:
        output_path = "/tmp/report.txt"
    result = await analysis_tools.generate_report(bdf_path, op2_path,
                                                  output_path)
    return result


# ============================================================================
# Resources
# ============================================================================


@mcp.resource("docs://bdf")
async def get_bdf_docs() -> str:
    """Get BDF file format documentation."""
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

## pyNastran BDF Class

```python
from pyNastran.bdf.bdf import BDF

model = BDF()
model.read_bdf('model.bdf')
```
"""


@mcp.resource("docs://op2")
async def get_op2_docs() -> str:
    """Get OP2 file format documentation."""
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

### Strains
- OSTR1X: Element strain

## pyNastran OP2 Class

```python
from pyNastran.op2.op2 import OP2

model = OP2()
model.read_op2('results.op2')
```
"""


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Run the MCP server with support for multiple transports."""
    parser = argparse.ArgumentParser(description="pyNastran MCP Server")
    parser.add_argument("--transport",
                        choices=["stdio", "sse", "streamable-http"],
                        default="stdio",
                        help="Transport type (default: stdio)")
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE/streamable-http transport (default: 8080)")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for SSE/streamable-http transport (default: 0.0.0.0)")

    args = parser.parse_args()

    print(f"🚀 Starting pyNastran MCP Server")
    print(f"   Transport: {args.transport}")

    if args.transport in ["sse", "streamable-http"]:
        print(f"   URL: http://{args.host}:{args.port}")
        # Configure host and port via settings
        mcp.settings.host = args.host
        mcp.settings.port = args.port
    
    # Run with specified transport
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        mcp.run(transport="sse")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
