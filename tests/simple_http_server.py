#!/usr/bin/env python3
"""
Simple HTTP Server for pyNastran MCP Testing

This is a simplified HTTP server for testing without the complex MCP protocol.
Directly exposes pyNastran functionality via REST API.

Usage:
    python simple_http_server.py --port 8080
    
Then test with:
    curl http://localhost:8080/api/health
    curl -X POST http://localhost:8080/api/bdf/read -H "Content-Type: application/json" -d '{"filepath": "/path/to/model.bdf"}'
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Disable logging
logging.disable(logging.CRITICAL)

from aiohttp import web

# Import pyNastran
logging.disable(logging.CRITICAL)
from pyNastran.bdf.bdf import read_bdf
from pyNastran.op2.op2 import read_op2

# Routes
routes = web.RouteTableDef()


@routes.get('/api/health')
async def health(request):
    """Health check endpoint."""
    return web.json_response({
        "status": "ok",
        "server": "pynastran-simple-http",
        "version": "0.1.0"
    })


@routes.post('/api/bdf/read')
async def read_bdf_file(request):
    """Read BDF file."""
    try:
        data = await request.json()
        filepath = data.get('filepath')
        
        if not filepath:
            return web.json_response({"error": "filepath is required"}, status=400)
        
        model = read_bdf(filepath, validate=True)
        
        result = {
            "filepath": filepath,
            "success": True,
            "n_nodes": len(model.nodes),
            "n_elements": len(model.elements),
            "n_materials": len(model.materials),
            "n_properties": len(model.properties),
            "element_types": {},
            "material_types": {}
        }
        
        # Count element types
        for elem in model.elements.values():
            etype = elem.type
            result["element_types"][etype] = result["element_types"].get(etype, 0) + 1
        
        # Count material types
        for mat in model.materials.values():
            mtype = mat.type
            result["material_types"][mtype] = result["material_types"].get(mtype, 0) + 1
        
        return web.json_response(result)
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/bdf/nodes')
async def get_nodes(request):
    """Get nodes from BDF."""
    try:
        data = await request.json()
        filepath = data.get('filepath')
        node_ids = data.get('node_ids', [])
        
        if not filepath:
            return web.json_response({"error": "filepath is required"}, status=400)
        
        model = read_bdf(filepath, validate=True)
        
        nodes = []
        ids_to_get = node_ids if node_ids else list(model.nodes.keys())[:100]
        
        for nid in ids_to_get:
            if nid in model.nodes:
                node = model.nodes[nid]
                nodes.append({
                    "id": nid,
                    "xyz": [float(x) for x in node.xyz],
                    "cp": int(node.cp),
                    "cd": int(node.cd) if hasattr(node, 'cd') else None
                })
        
        return web.json_response({
            "filepath": filepath,
            "total_count": len(model.nodes),
            "returned_count": len(nodes),
            "nodes": nodes
        })
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/bdf/elements')
async def get_elements(request):
    """Get elements from BDF."""
    try:
        data = await request.json()
        filepath = data.get('filepath')
        element_type = data.get('element_type')
        
        if not filepath:
            return web.json_response({"error": "filepath is required"}, status=400)
        
        model = read_bdf(filepath, validate=True)
        
        elements = []
        type_counts = {}
        
        for eid, elem in model.elements.items():
            etype = elem.type
            type_counts[etype] = type_counts.get(etype, 0) + 1
            
            if element_type and etype != element_type:
                continue
            
            if len(elements) < 100:
                elem_info = {
                    "id": int(eid),
                    "type": etype,
                    "nodes": [int(n) for n in elem.nodes] if hasattr(elem, 'nodes') else []
                }
                if hasattr(elem, 'pid'):
                    elem_info["pid"] = int(elem.pid)
                elements.append(elem_info)
        
        return web.json_response({
            "filepath": filepath,
            "total_count": len(model.elements),
            "returned_count": len(elements),
            "by_type": type_counts,
            "elements": elements
        })
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/op2/read')
async def read_op2_file(request):
    """Read OP2 file."""
    try:
        data = await request.json()
        filepath = data.get('filepath')
        
        if not filepath:
            return web.json_response({"error": "filepath is required"}, status=400)
        
        model = read_op2(filepath)
        
        result = {
            "filepath": filepath,
            "success": True,
            "available_results": []
        }
        
        # Check available results
        if hasattr(model, 'op2_results') and model.op2_results:
            ors = model.op2_results
            if hasattr(ors, 'displacements') and ors.displacements:
                result["available_results"].append("displacements")
            if hasattr(ors, 'stress') and ors.stress:
                result["available_results"].append("stress")
            if hasattr(ors, 'strain') and ors.strain:
                result["available_results"].append("strain")
        
        return web.json_response(result)
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/op2/displacement')
async def get_displacement(request):
    """Get displacement from OP2."""
    try:
        data = await request.json()
        filepath = data.get('filepath')
        subcase_id = data.get('subcase_id', 1)
        
        if not filepath:
            return web.json_response({"error": "filepath is required"}, status=400)
        
        model = read_op2(filepath)
        
        displacements = []
        
        if hasattr(model, 'op2_results') and model.op2_results:
            # Try to get displacements from various sources
            disp_results = None
            if hasattr(model.op2_results, 'displacements') and model.op2_results.displacements:
                disp_results = model.op2_results.displacements
            elif hasattr(model, 'displacements') and model.displacements:
                disp_results = model.displacements
            
            if disp_results:
                for key, disp in disp_results.items():
                    disp_data = {
                        "subcase": str(key),
                        "node_count": len(disp.node_gridtype) if hasattr(disp, 'node_gridtype') else 0
                    }
                    
                    if hasattr(disp, 'data') and disp.data is not None:
                        data_arr = disp.data
                        if len(data_arr.shape) == 3:
                            magnitudes = [float(x) for x in 
                                __import__('numpy').sqrt(__import__('numpy').sum(data_arr[0][:, :3]**2, axis=1))]
                            disp_data["max_magnitude"] = max(magnitudes) if magnitudes else None
                            disp_data["min_magnitude"] = min(magnitudes) if magnitudes else None
                    
                    displacements.append(disp_data)
        
        return web.json_response({
            "filepath": filepath,
            "subcase_id": subcase_id,
            "displacements": displacements
        })
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def init_app():
    """Initialize the application."""
    app = web.Application()
    app.add_routes(routes)
    
    # Enable CORS
    import aiohttp_cors
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Simple HTTP Server for pyNastran")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    args = parser.parse_args()
    
    print(f"🚀 Simple HTTP Server for pyNastran")
    print(f"   URL: http://{args.host}:{args.port}")
    print(f"   API: http://{args.host}:{args.port}/api")
    print()
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/bdf/read")
    print("  POST /api/bdf/nodes")
    print("  POST /api/bdf/elements")
    print("  POST /api/op2/read")
    print("  POST /api/op2/displacement")
    print()
    
    web.run_app(init_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
