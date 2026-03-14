import re

def check_qml_braces(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple tokenizer to handle strings and comments
    tokens = []
    i = 0
    while i < len(content):
        if content[i:i+2] == '//':
            # Skip line comment
            i = content.find('\n', i)
            if i == -1: break
        elif content[i:i+2] == '/*':
            # Skip block comment
            i = content.find('*/', i)
            if i == -1: break
            i += 2
        elif content[i] == '"':
            # Skip string
            i = content.find('"', i + 1)
            if i == -1: break
            i += 1
        elif content[i] == "'":
            # Skip char/single string
            i = content.find("'", i + 1)
            if i == -1: break
            i += 1
        elif content[i] == '{' or content[i] == '}':
            tokens.append((content[i], i))
            i += 1
        else:
            i += 1

    stack = []
    for t, pos in tokens:
        if t == '{':
            stack.append(pos)
        else:
            if not stack:
                print(f"Extra '}}' found at position {pos}")
            else:
                stack.pop()
    
    if stack:
        for pos in stack:
            # Find line number
            line_num = content.count('\n', 0, pos) + 1
            snippet = content[pos:pos+40].replace('\n', ' ')
            print(f"Unclosed '{{' opened at line {line_num}: {snippet}...")
    else:
        print("Braces are balanced (ignoring strings/comments)")

check_qml_braces(r'f:\00_CHRISTIAN\00_PROJECTS\EmuManager\ui\qml\views\Dashboard.qml')
