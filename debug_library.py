import sys

with open(r'f:\00_CHRISTIAN\00_PROJECTS\EmuManager\ui\qml\views\Library.qml', 'r', encoding='utf-8') as f:
    content = f.read()

open_braces = content.count('{')
close_braces = content.count('}')
print(f"Open: {open_braces}, Close: {close_braces}")

# Also check for unclosed strings
single_quotes = content.count("'")
double_quotes = content.count('"')
print(f"Single: {single_quotes}, Double: {double_quotes}")
