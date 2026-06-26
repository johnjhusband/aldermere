"""Parse the MCP get_thread JSON dump and extract the latest 6-digit code."""
import json
import re
import sys
from pathlib import Path

def find_latest_code(path: str) -> str | None:
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    msgs = data.get('messages', [])
    if not msgs:
        return None
    # Sort by date descending
    msgs.sort(key=lambda m: m.get('date', ''), reverse=True)
    for msg in msgs:
        print(f"Trying message dated {msg.get('date')}, fields: {list(msg.keys())}")
        # Try every text field
        for k in ('plaintextBody', 'plainText', 'text', 'body', 'htmlBody', 'snippet'):
            v = msg.get(k)
            if not v:
                continue
            print(f"  field {k} len={len(v)}")
            # Look for typical code phrases first, then bare 6-digit
            for pattern in (
                r'verification code[^0-9]{0,200}([0-9]{6})',
                r'code[^0-9]{0,50}([0-9]{6})',
                r'>\s*([0-9]{6})\s*<',
                r'\b([0-9]{6})\b',
            ):
                m = re.search(pattern, v, re.IGNORECASE | re.DOTALL)
                if m:
                    print(f"  matched pattern {pattern!r} -> {m.group(1)}")
                    return m.group(1)
    return None

if __name__ == '__main__':
    p = sys.argv[1] if len(sys.argv) > 1 else None
    if not p:
        # Find the latest get_thread file
        d = Path(r"C:\Users\jhusband\.claude\projects\C--Users-jhusband-Documents-claude\46ca764b-b5c0-4464-af67-7803f5d697d7\tool-results")
        files = sorted(d.glob("mcp-claude_ai_Gmail-get_thread-*.txt"), key=lambda f: f.stat().st_mtime)
        if not files:
            print("No get_thread dumps found")
            sys.exit(2)
        p = str(files[-1])
        print(f"Using latest dump: {p}")
    code = find_latest_code(p)
    if code:
        print(f"CODE: {code}")
        sys.exit(0)
    print("No code found")
    sys.exit(1)
