"""Add 2 IPs via the Whitelisted IPs modal."""
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

        # Ensure modal is open. If not on /apiaccess/ at all, go there and click EDIT.
        if "apiaccess" not in target.url:
            await target.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
            await target.wait_for_timeout(4000)

        # If the Whitelisted IPs modal isn't already open, click EDIT
        modal_open = await target.locator('aside.gb-modal.gb-is-opened').count() > 0
        if not modal_open:
            edit_btn = await first_visible('button:has-text("EDIT")')
            if edit_btn:
                await edit_btn.click()
                await target.wait_for_timeout(2000)

        await target.screenshot(path=str(SHOTS / "wl2-00-modal.png"), full_page=True)

        for name, ip in IP_LABELS:
            print(f"--- Adding {name}={ip} ---")
            # Scope to the OPEN modal so we don't click the page button behind it
            modal = target.locator('aside.gb-modal.gb-is-opened').first
            add_btn = modal.locator('button:has-text("ADD IP"), button:has-text("Add IP"), button:has-text("Add Ip")').first
            try:
                await add_btn.wait_for(state="visible", timeout=5000)
            except Exception:
                print("  ADD IP button (in modal) not found")
                await target.screenshot(path=str(SHOTS / f"wl2-no-add-{name}.png"), full_page=True)
                continue
            if not add_btn:
                print("  ADD IP button not found")
                await target.screenshot(path=str(SHOTS / f"wl2-no-add-{name}.png"), full_page=True)
                continue
            await add_btn.click()
            print("  clicked ADD IP")
            await target.wait_for_timeout(2000)
            await target.screenshot(path=str(SHOTS / f"wl2-{name}-01-form.png"), full_page=True)

            # Dump inputs in the add-IP form
            inputs = await target.eval_on_selector_all("input, textarea", "els => els.filter(e => e.offsetParent !== null).map(e => ({tag: e.tagName, name: e.name, type: e.type, id: e.id, placeholder: e.placeholder, value: (e.value || '').slice(0,40)}))")
            print(f"  inputs: {inputs}")

            # Find name + IP fields and fill them
            # Common patterns: name first, then IP
            name_field = await first_visible('input[placeholder*="name" i]')
            ip_field = await first_visible('input[placeholder*="IP" i]')
            if not name_field or not ip_field:
                # Try by order
                all_text_inputs = target.locator('input[type="text"]:visible')
                n_inputs = await all_text_inputs.count()
                # Skip search box
                visible = []
                for i in range(n_inputs):
                    el = all_text_inputs.nth(i)
                    ph = await el.get_attribute("placeholder") or ""
                    if "search" not in ph.lower():
                        visible.append(el)
                if len(visible) >= 2:
                    name_field = visible[0]
                    ip_field = visible[1]

            if name_field:
                await name_field.click()
                await target.keyboard.type(name, delay=50)
                print(f"  typed name: {name}")
            if ip_field:
                await ip_field.click()
                await target.keyboard.type(ip, delay=50)
                print(f"  typed IP: {ip}")
            await target.screenshot(path=str(SHOTS / f"wl2-{name}-02-filled.png"), full_page=True)

            # Click Save / Add in the IP form (not the outer Add IP button)
            for sel in [
                'button:has-text("Save Changes")',
                'aside button:has-text("Save")',
                'aside button:has-text("Add")',
            ]:
                cand = await first_visible(sel)
                if cand:
                    await cand.click()
                    print(f"  saved via {sel}")
                    break
            await target.wait_for_timeout(2500)
            await target.screenshot(path=str(SHOTS / f"wl2-{name}-03-saved.png"), full_page=True)

        # Done
        done_btn = await first_visible('button:has-text("Done")')
        if done_btn:
            await done_btn.click()
            print("Clicked Done")
        await target.wait_for_timeout(2000)
        await target.screenshot(path=str(SHOTS / "wl2-99-final.png"), full_page=True)
        print(f"Final URL: {target.url}")

asyncio.run(main())
