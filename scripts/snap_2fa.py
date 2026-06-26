"""Attach to running Chrome, find the Namecheap 2FA tab, snapshot it."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        for page in ctx.pages:
            if "namecheap.com" in page.url:
                print(f"Tab URL: {page.url}")
                print(f"Tab title: {await page.title()}")
                await page.screenshot(path=r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots\live-2fa-state.png", full_page=True)
                # Look for any visible error message
                body_text = await page.text_content("body") or ""
                # Search for typical error markers
                for needle in ("incorrect", "invalid", "expired", "again", "wrong", "Sign-in", "verify"):
                    idx = body_text.lower().find(needle.lower())
                    if idx >= 0:
                        print(f"  near '{needle}': ...{body_text[max(0,idx-40):idx+80]}...")
                # Inputs visible
                inputs = await page.eval_on_selector_all("input:not([type=hidden])", "els => els.map(e => ({name: e.name, type: e.type, id: e.id, placeholder: e.placeholder, value: (e.value || '').slice(0,20)}))")
                print(f"Visible inputs: {inputs}")
                return
        print("No namecheap tab found")

asyncio.run(main())
