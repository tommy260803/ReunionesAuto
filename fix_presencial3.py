import json

with open("json n8n/resumen_presencial.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for node in data["nodes"]:
    if node["name"] == "Groq API":
        body = node["parameters"]["jsonBody"]
        
        # The template should have: "content": {{ JSON.stringify($json.contexto) }}
        # Find the user message and fix the content field
        # First, let's identify the correct template by finding the problematic section
        # In the template (after JSON parsing), the issue is:
        # ..."user",\n      \              "content\": {{ JSON.stringify(...)}}
        # Should be:
        # ..."user",\n      "content": {{ JSON.stringify(...)}}
        
        # Fix: replace the bad pattern in the template string
        # The pattern is: stray backslash + spaces then "content\"
        # Replace with: "content" (without stray backslash and cleaned spacing)
        
        import re
        
        # Find the pattern in the body template
        print("Before fix:")
        idx = body.find("JSON.stringify($json.contexto)")
        if idx > 0:
            print(repr(body[idx-50:idx+60]))
        
        # The body is a template string like: "={\n ... "content": {{ JSON.stringify(...) }}\n}"
        # We need to find "content" near the user message, not the system message
        
        # Find the LAST occurrence of "content" (the user message is after system message)
        # Actually, let's find the user role first
        user_role_idx = body.rfind('"user"')
        print(f"\n'user' role at: {user_role_idx}")
        if user_role_idx > 0:
            print(repr(body[user_role_idx:user_role_idx+100]))
        
        # Find "content": right after "user"
        content_field_idx = body.find('content"', user_role_idx)
        print(f"\n'content\" field at: {content_field_idx}")
        if content_field_idx > 0:
            print(repr(body[content_field_idx-10:content_field_idx+100]))
        
        # Now fix by replacing everything from the content field to JSON.stringify
        # The problem is:   \              "content\": {{ JSON.stringify(...) }}
        # Should be:        "content": {{ JSON.stringify(...) }}
        
        # Find the exact bad pattern
        # Pattern: comma, newline, indent, stray-backslash, spaces, "content\"
        old_pattern = r'\n      \\[ ]+"content\\"'
        match = re.search(old_pattern, body[user_role_idx:user_role_idx+100])
        if match:
            print(f"\nFound bad pattern: {repr(match.group())}")
            
        break

print("\n=== Writing fixed file ===")

# Manually construct the correct jsonBody for the Groq API node
# The correct template (after JSON parsing) should be:
# ..."user",\n      "content": {{ JSON.stringify($json.contexto) }}\n    }\n  ],...

for node in data["nodes"]:
    if node["name"] == "Groq API":
        body = node["parameters"]["jsonBody"]
        
        # Find the problematic section and replace it
        # Step 1: Find what's between "role": "user", and JSON.stringify
        user_idx = body.rfind('"role": "user"')
        if user_idx == -1:
            user_idx = body.rfind('"role": \\"user\\"')
        
        js_idx = body.find("JSON.stringify($json.contexto)", user_idx)
        
        # Get the section between them
        between = body[user_idx+len('"role": "user"'):js_idx]
        print(f"\nSection between 'user' and JSON.stringify:")
        print(repr(between))
        
        # Now fix it: the section should be: ,\n      "content": {{ 
        # Remove stray backslash and normalize
        
        # Find the actual fix pattern
        for i, ch in enumerate(between):
            if ch == '\\':
                print(f"  Stray backslash at index {i} in section")
        
        # Replace the bad section
        # The correct section should be: ,\n      "content": {{ 
        correct_section = ',\\n      "content": {{ '
        
        old_section = between
        # Clean up - remove all stray backslashes that aren't part of \n, \\, \", etc.
        # In the template string, the correct format after the user role is:
        # ,<newline><spaces>"content": {{ JSON.stringify(...) }}
        
        cleaned = ',\\n      "content": {{ '
        new_body = body[:user_idx+len('"role": "user"')] + cleaned + body[js_idx:]
        
        print(f"\nNew body around fix:")
        fix_idx = new_body.find("JSON.stringify($json.contexto)")
        print(repr(new_body[fix_idx-40:fix_idx+60]))
        
        node["parameters"]["jsonBody"] = new_body
        break

with open("json n8n/resumen_presencial.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nFile written!")

# Validate
with open("json n8n/resumen_presencial.json", "r", encoding="utf-8") as f:
    json.load(f)
print("JSON is valid!")
