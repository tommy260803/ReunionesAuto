import re

with open("json n8n/resumen_presencial.json", "r", encoding="utf-8") as f:
    raw = f.read()

# Find the bad pattern: a single backslash followed by spaces then "content"
# In the raw file, the bad sequence is typically:      \              "content\"
# Where \ is a bare backslash (invalid in JSON)

# Strategy: find the user message section and fix the content field

# Target: JSON.stringify($json.contexto)
target = "JSON.stringify($json.contexto)"
idx = raw.find(target)
print(f"Target at position {idx}")

# Show what's before
before = raw[idx-80:idx]
print(f"Before: {repr(before)}")

# The issue: the section between 'user"' and JSON.stringify has:
# ,\n      \              "content\": {{ 
# Should be: ,\n      "content": {{ 

# Find the pattern
# We need to find: a single backslash followed by spaces, then "content"
# In the raw file, this might appear as: \              "content\"
# where \ + spaces + "content\" has the stray \

# Find the user role
user_idx = raw.rfind('"user"', 0, idx)
print(f"'user' at {user_idx}")
print(f"After user: {repr(raw[user_idx:user_idx+100])}")

# The fix: find the pattern  \              "content\"  and replace with  "content"
# Actually, look at the exact characters

# Let's find what's between the comma after user role and "content":
between_idx = raw.find(',', user_idx)
print(f"Comma after user at {between_idx}")
section = raw[between_idx:idx]
print(f"Section: {repr(section)}")

# Now find the "content" string and the stray backslash
content_pos = section.find('"content"')
if content_pos == -1:
    content_pos = section.find('"content\\"')
print(f"content at offset {content_pos} in section")
print(f"  chars: {repr(section[max(0,content_pos-20):content_pos+30])}")

# The bad pattern is probably: \n      \              "content\"
# where there's a \ (backslash) before "content

# Let's fix by constructing the correct section
# Correct: ,\n      "content": {{ JSON.stringify($json.contexto) }}
correct_section = ',\\n      \\"content\\": {{ '

# Actually, I need to think about what the raw file SHOULD contain
# In the JSON file, the jsonBody value is a string.
# Inside that string, we want the template to be:
#   ,\n      "content": {{ JSON.stringify($json.contexto) }}
# 
# For this to be in the JSON file string value:
#   ,\\n      \\"content\\": {{ JSON.stringify($json.contexto) }}
# 
# Because:
#   \\n in JSON = literal \n (backslash + n) in the template
#   \\" in JSON = literal " in the template

# But the current file has:
#   ,\n      \              "content\": {{ JSON.stringify(...) }}
# After JSON parsing:
#   newline, 6 spaces, backslash, 14 spaces, double-quote, "content\", ...

# The correct file content should be:
#   ,\\n      \\"content\\": {{ JSON.stringify(...) }}
# After JSON parsing:
#   newline, 6 spaces, `\"`, "content", `\"`, colon, space, "{{ JSON.stringify(...) }}"

# So I need to replace the bad section with the correct escaped version
# The section starts after 'user",' and goes until the JSON.stringify target

# Find the exact start of the bad section
# In the file, after 'user",': ,\n      \              "content\": {{ JSON.stringify...
# First comma after user_idx
comma_after_user = raw.find(',', user_idx)
# Find the actual \n (newline) after the comma
# Actually, after 'user",', the next chars should be: comma
# Let's look at what follows

after_comma = raw[comma_after_user:comma_after_user+5]
print(f"\nAfter comma: {repr(after_comma)}")

# Find the "content" in the template (not the system message)
# We need to find the last "content" before target
content_pos = raw.rfind('"content"', user_idx, idx)
if content_pos == -1:
    content_pos = raw.rfind('content"', user_idx, idx)
if content_pos == -1:
    content_pos = raw.rfind('content', user_idx, idx)
print(f"\n'content' found at {content_pos}")

# Show full context from comma after user to JSON.stringify
ctx = raw[comma_after_user:idx+len(target)]
print(f"Full section to replace: {repr(ctx)}")

# Now, the correct JSON for this section should be:
# After JSON parsing, the template has:
#   ,\n      "content": {{ JSON.stringify($json.contexto) }}
# In the raw JSON file, this is:
#   ,\\n      \\"content\\": {{ JSON.stringify($json.contexto) }}

correct_inner = ',\\\n      \\"content\\": {{ '

# Let's construct the replacement
# from comma_after_user to idx (where JSON.stringify starts), inclusive
old_section = raw[comma_after_user:idx]
print(f"OLD section: {repr(old_section)}")
print(f"OLD length: {len(old_section)}")

# NEW section: correct JSON escaped template
new_section = ',\\n      \\"content\\": {{ '
print(f"NEW section: {repr(new_section)}")

# Replace
new_raw = raw[:comma_after_user] + new_section + raw[idx:]
print(f"\nAfter fix (context): {repr(new_raw[idx-40:idx+60])}")

# Validate JSON
try:
    import json
    json.loads(new_raw)
    print("\n✅ JSON is VALID!")
    
    # Write back
    with open("json n8n/resumen_presencial.json", "w", encoding="utf-8") as f:
        f.write(new_raw)
    print("✅ File written successfully!")
except json.JSONDecodeError as e:
    print(f"\n❌ JSON still invalid: {e}")
    # Show the area around the error
    print(repr(new_raw[e.pos-50:e.pos+50]))
