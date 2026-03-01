"""
Geometry Tools for MCP Server

Handles mesh quality checks and geometric operations.
"""

import json
import logging
import numpy as np

# Disable pyNastran logging before import
logging.disable(logging.CRITICAL)

from pyNastran.bdf.bdf import read_bdf


class GeometryTools:
    """Tools for geometric analysis and mesh quality."""
    
    def __init__(self):
        """Initialize geometry tools."""
        self._cache = {}
    
    async def check_mesh_quality(self, filepath: str) -> str:
        """
        Check mesh quality metrics.
        
        Args:
            filepath: Path to BDF file
            
        Returns:
            Mesh quality report as JSON
        """
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            quality = {
                "filepath": filepath,
                "element_quality": self._check_element_quality(model),
                "node_quality": self._check_node_quality(model),
                "connectivity": self._check_connectivity(model),
                "recommendations": []
            }
            
            # Generate recommendations
            recommendations = []
            
            eq = quality["element_quality"]
            if eq.get("high_aspect_ratio_count", 0) > 0:
                recommendations.append(
                    f"Found {eq['high_aspect_ratio_count']} elements with high aspect ratio. "
                    "Consider remeshing or refining."
                )
            
            if eq.get("zero_area_count", 0) > 0:
                recommendations.append(
                    f"Found {eq['zero_area_count']} degenerate elements (zero area/volume). "
                    "These should be fixed before analysis."
                )
            
            cq = quality["connectivity"]
            if cq.get("free_nodes", 0) > 0:
                recommendations.append(
                    f"Found {cq['free_nodes']} free nodes not connected to any element."
                )
            
            quality["recommendations"] = recommendations
            
            return json.dumps(quality, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_model_bounds(self, filepath: str) -> str:
        """
        Get bounding box of the model.
        
        Args:
            filepath: Path to BDF file
            
        Returns:
            Bounding box information as JSON
        """
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_bdf(filepath, validate=True)
                self._cache[filepath] = model
            
            if not model.nodes:
                return json.dumps({"error": "No nodes in model"})
            
            # Collect all node coordinates
            coords = np.array([node.xyz for node in model.nodes.values()])
            
            bounds = {
                "filepath": filepath,
                "bounding_box": {
                    "x": {"min": float(coords[:, 0].min()), "max": float(coords[:, 0].max())},
                    "y": {"min": float(coords[:, 1].min()), "max": float(coords[:, 1].max())},
                    "z": {"min": float(coords[:, 2].min()), "max": float(coords[:, 2].max())}
                },
                "dimensions": {
                    "x": float(coords[:, 0].max() - coords[:, 0].min()),
                    "y": float(coords[:, 1].max() - coords[:, 1].min()),
                    "z": float(coords[:, 2].max() - coords[:, 2].min())
                },
                "center": [
                    float(coords[:, 0].mean()),
                    float(coords[:, 1].mean()),
                    float(coords[:, 2].mean())
                ]
            }
            
            return json.dumps(bounds, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _check_element_quality(self, model) -> dict:
        """Check element quality metrics."""
        metrics = {
            "total_elements": len(model.elements),
            "by_type": {},
            "high_aspect_ratio_count": 0,
            "zero_area_count": 0,
            "warnings": []
        }
        
        aspect_ratios = []
        
        for eid, elem in model.elements.items():
            etype = elem.type
            metrics["by_type"][etype] = metrics["by_type"].get(etype, 0) + 1
            
            # Check element-specific quality
            if etype in ['CQUAD4', 'CQUAD8', 'CTRIA3', 'CTRIA6']:
                quality = self._check_shell_quality(elem)
                if quality.get("aspect_ratio", 0) > 10:
                    metrics["high_aspect_ratio_count"] += 1
                if quality.get("area", 1) <= 0:
                    metrics["zero_area_count"] += 1
                aspect_ratios.append(quality.get("aspect_ratio", 0))
            
            elif etype in ['CTETRA', 'CHEXA', 'CPENTA', 'CPYRAM']:
                quality = self._check_solid_quality(elem)
                if quality.get("volume", 1) <= 0:
                    metrics["zero_area_count"] += 1
        
        if aspect_ratios:
            metrics["aspect_ratio_stats"] = {
                "min": min(aspect_ratios),
                "max": max(aspect_ratios),
                "mean": sum(aspect_ratios) / len(aspect_ratios)
            }
        
        return metrics
    
    def _check_shell_quality(self, elem) -> dict:
        """Check shell element quality."""
        quality = {"aspect_ratio": 0, "area": 0}
        
        try:
            nodes = elem.nodes
            if len(nodes) < 3:
                return quality
            
            # Get node coordinates
            coords = []
            for nid in nodes[:4]:  # Limit to first 4 for quads
                if nid in elem.model.nodes:
                    coords.append(elem.model.nodes[nid].xyz)
            
            if len(coords) >= 3:
                coords = np.array(coords)
                
                # Calculate edge lengths
                edges = []
                for i in range(len(coords)):
                    j = (i + 1) % len(coords)
                    length = np.linalg.norm(coords[j] - coords[i])
                    edges.append(length)
                
                if edges:
                    min_edge = min(edges)
                    max_edge = max(edges)
                    if min_edge > 0:
                        quality["aspect_ratio"] = max_edge / min_edge
                
                # Calculate area (simplified for triangles)
                if len(coords) == 3:
                    v1 = coords[1] - coords[0]
                    v2 = coords[2] - coords[0]
                    cross = np.cross(v1, v2)
                    quality["area"] = 0.5 * np.linalg.norm(cross)
                else:
                    # For quads, use cross product of diagonals
                    v1 = coords[2] - coords[0]
                    v2 = coords[3] - coords[1]
                    quality["area"] = 0.5 * np.linalg.norm(np.cross(v1, v2))
        
        except Exception:
            pass
        
        return quality
    
    def _check_solid_quality(self, elem) -> dict:
        """Check solid element quality."""
        quality = {"volume": 0}
        
        try:
            nodes = elem.nodes
            if len(nodes) < 4:
                return quality
            
            # Simplified volume calculation for tetrahedra
            if elem.type in ['CTETRA', 'CTETRA4', 'CTETRA10'] and len(nodes) >= 4:
                coords = []
                for nid in nodes[:4]:
                    if nid in elem.model.nodes:
                        coords.append(elem.model.nodes[nid].xyz)
                
                if len(coords) == 4:
                    coords = np.array(coords)
                    # Volume = |det([v1-v0, v2-v0, v3-v0])| / 6
                    v1 = coords[1] - coords[0]
                    v2 = coords[2] - coords[0]
                    v3 = coords[3] - coords[0]
                    matrix = np.array([v1, v2, v3])
                    quality["volume"] = abs(np.linalg.det(matrix)) / 6.0
        
        except Exception:
            pass
        
        return quality
    
    def _check_node_quality(self, model) -> dict:
        """Check node quality metrics."""
        metrics = {
            "total_nodes": len(model.nodes),
            "spoints": len(model.spoints),
            "epoints": len(model.epoints),
            "coordinate_systems": len(model.coords)
        }
        
        # Check for duplicate nodes (simplified)
        coords_dict = {}
        duplicate_count = 0
        
        for nid, node in model.nodes.items():
            coord_tuple = tuple(np.round(node.xyz, 6))
            if coord_tuple in coords_dict:
                duplicate_count += 1
            else:
                coords_dict[coord_tuple] = nid
        
        metrics["potential_duplicate_nodes"] = duplicate_count
        
        return metrics
    
    def _check_connectivity(self, model) -> dict:
        """Check model connectivity."""
        # Build node-element connectivity
        node_elements = {nid: [] for nid in model.nodes}
        
        for eid, elem in model.elements.items():
            for nid in elem.nodes:
                if nid in node_elements:
                    node_elements[nid].append(eid)
        
        # Find free nodes (nodes connected to no elements)
        free_nodes = [nid for nid, elems in node_elements.items() if not elems]
        
        # Find elements with missing nodes
        missing_nodes = []
        for eid, elem in model.elements.items():
            for nid in elem.nodes:
                if nid not in model.nodes:
                    missing_nodes.append({"element": eid, "missing_node": nid})
        
        return {
            "free_nodes": len(free_nodes),
            "free_node_ids": free_nodes[:10],  # First 10
            "missing_node_references": len(missing_nodes),
            "missing_node_details": missing_nodes[:10]
        }
