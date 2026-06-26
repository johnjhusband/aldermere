"""Click EDIT on Whitelisted IPs, add my IPs, save."""
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

# Ensure stdout handles unicode
sys.stdout.reconfigure(encoding='utf-8')

CRED_DIR = r"C:\Users\jhusband\.credentials"
SHOTS = Path(r"C:\Users\jhusband\Documents\claude\aldermere\scripts\screenshots")

def cache_get(service: str) -> dict:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         rf'& "{CRED_DIR}\Get-Credential.ps1" -Service {service}'],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)

async def main():
    api = cache_get("namecheap_api")
    ips = api.get("client_ips") or ["87.99.153.18", "72.224.149.206"]
    print(f"IPs to whitelist: {ips}")

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

        # Ensure we're on the API access page
        if "apiaccess" not in target.url:
            await target.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
            await target.wait_for_timeout(4000)
        print(f"At: {target.url}")

        # Click EDIT next to Whitelisted IPs
        edit_btn = await first_visible('button:has-text("EDIT")') or \
                   await first_visible('a:has-text("EDIT")') or \
                   await first_visible('button:has-text("Edit")')
        if not edit_btn:
            print("EDIT button not found")
            await target.screenshot(path=str(SHOTS / "wl-no-edit.png"), full_page=True)
            return
        await edit_btn.click()
        print("Clicked EDIT")
        await target.wait_for_timeout(3000)
        await target.screenshot(path=str(SHOTS / "wl-02-after-edit.png"), full_page=True)

        # Dump inputs/textareas/buttons after edit
        inputs = await target.eval_on_selector_all("input, textarea", "els => els.filter(e => e.offsetParent !== null).map(e => ({tag: e.tagName, name: e.name, type: e.type, id: e.id, placeholder: e.placeholder, value: (e.value || '').slice(0,60)}))")
        print(f"Inputs after EDIT: {inputs}")

        # Find IP input (usually a textbox where you enter IP)
        ip_input = None
        for sel in [
            'input[placeholder*="IP" i]',
            'input[name*="ip" i]',
            'input[type="text"][placeholder]',
        ]:
            cand = await first_visible(sel)
            if cand:
                ip_input = cand
                print(f"Found IP input via: {sel}")
                break

        if not ip_input:
            print("Could not find IP input field")
            return

        # Type each IP and click Add (or similar)
        for ip in ips:
            await ip_input.click()
            await ip_input.press("Control+a")
            await ip_input.press("Delete")
            await target.keyboard.type(ip, delay=60)
            print(f"Typed IP: {ip}")
            await target.wait_for_timeout(500)
            # Try clicking an "Add" / "+" button or pressing Enter
            for sel in [
                'button:has-text("Add")',
                'button:has-text("+")',
                'button[type="submit"]:has-text("Add")',
            ]:
                cand = await first_visible(sel)
                if cand:
                    await cand.click()
                    print(f"  clicked add via {sel}")
                    break
            else:
                await ip_input.press("Enter")
                print(f"  pressed Enter to add")
            await target.wait_for_timeout(1500)

        await target.screenshot(path=str(SHOTS / "wl-03-after-add.png"), full_page=True)

        # Click Save
        for sel in [
            'button:has-text("Save Changes")',
            'button:has-text("Save")',
            'button:has-text("Done")',
        ]:
            cand = await first_visible(sel)
            if cand:
                await cand.click()
                print(f"Clicked save via: {sel}")
                break

        await target.wait_for_timeout(3000)
        await target.screenshot(path=str(SHOTS / "wl-04-after-save.png"), full_page=True)
        print(f"Final URL: {target.url}")

asyncio.run(main())
