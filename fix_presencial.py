import json

with open("json n8n/resumen_presencial.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Find Groq API node and fix the jsonBody
for node in data["nodes"]:
    if node["name"] == "Groq API":
        body = node["parameters"]["jsonBody"]
        # The body template: the user message content should use JSON.stringify
        # and not have surrounding quotes since JSON.stringify adds them
        print("BEFORE fix (first 100 chars):", repr(body[:100]))
        print("BEFORE fix (last 100 chars):", repr(body[-100:]))
        
        # Find the user message content template and fix it
        # Old pattern: "content": "{{ $json.contexto }}"
        # New pattern: "content": {{ JSON.stringify($json.contexto) }}
        
        # Check what's there now
        if '{{ JSON.stringify($json.contexto) }}' in body:
            print("Already has JSON.stringify - good")
            # But verify the surrounding chars
            idx = body.find('{{ JSON.stringify($json.contexto) }}')
            print(f"Context: {repr(body[idx-30:idx+60])}")
        else:
            print("Does NOT have JSON.stringify")
            
        break

# Also check the otros nodes
for node in data["nodes"]:
    if "Groq API" in node.get("name", ""):
        print(f"\nNode '{node['name']}':")
        body = node["parameters"].get("jsonBody", "")
        if 'content"' in body:
            idx = body.rfind('"content"')
            print(f"  content context: {repr(body[idx:idx+150])}")

print("\n--- Checking all jsonBody for issues ---")
for node in data["nodes"]:
    params = node.get("parameters", {})
    for key, val in params.items():
        if "jsonBody" in key and isinstance(val, str):
            # Try to parse the template after replacing expressions
            # First check for any invalid escapes
            lines = val.split("\\n")
            for i, line in enumerate(lines):
                if "\\" in line:
                    # Check each backslash
                    parts = line.split("\\")
                    for j, part in enumerate(parts):
                        if part and not part.startswith(('"', 'n', '\\', 'u', 't', 'r')):
                            pass  # normal text after escape
            
            # Just check the raw content for issues
            if '\\              "' in val:
                print(f"  \\n  FOUND STRAY ESCAPE in node '{node['name']}'")
                print(f"  Context: {repr(val[val.find('\\\\              \"')-30:val.find('\\\\              \"')+50])}")
