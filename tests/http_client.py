#!/usr/bin/env python3
"""
HTTP MCP Client for pyNastran

A simple HTTP client for testing pyNastran MCP Server via SSE transport.

Usage:
    # First, start the MCP server with SSE transport:
    pynastran-mcp --transport sse --port 8080
    
    # Then run this client:
    python http_client.py
    
    # Or test specific endpoints:
    python http_client.py --read-bdf /path/to/model.bdf
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Optional, Any
import aiohttp


class HTTPMCPClient:
    """HTTP MCP Client for pyNastran."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """Initialize HTTP MCP client.
        
        Args:
            base_url: Base URL of MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.message_endpoint: Optional[str] = None
    
    async def connect(self):
        """Connect to MCP server via SSE."""
        self.session = aiohttp.ClientSession()
        
        # Connect to SSE endpoint
        async with self.session.get(f"{self.base_url}/sse") as response:
            if response.status != 200:
                raise ConnectionError(f"Failed to connect: {response.status}")
            
            # Read the endpoint from SSE stream
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('event: endpoint'):
                    # Next line contains the data
                    pass
                elif line.startswith('data:'):
                    self.message_endpoint = line[5:].strip()
                    print(f"✅ Connected to MCP server at {self.base_url}")
                    print(f"   Message endpoint: {self.message_endpoint}")
                    break
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session:
            await self.session.close()
            print("✅ Disconnected from MCP server")
    
    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Call a tool via HTTP.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if not self.session or not self.message_endpoint:
            raise RuntimeError("Not connected to server")
        
        # Prepare JSON-RPC request
        request_id = 1
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        # Send request
        url = f"{self.base_url}{self.message_endpoint}"
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                raise RuntimeError(f"Request failed: {response.status}")
            
            result = await response.json()
            return result.get("result", {})
    
    async def read_bdf(self, filepath: str) -> dict:
        """Read BDF file."""
        result = await self.call_tool("read_bdf", {"filepath": filepath})
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def get_model_info(self, filepath: str) -> dict:
        """Get detailed model information."""
        result = await self.call_tool("get_model_info", {"filepath": filepath})
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def get_nodes(self, filepath: str, node_ids: list = None) -> dict:
        """Get node information."""
        args = {"filepath": filepath}
        if node_ids:
            args["node_ids"] = node_ids
        result = await self.call_tool("get_nodes", args)
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def get_elements(self, filepath: str, element_type: str = None) -> dict:
        """Get element information."""
        args = {"filepath": filepath}
        if element_type:
            args["element_type"] = element_type
        result = await self.call_tool("get_elements", args)
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def check_mesh_quality(self, filepath: str) -> dict:
        """Check mesh quality."""
        result = await self.call_tool("check_mesh_quality", {"filepath": filepath})
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def get_model_bounds(self, filepath: str) -> dict:
        """Get model bounds."""
        result = await self.call_tool("get_model_bounds", {"filepath": filepath})
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def read_op2(self, filepath: str) -> dict:
        """Read OP2 file."""
        result = await self.call_tool("read_op2", {"filepath": filepath})
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def get_displacement(self, filepath: str, subcase_id: int = 1) -> dict:
        """Get displacement results."""
        result = await self.call_tool("get_displacement", {
            "filepath": filepath,
            "subcase_id": subcase_id
        })
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result
    
    async def generate_report(self, bdf_path: str, op2_path: str = None, 
                             output_path: str = None) -> dict:
        """Generate analysis report."""
        args = {"bdf_path": bdf_path, "output_path": output_path or "/tmp/report.txt"}
        if op2_path:
            args["op2_path"] = op2_path
        result = await self.call_tool("generate_report", args)
        if result.get("content"):
            return json.loads(result["content"][0]["text"])
        return result


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


