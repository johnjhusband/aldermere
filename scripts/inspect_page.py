"""Dump all clickable elements on Namecheap 2FA page."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        for page in ctx.pages:
            if "namecheap.com" in page.url:
                links = await page.eval_on_selector_all("a, button", "els => els.filter(e => e.offsetParent !== null).map(e => ({tag: e.tagName, text: (e.innerText || '').trim().slice(0, 80), href: e.href || '', id: e.id, cls: e.className.slice(0,50)})).filter(o => o.text)")
                print("Visible buttons/links:")
                for l in links[:30]:
                    print(f"  {l}")
                # Also get visible text in case there's a clickable countdown text
                allspans = await page.eval_on_selector_all("span, div, p", "els => els.filter(e => e.offsetParent !== null && e.children.length === 0).map(e => (e.innerText || '').trim()).filter(t => t && t.length < 100 && /resend|send|code/i.test(t))")
                print("\nText matching 'resend|send|code':")
                for t in allspans[:15]:
                    print(f"  {t!r}")
                return
        print("No namecheap tab found")

asyncio.run(main())
