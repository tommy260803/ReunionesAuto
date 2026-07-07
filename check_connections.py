import json

def check_connections(filepath):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    nodes = {n["name"]: n for n in data["nodes"]}
    print(f"\n=== {filepath} ===")
    if "connections" in data:
        for conn_node, conns in data["connections"].items():
            if conn_node not in nodes:
                print(f"  ERROR: Connection from unknown node: '{conn_node}'")
            if "main" in conns:
                for main_idx, outputs in enumerate(conns["main"]):
                    if outputs:
                        for out in outputs:
                            target = out["node"]
                            if target not in nodes:
                                print(f"  ERROR: '{conn_node}' -> unknown node '{target}'")
    print(f"  Nodes ({len(nodes)}): {list(nodes.keys())}")

check_connections("json n8n/AsistenteIA1.json")
check_connections("json n8n/resumen_virtual.json")
check_connections("json n8n/resumen_presencial.json")
