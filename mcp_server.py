import sys, json
from client import AgentDocumentTableExtractor

def handle_mcp():
    extractor = AgentDocumentTableExtractor()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps(extractor.run_table_benchmark(), indent=2))
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "initialize":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "genpark-agent-multimodal-document-table-extractor-skill", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }}
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [
                    {"name": "extract_tables_from_text", "description": "Extract tabular matrices from raw text.", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}}},
                    {"name": "table_to_markdown", "description": "Format table matrix as GFM Markdown.", "inputSchema": {"type": "object", "properties": {"rows": {"type": "array"}}}},
                    {"name": "run_table_benchmark", "description": "Run document table extractor benchmark.", "inputSchema": {"type": "object"}}
                ]}}
            elif method == "tools/call":
                tname = req.get("params", {}).get("name")
                args = req.get("params", {}).get("arguments", {})
                if tname == "extract_tables_from_text":
                    res = extractor.extract_tables_from_text(args.get("text", ""))
                elif tname == "table_to_markdown":
                    res = extractor.table_to_markdown(args.get("rows", []))
                else:
                    res = extractor.run_table_benchmark()
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    handle_mcp()
