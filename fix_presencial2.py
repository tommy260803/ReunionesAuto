import json
import re

with open("json n8n/resumen_presencial.json", "r", encoding="utf-8") as f:
    raw = f.read()

# Check for the bad escape pattern: a single backslash followed by spaces then double-quote
# In the raw file, this is stored as: \ followed by spaces followed by "content\"
# But in JSON encoding, a backslash in the value is stored as \\ and " as \"

# Let's find the exact bad pattern
# The raw file should have: "content": {{ JSON.stringify($json.contexto) }}
# But it currently has: <stray backslash + spaces>"content": {{ JSON.stringify(...) }}

# Let's look for the pattern using a different approach
# Find the position of "JSON.stringify"
target = "JSON.stringify($json.contexto)"
idx = raw.find(target)
if idx >= 0:
    print(f"Found target at position {idx}")
    # Show 100 chars before
    before = raw[idx-100:idx]
    print("Before:", repr(before))
    print()
    # Show what's after
    after = raw[idx:idx+100]
    print("After:", repr(after))
    
    # The issue is probably raw[idx-1] being a stray quote or backslash
    # Let's check the exact content around where the content value should be
    
    # Find "content" before the target
    content_idx = raw.rfind('content"', idx-200, idx)
    print(f"\ncontent\" at {content_idx}")
    print(repr(raw[content_idx-20:content_idx+100]))
    
    # Find what's right before JSON.stringify
    # Check if there's a stray "\              " 
    # In JSON file encoding, this would be: \\              \"
    # Where \\ = literal backslash (escaped in JSON)
    # Then spaces
    # Then \" = literal double-quote (escaped in JSON)

else:
    print("Target not found!")
    # Searching for what's there instead
    target2 = "JSON.stringify"
    idx2 = raw.find(target2)
    if idx2 >= 0:
        print(f"Found JSON.stringify at {idx2}")
        print(repr(raw[idx2-100:idx2+100]))
    else:
        print("JSON.stringify not found either!")
        # Search for "content" near the user message
        for m in re.finditer('content', raw):
            pos = m.start()
            ctx = raw[pos-30:pos+80]
            if 'user' in ctx or 'role' in ctx:
                print(f"Found at {pos}: {repr(ctx)}")
