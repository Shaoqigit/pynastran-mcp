#!/bin/bash
# Start pyNastran MCP Server in SSE mode
# Usage: ./start_sse_server.sh [PORT]

PORT=${1:-8080}

echo "🚀 Starting pyNastran MCP Server (SSE mode)"
echo "   Port: $PORT"
echo "   SSE Endpoint: http://localhost:$PORT/sse"
echo "   REST API: http://localhost:$PORT/api"
echo ""
echo "Available endpoints:"
echo "  - GET  /api/health"
echo "  - GET  /api/tools"
echo "  - POST /api/bdf/read"
echo "  - POST /api/bdf/info"
echo "  - POST /api/bdf/quality"
echo "  - POST /api/bdf/bounds"
echo "  - POST /api/op2/read"
echo "  - POST /api/report"
echo ""
echo "Press Ctrl+C to stop"
echo "==========================================="

pynastran-mcp --transport sse --port $PORT
