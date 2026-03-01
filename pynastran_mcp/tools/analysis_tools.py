"""
Analysis Tools for MCP Server

Handles report generation and advanced analysis.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Disable pyNastran logging before import
logging.disable(logging.CRITICAL)

from pyNastran.bdf.bdf import read_bdf
from pyNastran.op2.op2 import read_op2


class AnalysisTools:
    """Tools for analysis and report generation."""
    
    def __init__(self):
        """Initialize analysis tools."""
        pass
    
    async def generate_report(self, bdf_path: str, op2_path: str = None, 
                             output_path: str = None) -> str:
        """
        Generate comprehensive analysis report.
        
        Args:
            bdf_path: Path to BDF file
            op2_path: Path to OP2 file (optional)
            output_path: Path for output report
            
        Returns:
            Report summary as JSON
        """
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "bdf_file": bdf_path,
                "op2_file": op2_path,
                "sections": []
            }
            
            # Read BDF model
            bdf_model = read_bdf(bdf_path, validate=True)
            
            # Model Summary Section
            model_summary = {
                "title": "Model Summary",
                "content": {
                    "nodes": len(bdf_model.nodes),
                    "elements": len(bdf_model.elements),
                    "materials": len(bdf_model.materials),
                    "properties": len(bdf_model.properties),
                    "loads": len(bdf_model.loads),
                    "constraints": len(bdf_model.spcs) + len(bdf_model.mpcs)
                }
            }
            report["sections"].append(model_summary)
            
            # Element Breakdown
            element_types = {}
            for elem in bdf_model.elements.values():
                etype = elem.type
                element_types[etype] = element_types.get(etype, 0) + 1
            
            report["sections"].append({
                "title": "Element Breakdown",
                "content": element_types
            })
            
            # Material Summary
            materials = []
            for mid, mat in bdf_model.materials.items():
                mat_info = {"id": mid, "type": mat.type}
                if hasattr(mat, 'e'):
                    mat_info["E"] = mat.e
                if hasattr(mat, 'nu'):
                    mat_info["nu"] = mat.nu
                if hasattr(mat, 'rho'):
                    mat_info["rho"] = mat.rho
                materials.append(mat_info)
            
            report["sections"].append({
                "title": "Materials",
                "content": materials
            })
            
            # Results Analysis (if OP2 provided)
            if op2_path:
                try:
                    op2_model = read_op2(op2_path)
                    
                    results_summary = {
                        "title": "Results Summary",
                        "content": {}
                    }
                    
                    # Displacement results
                    if hasattr(op2_model, 'op2_results') and op2_model.op2_results:
                        ors = op2_model.op2_results
                        
                        if ors.displacements:
                            results_summary["content"]["displacements"] = {
                                "cases": len(ors.displacements)
                            }
                        
                        if ors.stress:
                            stress_types = [attr for attr in dir(ors.stress) 
                                          if 'stress' in attr and not attr.startswith('_')]
                            results_summary["content"]["stress_types"] = stress_types
                        
                        if ors.strain:
                            results_summary["content"]["strain_available"] = True
                        
                        if ors.grid_point_forces:
                            results_summary["content"]["grid_point_forces"] = True
                    
                    report["sections"].append(results_summary)
                    
                    # Grid Point Weight
                    if hasattr(op2_model, 'grid_point_weight') and op2_model.grid_point_weight:
                        gpw = op2_model.grid_point_weight
                        report["sections"].append({
                            "title": "Grid Point Weight",
                            "content": {
                                "mass": float(gpw.mass.sum()) if hasattr(gpw, 'mass') else None,
                                "center_of_gravity": list(gpw.cg) if hasattr(gpw, 'cg') else None
                            }
                        })
                
                except Exception as e:
                    report["sections"].append({
                        "title": "Results Error",
                        "content": {"error": str(e)}
                    })
            
            # Write report to file
            if output_path:
                report_text = self._format_report_text(report)
                Path(output_path).write_text(report_text, encoding='utf-8')
                report["output_path"] = output_path
            
            return json.dumps(report, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _format_report_text(self, report: dict) -> str:
        """Format report as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("NASTRAN ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {report['generated_at']}")
        lines.append(f"BDF File: {report['bdf_file']}")
        if report.get('op2_file'):
            lines.append(f"OP2 File: {report['op2_file']}")
        lines.append("")
        
        for section in report["sections"]:
            lines.append("-" * 80)
            lines.append(section["title"].upper())
            lines.append("-" * 80)
            
            content = section["content"]
            
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        lines.append(f"\n{key}:")
                        for k, v in value.items():
                            lines.append(f"  {k}: {v}")
                    elif isinstance(value, list):
                        lines.append(f"\n{key}:")
                        for item in value[:20]:  # Limit to 20 items
                            if isinstance(item, dict):
                                lines.append(f"  - {item}")
                            else:
                                lines.append(f"  - {item}")
                        if len(value) > 20:
                            lines.append(f"  ... and {len(value) - 20} more")
                    else:
                        lines.append(f"{key}: {value}")
            
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        lines.append(f"  {item}")
                    else:
                        lines.append(f"  - {item}")
            
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
