"""Add IPs via the Add IP dialog (which requires Namecheap password)."""
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

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

IP_LABELS = [
    ("aldermere-pc", "72.224.149.206"),
    ("aldermere-vps", "87.99.153.18"),
]

async def main():
    namecheap = cache_get("namecheap")
    password = namecheap["password"]

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

        # Navigate to the whitelist page directly
        if "whitelisted-ips" not in target.url:
            await target.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/whitelisted-ips", wait_until="domcontentloaded")
            await target.wait_for_timeout(3000)
        print(f"At: {target.url}")

        for name, ip in IP_LABELS:
            print(f"\n=== Adding {name}={ip} ===")

            # If an Add IP dialog isn't open, click the ADD IP button
            dialog = await first_visible('h2:has-text("Add IP"), h1:has-text("Add IP"), header:has-text("Add IP")')
            if not dialog:
                add_btn = await first_visible('button:has-text("ADD IP")') or \
                          await first_visible('button:has-text("Add IP")') or \
                          await first_visible('button:has-text("Add Ip")')
                if not add_btn:
                    print("  ADD IP button not found")
                    await target.screenshot(path=str(SHOTS / f"wl3-no-add-{name}.png"), full_page=True)
                    continue
                await add_btn.click()
                print("  clicked ADD IP")
                await target.wait_for_timeout(2000)

            # Fields by placeholder
            name_field = await first_visible('input[placeholder*="000" i]')  # NOT IP placeholder
            # Actually IP Name input has no placeholder; let me try by adjacency to "IP Name" label
            # Better: get all text inputs in the dialog area, in order
            all_text = target.locator('input[type="text"]:visible')
            name_field = None
            ip_field = None
            n = await all_text.count()
            for i in range(n):
                el = all_text.nth(i)
                ph = (await el.get_attribute("placeholder") or "").lower()
                if "search" in ph:
                    continue
                if "000" in ph or "ip" in ph and "name" not in ph:
                    if ip_field is None:
                        ip_field = el
                elif name_field is None:
                    name_field = el

            if not name_field or not ip_field:
                # Fallback: assume the first two non-search inputs are name + IP
                others = []
                for i in range(n):
                    el = all_text.nth(i)
                    ph = (await el.get_attribute("placeholder") or "").lower()
                    if "search" not in ph:
                        others.append(el)
                if len(others) >= 2:
                    name_field = others[0]
                    ip_field = others[1]
            if not name_field or not ip_field:
                print("  could not find name/IP fields")
                await target.screenshot(path=str(SHOTS / f"wl3-no-fields-{name}.png"), full_page=True)
                continue

            # Fill name
            await name_field.click()
            await target.keyboard.type(name, delay=50)
            print(f"  typed name: {name}")

            # Fill IP
            await ip_field.click()
            await target.keyboard.type(ip, delay=50)
            print(f"  typed IP: {ip}")

            # Fill password
            pwd_field = await first_visible('input[type="password"]')
            if not pwd_field:
                print("  password field not found")
                continue
            await pwd_field.click()
            await target.keyboard.type(password, delay=50)
            print("  typed password")

            await target.screenshot(path=str(SHOTS / f"wl3-{name}-filled.png"), full_page=True)

            # Click Save Changes
            save_btn = await first_visible('button:has-text("Save Changes")')
            if not save_btn:
                save_btn = await first_visible('button:has-text("Save")')
            if not save_btn:
                print("  Save button not found")
                continue
            await save_btn.click()
            print("  clicked Save Changes")
            await target.wait_for_timeout(4000)
            await target.screenshot(path=str(SHOTS / f"wl3-{name}-saved.png"), full_page=True)

        # Click Done at the end
        done_btn = await first_visible('button:has-text("Done")')
        if done_btn:
            await done_btn.click()
            print("\nClicked Done")
        await target.wait_for_timeout(2000)
        await target.screenshot(path=str(SHOTS / "wl3-final.png"), full_page=True)

asyncio.run(main())
