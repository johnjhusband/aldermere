"""Reload the Namecheap 2FA tab to trigger a fresh code send."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        for page in ctx.pages:
            if "namecheap.com" in page.url:
                print(f"Reloading: {page.url}")
                await page.reload(wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                print(f"After reload: {page.url}")
                await page.screenshot(path=r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots\live-2fa-reloaded.png", full_page=True)
                return
        print("No namecheap tab found")

asyncio.run(main())
