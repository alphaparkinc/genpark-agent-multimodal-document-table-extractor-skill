from client import AgentDocumentTableExtractor
import json

extractor = AgentDocumentTableExtractor()
print("=== AGENT DOCUMENT TABLE EXTRACTOR BENCHMARK ===")
res = extractor.run_table_benchmark()
print(json.dumps(res, indent=2))
