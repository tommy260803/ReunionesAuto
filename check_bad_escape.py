import json

with open("json n8n/resumen_presencial.json", "rb") as f:
    data = f.read().decode("utf-8")

# Find the user message section
target = '{{ JSON.stringify($json.contexto) }}'
idx = data.find(target)
print("Found target at:", idx)

# Show 150 chars before target
start = max(0, idx - 150)
print("Context before:")
print(repr(data[start:idx]))
print("---")

# Show the target and after
end = min(len(data), idx + len(target) + 50)
print("Context after:")
print(repr(data[idx:end]))
print("---")

# Try to parse
try:
    json.loads(data)
    print("JSON is valid!")
except json.JSONDecodeError as e:
    print(f"JSON error at line {e.lineno}, col {e.colno}, pos {e.pos}")
    print(repr(data[max(0,e.pos-50):e.pos+50]))
