"""Click the 'Didn't get the code?' button to trigger a fresh 2FA email."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        for page in ctx.pages:
            if "namecheap.com" in page.url:
                try:
                    await page.locator('button:has-text("Didn\'t get the code?")').first.click(timeout=5000)
                    print("Clicked 'Didn\\'t get the code?'")
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots\after-resend.png", full_page=True)
                except Exception as e:
                    print(f"Click failed: {e}")
                return
        print("No namecheap tab found")

asyncio.run(main())
