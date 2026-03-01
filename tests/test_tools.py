"""
Tests for pyNastran MCP Server.
"""

import pytest
import asyncio
from pathlib import Path

from pynastran_mcp.tools.bdf_tools import BdfTools
from pynastran_mcp.tools.op2_tools import Op2Tools
from pynastran_mcp.tools.geometry_tools import GeometryTools
from pynastran_mcp.tools.analysis_tools import AnalysisTools


class TestBdfTools:
    """Test BDF tools."""
    
    @pytest.fixture
    def bdf_tools(self):
        return BdfTools()
    
    @pytest.mark.asyncio
    async def test_read_bdf_invalid_file(self, bdf_tools):
        """Test reading invalid BDF file."""
        result = await bdf_tools.read_bdf("/nonexistent/path/model.bdf")
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_model_info_invalid_file(self, bdf_tools):
        """Test getting model info for invalid file."""
        result = await bdf_tools.get_model_info("/nonexistent/path/model.bdf")
        assert "error" in result


class TestOp2Tools:
    """Test OP2 tools."""
    
    @pytest.fixture
    def op2_tools(self):
        return Op2Tools()
    
    @pytest.mark.asyncio
    async def test_read_op2_invalid_file(self, op2_tools):
        """Test reading invalid OP2 file."""
        result = await op2_tools.read_op2("/nonexistent/path/results.op2")
        assert "error" in result


class TestGeometryTools:
    """Test geometry tools."""
    
    @pytest.fixture
    def geometry_tools(self):
        return GeometryTools()
    
    @pytest.mark.asyncio
    async def test_check_mesh_quality_invalid_file(self, geometry_tools):
        """Test mesh quality check for invalid file."""
        result = await geometry_tools.check_mesh_quality("/nonexistent/path/model.bdf")
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_model_bounds_invalid_file(self, geometry_tools):
        """Test model bounds for invalid file."""
        result = await geometry_tools.get_model_bounds("/nonexistent/path/model.bdf")
        assert "error" in result


class TestAnalysisTools:
    """Test analysis tools."""
    
    @pytest.fixture
    def analysis_tools(self):
        return AnalysisTools()
    
    @pytest.mark.asyncio
    async def test_generate_report_invalid_file(self, analysis_tools):
        """Test report generation for invalid file."""
        result = await analysis_tools.generate_report(
            bdf_path="/nonexistent/path/model.bdf",
            output_path="/tmp/report.txt"
        )
        assert "error" in result


def test_imports():
    """Test that all modules can be imported."""
    from pynastran_mcp import app, main
    from pynastran_mcp.tools import BdfTools, Op2Tools, GeometryTools, AnalysisTools
    assert app is not None
    assert main is not None
