"""
pyNastran MCP Server

MCP (Model Context Protocol) Server for pyNastran, built with FastMCP.
Enables AI agents to interact with Nastran FEA models.
"""

__version__ = "0.1.0"
__author__ = "shaoqigit"
__email__ = "shaoqigit@github.com"

from .server import mcp, main

__all__ = ['mcp', 'main']
