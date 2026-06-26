"""Dump readable text from the latest Namecheap email to find the code."""
import json, re, sys
from pathlib import Path

d = Path(r"C:\Users\jhusband\.claude\projects\C--Users-jhusband-Documents-claude\46ca764b-b5c0-4464-af67-7803f5d697d7\tool-results")
files = sorted(d.glob("mcp-claude_ai_Gmail-get_thread-*.txt"), key=lambda f: f.stat().st_mtime)
with open(files[-1], 'r', encoding='utf-8') as fp:
    data = json.load(fp)
msgs = sorted(data['messages'], key=lambda m: m.get('date', ''), reverse=True)
last = msgs[0]
html = last.get('htmlBody', '')
print(f"Newest message: {last.get('date')}")
print(f"htmlBody length: {len(html)}")

# Strip HTML tags to get text
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
# Decode entities
import html as ihtml
text = ihtml.unescape(text)

print(f"Stripped text length: {len(text)}")
out = Path(r"C:\Users\jhusband\AppData\Local\Temp\email_body.txt")
with open(out, 'w', encoding='utf-8') as fp:
    fp.write("--- TEXT (after first 'Hello' or 'verification') ---\n")
    idx_h = text.find('Hello')
    idx_v = text.lower().find('verification')
    cands = [i for i in (idx_h, idx_v) if i >= 0]
    idx = min(cands) if cands else 3000
    fp.write(text[idx:idx+2000] + "\n")
    fp.write("\n--- DIGITS WITH CONTEXT ---\n")
    for m in re.finditer(r'[0-9]{4,8}', text):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        fp.write(f"  ...{text[start:end]}...\n")
print(f"Wrote to {out}")