async def interactive_mode(client: HTTPMCPClient):
    """Run interactive mode."""
    print_header("pyNastran HTTP MCP Client - Interactive Mode")
    print("\nAvailable commands:")
    print("  read_bdf <path>              - Read BDF file")
    print("  get_model_info <path>        - Get model info")
    print("  get_nodes <path> [ids...]    - Get nodes")
    print("  get_elements <path> [type]   - Get elements")
    print("  check_quality <path>         - Check mesh quality")
    print("  get_bounds <path>            - Get model bounds")
    print("  read_op2 <path>              - Read OP2 file")
    print("  get_disp <path> [subcase]    - Get displacements")
    print("  generate_report <bdf> [op2]  - Generate report")
    print("  test_all                     - Run all tests")
    print("  quit                         - Exit")
    print()
    
    while True:
        try:
            command = input(f"{Colors.BLUE}http-mcp>{Colors.ENDC} ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "quit":
                break
            
            elif cmd == "read_bdf":
                if len(args) < 1:
                    print_error("Usage: read_bdf <filepath>")
                    continue
                print_info(f"Reading BDF: {args[0]}")
                result = await client.read_bdf(args[0])
                print(json.dumps(result, indent=2))
            
            elif cmd == "get_model_info":
                if len(args) < 1:
                    print_error("Usage: get_model_info <filepath>")
                    continue
                print_info(f"Getting model info: {args[0]}")
                result = await client.get_model_info(args[0])
                print(json.dumps(result, indent=2))
            
            elif cmd == "get_nodes":
                if len(args) < 1:
                    print_error("Usage: get_nodes <filepath> [node_ids...]")
                    continue
                filepath = args[0]
                node_ids = [int(x) for x in args[1:]] if len(args) > 1 else None
                print_info(f"Getting nodes from: {filepath}")
                result = await client.get_nodes(filepath, node_ids)
                print(json.dumps(result, indent=2))
            
            elif cmd == "get_elements":
                if len(args) < 1:
                    print_error("Usage: get_elements <filepath> [element_type]")
                    continue
                filepath = args[0]
                elem_type = args[1] if len(args) > 1 else None
                print_info(f"Getting elements from: {filepath}")
                result = await client.get_elements(filepath, elem_type)
                print(json.dumps(result, indent=2))
            
            elif cmd == "check_quality":
                if len(args) < 1:
                    print_error("Usage: check_quality <filepath>")
                    continue
                print_info(f"Checking mesh quality: {args[0]}")
                result = await client.check_mesh_quality(args[0])
                print(json.dumps(result, indent=2))
            
            elif cmd == "get_bounds":
                if len(args) < 1:
                    print_error("Usage: get_bounds <filepath>")
                    continue
                print_info(f"Getting model bounds: {args[0]}")
                result = await client.get_model_bounds(args[0])
                print(json.dumps(result, indent=2))
            
            elif cmd == "read_op2":
                if len(args) < 1:
                    print_error("Usage: read_op2 <filepath>")
                    continue
                print_info(f"Reading OP2: {args[0]}")
                result = await client.read_op2(args[0])
                print(json.dumps(result, indent=2))
            
            elif cmd == "get_disp":
                if len(args) < 1:
                    print_error("Usage: get_disp <filepath> [subcase_id]")
                    continue
                filepath = args[0]
                subcase = int(args[1]) if len(args) > 1 else 1
                print_info(f"Getting displacements from: {filepath}")
                result = await client.get_displacement(filepath, subcase)
                print(json.dumps(result, indent=2))
            
            elif cmd == "generate_report":
                if len(args) < 1:
                    print_error("Usage: generate_report <bdf_path> [op2_path]")
                    continue
                bdf_path = args[0]
                op2_path = args[1] if len(args) > 1 else None
                print_info(f"Generating report...")
                result = await client.generate_report(bdf_path, op2_path)
                print(json.dumps(result, indent=2))
            
            elif cmd == "test_all":
                await run_all_tests(client)
            
            else:
                print_error(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print_error(f"Error: {e}")


async def run_all_tests(client: HTTPMCPClient, models_dir: Path = None):
    """Run comprehensive tests."""
    print_header("Running Comprehensive Tests via HTTP")
    
    if models_dir is None:
        models_dir = Path("/home/shaoqi/Documents/01_Develop/wpyNastran/pyNastran/models")
    
    test_models = [
        ("sol_101_elements/static_solid_shell_bar.bdf", "Solid/Shell/Bar"),
        ("unit/pload4/cquad4.bdf", "CQUAD4"),
        ("unit/pload4/chexa.bdf", "CHEXA"),
    ]
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    for model_path, description in test_models:
        full_path = models_dir / model_path
        if not full_path.exists():
            print_warning(f"Model not found: {model_path}")
            continue
        
        print(f"\n{Colors.BOLD}Testing {description}:{Colors.ENDC}")
        print(f"  File: {model_path}")
        
        try:
            # Test 1: Read BDF
            result = await client.read_bdf(str(full_path))
            if "error" in result:
                print_error(f"  read_bdf failed: {result['error']}")
                results["failed"] += 1
            else:
                print_success(f"  read_bdf: {result.get('n_nodes')} nodes, {result.get('n_elements')} elements")
                results["passed"] += 1
            
            # Test 2: Get model info
            result = await client.get_model_info(str(full_path))
            if "error" in result:
                print_error(f"  get_model_info failed")
                results["failed"] += 1
            else:
                print_success(f"  get_model_info: OK")
                results["passed"] += 1
            
            # Test 3: Check mesh quality
            result = await client.check_mesh_quality(str(full_path))
            if "error" in result:
                print_error(f"  check_mesh_quality failed")
                results["failed"] += 1
            else:
                print_success(f"  check_mesh_quality: OK")
                results["passed"] += 1
                
        except Exception as e:
            print_error(f"  Exception: {e}")
            results["failed"] += 1
    
    # Test OP2 if available
    op2_path = models_dir / "sol_101_elements/static_solid_shell_bar.op2"
    if op2_path.exists():
        print(f"\n{Colors.BOLD}Testing OP2:{Colors.ENDC}")
        try:
            result = await client.read_op2(str(op2_path))
            if "error" in result:
                print_error(f"  read_op2 failed: {result['error']}")
                results["failed"] += 1
            else:
                print_success(f"  read_op2: OK")
                results["passed"] += 1
                
        except Exception as e:
            print_error(f"  Exception: {e}")
            results["failed"] += 1
    
    # Print summary
    print_header("Test Summary")
    print(f"  {Colors.GREEN}Passed: {results['passed']}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {results['failed']}{Colors.ENDC}")
    print(f"  Total: {results['passed'] + results['failed']}")
    
    success_rate = results['passed'] / (results['passed'] + results['failed']) * 100 if (results['passed'] + results['failed']) > 0 else 0
    print(f"\n  Success Rate: {success_rate:.1f}%")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="pyNastran HTTP MCP Client")
    parser.add_argument("--url", default="http://localhost:8080", 
                       help="MCP server URL (default: http://localhost:8080)")
    parser.add_argument("--test-all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--read-bdf", metavar="PATH",
                       help="Read specific BDF file")
    
    args = parser.parse_args()
    
    # Create client
    client = HTTPMCPClient(base_url=args.url)
    
    try:
        # Connect to server
        await client.connect()
        
        if args.test_all:
            # Run all tests
            await run_all_tests(client)
        elif args.read_bdf:
            # Read specific BDF
            print_info(f"Reading BDF: {args.read_bdf}")
            result = await client.read_bdf(args.read_bdf)
            print(json.dumps(result, indent=2))
        else:
            # Interactive mode
            await interactive_mode(client)
            
    except Exception as e:
        print_error(f"Failed to connect to MCP server: {e}")
        print_info("Make sure the server is running with: pynastran-mcp --transport sse --port 8080")
        return 1
    finally:
        # Disconnect
        await client.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
