import json

with open("json n8n/resumen_presencial.json", "rb") as f:
    d = f.read()

# Find the user message section
user_idx = d.find(b'"user"')
content_idx = d.find(b'content', user_idx)

print("User found at:", user_idx)
print("content found at:", content_idx)

# Show bytes between the comma after "user" and "content"
# Find the comma right before the content section
for i in range(content_idx-60, content_idx+10):
    ctx = d[i:i+40]
    if b'\\\\' in ctx and b'content' in ctx:
        print(f"Position {i}: {repr(d[i:i+50])}")
        print(f"  Hex: {' '.join(f'{b:02x}' for b in d[i:i+50])}")
        break

# Show the exact bytes before content
pre = d[content_idx-30:content_idx+10]
print(f"\nBytes before content: {repr(pre)}")
print(f"Hex: {' '.join(f'{b:02x}' for b in pre)}")

# The problem: after \\n + 6 spaces, there's a single \\ (0x5C) + 14 spaces + \"content\"
# In the bytes, this is: 0x5C, 0x20 x14, 0x5C, 0x22, 'content', 0x5C, 0x22

# Fix: replace the stray byte pattern
# Pattern to find: \\ + 14 spaces + \\"  (stray backslash + whitespace before the real \\")
stray_pattern = b'\\' + b' ' * 14 + b'\\"'
print(f"\nLooking for: {repr(stray_pattern)}")
print(f"Hex: {' '.join(f'{b:02x}' for b in stray_pattern)}")

if stray_pattern in d:
    print("FOUND! Replacing...")
    d = d.replace(stray_pattern, b'\\"')
    try:
        json.loads(d)
        print("JSON is now VALID!")
        with open("json n8n/resumen_presencial.json", "wb") as f:
            f.write(d)
        print("File written!")
    except json.JSONDecodeError as e:
        print(f"Still invalid: {e}")
        print(repr(d[e.pos-60:e.pos+60]))
else:
    print("Pattern not found.")
    print("Let me search for alternative patterns...")
    # Try finding the bytes differently
    # Look for bare backslash followed by many spaces
    for i in range(len(d)-50):
        if d[i:i+1] == b'\\':
            # Check if next 14+ chars are spaces
            space_count = 0
            j = i + 1
            while j < len(d) and d[j:j+1] == b' ':
                space_count += 1
                j += 1
            if space_count >= 10 and j < len(d) and d[j:j+1] == b'\\':
                print(f"Found stray backslash at byte {i}: {repr(d[i:i+30])}")
                print(f"  Hex: {' '.join(f'{b:02x}' for b in d[i:i+30])}")
                # Remove the stray backslash and spaces
                d = d[:i] + d[j:]
                print("Fixed!")
                try:
                    json.loads(d)
                    print("JSON is now VALID!")
                    with open("json n8n/resumen_presencial.json", "wb") as f:
                        f.write(d)
                    print("File written!")
                    break
                except json.JSONDecodeError as e:
                    print(f"Still invalid: {e}")
                    print(repr(d[e.pos-60:e.pos+60]))
                break
