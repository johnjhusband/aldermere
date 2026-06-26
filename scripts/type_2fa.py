"""Type 2FA code character-by-character with delays to mimic human input."""
import asyncio
import json
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

CRED_DIR = r"C:\Users\jhusband\.credentials"

def cache_get(service: str) -> dict:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         rf'& "{CRED_DIR}\Get-Credential.ps1" -Service {service}'],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)

async def main():
    code = Path(rf"{CRED_DIR}\namecheap_2fa_code.txt").read_text().strip()
    gmail = cache_get("gmail")
    print(f"Will type code: {code}, email: {gmail['email']}")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        target = None
        for pg in ctx.pages:
            if "namecheap.com" in pg.url:
                target = pg
                break
        if target is None:
            print("No namecheap tab")
            return

        async def first_visible(selector):
            locs = target.locator(selector)
            n = await locs.count()
            for i in range(n):
                if await locs.nth(i).is_visible():
                    return locs.nth(i)
            return None

        # Clear any existing values first
        code_input = await first_visible('input#codeInput')
        email_input = await first_visible('input[type="email"]:not([type=hidden])')
        if not code_input or not email_input:
            print(f"Missing fields: code={code_input}, email={email_input}")
            return

        await email_input.click()
        await email_input.press("Control+a")
        await email_input.press("Delete")
        await target.keyboard.type(gmail["email"], delay=80)
        print("Typed email")
        await target.wait_for_timeout(500)

        await code_input.click()
        await code_input.press("Control+a")
        await code_input.press("Delete")
        await target.keyboard.type(code, delay=120)
        print("Typed code")
        await target.wait_for_timeout(500)

        await target.screenshot(path=r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots\type-01-before-submit.png", full_page=True)

        # Click Submit
        submit = await first_visible('button:has-text("Submit")')
        if submit:
            await submit.click()
            print("Clicked Submit")
        else:
            await code_input.press("Enter")
            print("Pressed Enter")

        # Wait and observe
        await target.wait_for_timeout(8000)
        await target.screenshot(path=r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots\type-02-after-submit.png", full_page=True)
        print(f"URL after submit: {target.url}")
        print(f"Title: {await target.title()}")

asyncio.run(main())
