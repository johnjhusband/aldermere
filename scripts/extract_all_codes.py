"""Extract every 6-char alphanumeric code from all messages in the dump."""
import json, re
from pathlib import Path

d = Path(r"C:\Users\jhusband\.claude\projects\C--Users-jhusband-Documents-claude\46ca764b-b5c0-4464-af67-7803f5d697d7\tool-results")
files = sorted(d.glob("mcp-claude_ai_Gmail-get_thread-*.txt"), key=lambda f: f.stat().st_mtime)
import html as ihtml
with open(files[-1], 'r', encoding='utf-8') as fp:
    data = json.load(fp)
msgs = sorted(data['messages'], key=lambda m: m.get('date', ''), reverse=True)
print(f"Most recent file: {files[-1].name}")
print(f"Messages: {len(msgs)}\n")
for msg in msgs:
    html = msg.get('htmlBody', '')
    text = re.sub(r'<[^>]+>', ' ', html)
    text = ihtml.unescape(re.sub(r'\s+', ' ', text))
    # Look for the verification code phrase
    m = re.search(r'will expire in 30 minutes:\s*([a-f0-9]{6})', text, re.IGNORECASE)
    if not m:
        m = re.search(r'enable your new device[^:]*:\s*([a-f0-9]{6})', text, re.IGNORECASE)
    print(f"  {msg.get('date')}: code = {m.group(1) if m else 'NOT FOUND'}")
