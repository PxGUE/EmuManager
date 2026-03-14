with open(r'f:\00_CHRISTIAN\00_PROJECTS\EmuManager\ui\qml\views\Dashboard.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    for char in line:
        if char == '{':
            stack.append(i + 1)
        elif char == '}':
            if not stack:
                print(f"Extra closing brace at line {i+1}")
            else:
                stack.pop()

if stack:
    print(f"Unclosed braces opened at lines: {stack}")
else:
    print("All braces balanced")
