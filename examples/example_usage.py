"""
Example usage of pyNastran MCP Server tools.
"""

import asyncio
from pynastran_mcp.tools.bdf_tools import BdfTools
from pynastran_mcp.tools.op2_tools import Op2Tools
from pynastran_mcp.tools.geometry_tools import GeometryTools
from pynastran_mcp.tools.analysis_tools import AnalysisTools


async def example_bdf_analysis():
    """Example: Analyze a BDF file."""
    bdf_tools = BdfTools()
    
    # Read BDF file
    print("=== Reading BDF file ===")
    result = await bdf_tools.read_bdf("path/to/your/model.bdf")
    print(result)
    
    # Get detailed info
    print("\n=== Detailed Model Info ===")
    info = await bdf_tools.get_model_info("path/to/your/model.bdf")
    print(info)
    
    # Get nodes
    print("\n=== Node Information ===")
    nodes = await bdf_tools.get_nodes("path/to/your/model.bdf", node_ids=[1, 2, 3])
    print(nodes)
    
    # Get elements
    print("\n=== Element Information ===")
    elements = await bdf_tools.get_elements("path/to/your/model.bdf", element_type="CQUAD4")
    print(elements)


async def example_op2_analysis():
    """Example: Analyze OP2 results."""
    op2_tools = Op2Tools()
    
    # Read OP2 file
    print("=== Reading OP2 file ===")
    result = await op2_tools.read_op2("path/to/your/results.op2")
    print(result)
    
    # Get stress results
    print("\n=== Stress Results ===")
    stresses = await op2_tools.get_stress("path/to/your/results.op2", element_type="CQUAD4")
    print(stresses)
    
    # Get displacements
    print("\n=== Displacement Results ===")
    displacements = await op2_tools.get_displacement("path/to/your/results.op2")
    print(displacements)


async def example_geometry_analysis():
    """Example: Geometry and mesh quality analysis."""
    geometry_tools = GeometryTools()
    
    # Check mesh quality
    print("=== Mesh Quality Check ===")
    quality = await geometry_tools.check_mesh_quality("path/to/your/model.bdf")
    print(quality)
    
    # Get model bounds
    print("\n=== Model Bounds ===")
    bounds = await geometry_tools.get_model_bounds("path/to/your/model.bdf")
    print(bounds)


async def example_report_generation():
    """Example: Generate analysis report."""
    analysis_tools = AnalysisTools()
    
    # Generate report
    print("=== Generating Report ===")
    report = await analysis_tools.generate_report(
        bdf_path="path/to/your/model.bdf",
        op2_path="path/to/your/results.op2",
        output_path="path/to/your/report.txt"
    )
    print(report)


async def main():
    """Run all examples."""
    print("pyNastran MCP Tools Examples")
    print("=" * 50)
    
    # Uncomment the examples you want to run:
    # await example_bdf_analysis()
    # await example_op2_analysis()
    # await example_geometry_analysis()
    # await example_report_generation()
    
    print("\nExamples completed!")


if __name__ == "__main__":
    asyncio.run(main())
