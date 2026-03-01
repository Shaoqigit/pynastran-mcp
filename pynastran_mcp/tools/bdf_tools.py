"""
BDF Tools for MCP Server

Handles all BDF (Bulk Data File) related operations.
"""

import json
import logging

# Disable pyNastran logging before import
logging.disable(logging.CRITICAL)

from typing import Optional
from pyNastran.bdf.bdf import BDF, read_bdf


class BdfTools:
    """Tools for working with Nastran BDF files."""
    
    def __init__(self):
        """Initialize BDF tools."""
        self._cache = {}  # Simple cache for loaded models
    
    async def read_bdf(self, filepath: str, encoding: str = "latin-1") -> str:
        """Read a BDF file and return model summary."""
        try:
            model = read_bdf(filepath, encoding=encoding, validate=True)
            self._cache[filepath] = model
            
            summary = {
                "filepath": filepath,
                "n_nodes": len(model.nodes),
                "n_elements": len(model.elements),
                "n_materials": len(model.materials),
                "n_properties": len(model.properties),
                "n_loads": len(model.loads),
                "n_constraints": len(model.spcs) + len(model.mpcs),
                "element_types": self._count_element_types(model),
                "material_types": self._count_material_types(model),
            }
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_model_info(self, filepath: str) -> str:
        """Get detailed model information."""
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            info = {
                "filepath": filepath,
                "nodes": {
                    "count": len(model.nodes),
                    "coordinate_systems": list(set(node.cp for node in model.nodes.values()))
                },
                "elements": {
                    "count": len(model.elements),
                    "by_type": self._count_element_types(model)
                },
                "materials": {
                    "count": len(model.materials),
                    "by_type": self._count_material_types(model),
                    "ids": list(model.materials.keys())[:10]
                },
                "properties": {
                    "count": len(model.properties),
                    "by_type": self._count_property_types(model)
                },
                "loads": {
                    "count": len(model.loads),
                },
                "constraints": {
                    "spc_count": len(model.spcs),
                    "mpc_count": len(model.mpcs)
                },
            }
            
            return json.dumps(info, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def write_bdf(self, input_path: str, output_path: str) -> str:
        """Write BDF model to file."""
        try:
            if input_path in self._cache:
                model = self._cache[input_path]
            else:
                model = read_bdf(input_path, validate=True)
            
            model.write_bdf(output_path)
            
            return json.dumps({
                "success": True,
                "message": f"Model written to {output_path}",
                "output_path": output_path
            })
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_nodes(self, filepath: str, node_ids: Optional[list] = None) -> str:
        """Get node information."""
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            nodes = []
            ids_to_get = node_ids if node_ids else list(model.nodes.keys())[:100]
            
            for nid in ids_to_get:
                if nid in model.nodes:
                    node = model.nodes[nid]
                    nodes.append({
                        "id": nid,
                        "xyz": list(node.xyz),
                        "cp": node.cp,
                        "cd": node.cd
                    })
            
            return json.dumps({
                "filepath": filepath,
                "nodes": nodes,
                "total_count": len(model.nodes),
                "returned_count": len(nodes)
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_elements(self, filepath: str, element_type: Optional[str] = None) -> str:
        """Get element information."""
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            elements = []
            count = 0
            max_elements = 100
            
            for eid, elem in model.elements.items():
                if element_type and elem.type != element_type:
                    continue
                
                if count >= max_elements:
                    break
                
                elem_info = {
                    "id": eid,
                    "type": elem.type,
                    "nodes": elem.nodes.tolist() if hasattr(elem.nodes, 'tolist') else list(elem.nodes),
                    "pid": elem.pid if hasattr(elem, 'pid') else None
                }
                elements.append(elem_info)
                count += 1
            
            type_counts = {}
            for elem in model.elements.values():
                etype = elem.type
                type_counts[etype] = type_counts.get(etype, 0) + 1
            
            return json.dumps({
                "filepath": filepath,
                "elements": elements,
                "total_count": len(model.elements),
                "returned_count": len(elements),
                "by_type": type_counts
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_materials(self, filepath: str) -> str:
        """Get material properties."""
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            materials = []
            for mid, mat in model.materials.items():
                mat_info = {
                    "id": mid,
                    "type": mat.type
                }
                
                if hasattr(mat, 'e'):
                    mat_info["youngs_modulus"] = mat.e
                if hasattr(mat, 'g'):
                    mat_info["shear_modulus"] = mat.g
                if hasattr(mat, 'nu'):
                    mat_info["poissons_ratio"] = mat.nu
                if hasattr(mat, 'rho'):
                    mat_info["density"] = mat.rho
                
                materials.append(mat_info)
            
            return json.dumps({
                "filepath": filepath,
                "materials": materials,
                "count": len(materials)
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_properties(self, filepath: str) -> str:
        """Get property definitions."""
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            properties = []
            for pid, prop in model.properties.items():
                prop_info = {
                    "id": pid,
                    "type": prop.type,
                    "mid": prop.mid if hasattr(prop, 'mid') else None
                }
                
                if prop.type == 'PSHELL':
                    if hasattr(prop, 't') and prop.t is not None:
                        try:
                            import numpy as np
                            if isinstance(prop.t, np.ndarray):
                                prop_info["thickness"] = float(prop.t[0]) if len(prop.t) > 0 else None
                            else:
                                prop_info["thickness"] = float(prop.t)
                        except:
                            prop_info["thickness"] = str(prop.t)
                elif prop.type in ['PBAR', 'PBEAM']:
                    if hasattr(prop, 'A') and prop.A is not None:
                        try:
                            import numpy as np
                            if isinstance(prop.A, np.ndarray):
                                prop_info["area"] = float(prop.A[0]) if len(prop.A) > 0 else None
                            else:
                                prop_info["area"] = float(prop.A)
                        except:
                            prop_info["area"] = str(prop.A)
                
                properties.append(prop_info)
            
            return json.dumps({
                "filepath": filepath,
                "properties": properties,
                "count": len(properties)
            }, indent=2, default=str)
            
        except Exception as e:
            import traceback
            return json.dumps({"error": str(e), "traceback": traceback.format_exc()})
    
    def _count_element_types(self, model: BDF) -> dict:
        """Count elements by type."""
        counts = {}
        for elem in model.elements.values():
            etype = elem.type
            counts[etype] = counts.get(etype, 0) + 1
        return counts
    
    def _count_material_types(self, model: BDF) -> dict:
        """Count materials by type."""
        counts = {}
        for mat in model.materials.values():
            mtype = mat.type
            counts[mtype] = counts.get(mtype, 0) + 1
        return counts
    
    def _count_property_types(self, model: BDF) -> dict:
        """Count properties by type."""
        counts = {}
        for prop in model.properties.values():
            ptype = prop.type
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts
