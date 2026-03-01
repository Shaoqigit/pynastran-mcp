"""
OP2 Tools for MCP Server

Handles all OP2 result file related operations.
"""

import json
import logging
import numpy as np
from typing import Optional

# Disable pyNastran logging before import
logging.disable(logging.CRITICAL)

from pyNastran.op2.op2 import OP2, read_op2


class Op2Tools:
    """Tools for working with Nastran OP2 result files."""
    
    def __init__(self):
        """Initialize OP2 tools."""
        self._cache = {}
    
    async def read_op2(self, filepath: str, combine: bool = True) -> str:
        """
        Read an OP2 file and return summary.
        
        Args:
            filepath: Path to OP2 file
            combine: Combine results flag
            
        Returns:
            JSON string with result summary
        """
        try:
            model = read_op2(filepath, combine=combine)
            self._cache[filepath] = model
            
            summary = {
                "filepath": filepath,
                "grid_point_weight": self._get_grid_point_weight(model),
                "result_cases": self._get_result_cases_list(model),
                "available_results": self._get_available_results(model)
            }
            
            return json.dumps(summary, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_result_cases(self, filepath: str) -> str:
        """
        Get list of available result cases.
        
        Args:
            filepath: Path to OP2 file
            
        Returns:
            List of result cases as JSON
        """
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_op2(filepath)
                self._cache[filepath] = model
            
            cases = self._get_result_cases_list(model)
            
            return json.dumps({
                "filepath": filepath,
                "result_cases": cases,
                "count": len(cases)
            }, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_stress(self, filepath: str, element_type: Optional[str] = None, 
                        subcase_id: int = 1) -> str:
        """
        Extract stress results.
        
        Args:
            filepath: Path to OP2 file
            element_type: Filter by element type (e.g., 'CQUAD4')
            subcase_id: Subcase ID
            
        Returns:
            Stress results as JSON
        """
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_op2(filepath)
                self._cache[filepath] = model
            
            stresses = []
            
            # Access stress results from op2_results
            if hasattr(model, 'op2_results') and model.op2_results:
                stress_results = model.op2_results.stress
                
                # Map element types to result attributes
                type_mapping = {
                    'CQUAD4': 'cquad4_stress',
                    'CTRIA3': 'ctria3_stress',
                    'CTETRA': 'ctetra_stress',
                    'CHEXA': 'chexa_stress',
                    'CBAR': 'cbar_stress',
                    'CROD': 'crod_stress',
                }
                
                if element_type and element_type in type_mapping:
                    attr_name = type_mapping[element_type]
                    if hasattr(stress_results, attr_name):
                        result_obj = getattr(stress_results, attr_name)
                        if result_obj:
                            stresses = self._extract_stress_data(result_obj, subcase_id)
                else:
                    # Get all stress types
                    for attr_name in dir(stress_results):
                        if 'stress' in attr_name and not attr_name.startswith('_'):
                            result_obj = getattr(stress_results, attr_name)
                            if result_obj:
                                stress_data = self._extract_stress_data(result_obj, subcase_id)
                                if stress_data:
                                    stresses.extend(stress_data)
            
            # Calculate statistics
            if stresses:
                von_mises = [s.get('von_mises', 0) for s in stresses if 'von_mises' in s]
                stats = {
                    "max": max(von_mises) if von_mises else None,
                    "min": min(von_mises) if von_mises else None,
                    "mean": sum(von_mises) / len(von_mises) if von_mises else None
                }
            else:
                stats = {}
            
            return json.dumps({
                "filepath": filepath,
                "subcase_id": subcase_id,
                "element_type": element_type,
                "stresses": stresses[:50],  # Limit output
                "stats": stats,
                "total_count": len(stresses)
            }, indent=2, default=self._numpy_to_python)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_displacement(self, filepath: str, subcase_id: int = 1) -> str:
        """
        Extract displacement results.
        
        Args:
            filepath: Path to OP2 file
            subcase_id: Subcase ID
            
        Returns:
            Displacement results as JSON
        """
        try:
            if filepath in self._cache:
                model = self._cache[filepath]
            else:
                model = read_op2(filepath)
                self._cache[filepath] = model
            
            displacements = []
            
            # Access displacement results from op2_results
            if hasattr(model, 'op2_results') and model.op2_results:
                op2_results = model.op2_results
                
                # Check for displacements in different possible locations
                disp_results = None
                if hasattr(op2_results, 'displacements') and op2_results.displacements:
                    disp_results = op2_results.displacements
                elif hasattr(model, 'displacements') and model.displacements:
                    disp_results = model.displacements
                
                if disp_results:
                    for key, disp in disp_results.items():
                        # Extract displacement data
                        data = {
                            "subcase": str(key),
                            "node_count": len(disp.node_gridtype) if hasattr(disp, 'node_gridtype') else 0,
                        }
                        
                        if hasattr(disp, 'data') and disp.data is not None:
                            # Get magnitude
                            disp_data = disp.data
                            if len(disp_data.shape) == 3:  # (nresults, nnodes, 6)
                                # Take first result
                                disp_2d = disp_data[0]
                                magnitudes = [float(x) for x in np.sqrt(np.sum(disp_2d[:, :3]**2, axis=1))]
                                data["max_magnitude"] = max(magnitudes) if magnitudes else None
                                data["min_magnitude"] = min(magnitudes) if magnitudes else None
                                data["mean_magnitude"] = sum(magnitudes) / len(magnitudes) if magnitudes else None
                        
                        displacements.append(data)
            
            return json.dumps({
                "filepath": filepath,
                "subcase_id": subcase_id,
                "displacements": displacements
            }, indent=2, default=self._numpy_to_python)
            
        except Exception as e:
            import traceback
            return json.dumps({"error": str(e), "traceback": traceback.format_exc()})
    
    def _get_grid_point_weight(self, model: OP2) -> Optional[dict]:
        """Get grid point weight if available."""
        if hasattr(model, 'grid_point_weight') and model.grid_point_weight:
            gpw = model.grid_point_weight
            return {
                "mass": float(gpw.mass.sum()) if hasattr(gpw, 'mass') else None,
                "center_of_gravity": list(gpw.cg) if hasattr(gpw, 'cg') else None
            }
        return None
    
    def _get_result_cases_list(self, model: OP2) -> list:
        """Get list of result cases."""
        cases = []
        
        # Get from displacements
        if hasattr(model, 'op2_results') and model.op2_results:
            if model.op2_results.displacements:
                for key in model.op2_results.displacements.keys():
                    cases.append({
                        "type": "displacement",
                        "key": str(key)
                    })
            
            # Get from stress
            if model.op2_results.stress:
                stress = model.op2_results.stress
                for attr in dir(stress):
                    if 'stress' in attr and not attr.startswith('_'):
                        obj = getattr(stress, attr)
                        if obj:
                            cases.append({
                                "type": "stress",
                                "element_type": attr.replace('_stress', '')
                            })
        
        return cases
    
    def _get_available_results(self, model: OP2) -> list:
        """Get list of available result types."""
        results = []
        
        if hasattr(model, 'op2_results') and model.op2_results:
            op2_results = model.op2_results
            
            if hasattr(op2_results, 'displacements') and op2_results.displacements:
                results.append("displacements")
            if hasattr(op2_results, 'velocity') and op2_results.velocity:
                results.append("velocity")
            if hasattr(op2_results, 'acceleration') and op2_results.acceleration:
                results.append("acceleration")
            if hasattr(op2_results, 'stress') and op2_results.stress:
                results.append("stress")
            if hasattr(op2_results, 'strain') and op2_results.strain:
                results.append("strain")
            if hasattr(op2_results, 'force') and op2_results.force:
                results.append("force")
            if hasattr(op2_results, 'strain_energy') and op2_results.strain_energy:
                results.append("strain_energy")
            if hasattr(op2_results, 'grid_point_forces') and op2_results.grid_point_forces:
                results.append("grid_point_forces")
        
        return results
    
    def _extract_stress_data(self, result_obj, subcase_id: int) -> list:
        """Extract stress data from result object."""
        stresses = []
        
        try:
            # Handle different result object structures
            if hasattr(result_obj, 'data') and result_obj.data is not None:
                data = result_obj.data
                
                # Get element IDs
                element_ids = []
                if hasattr(result_obj, 'element'):
                    element_ids = result_obj.element.tolist() if hasattr(result_obj.element, 'tolist') else list(result_obj.element)
                
                # Process data
                if len(data.shape) == 3:  # (nresults, nelements, ncomponents)
                    stress_array = data[0]  # First result
                    
                    for i, eid in enumerate(element_ids[:100]):  # Limit to 100
                        if i < len(stress_array):
                            row = stress_array[i]
                            stress_entry = {
                                "element_id": int(eid),
                                "von_mises": float(row[-1]) if len(row) > 0 else None
                            }
                            stresses.append(stress_entry)
        
        except Exception as e:
            print(f"Error extracting stress: {e}")
        
        return stresses
    
    def _numpy_to_python(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return str(obj)
