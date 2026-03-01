"""
pyNastran MCP Server

MCP (Model Context Protocol) Server for pyNastran, enabling AI agents
to interact with Nastran FEA models.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import app, main

__all__ = ['app', 'main']
