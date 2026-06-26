"""Now that we're logged in, navigate to API Access and whitelist IPs."""
import asyncio
import json
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

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
    ips = api.get("client_ips") or ["87.99.153.18"]
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

        print(f"Current URL: {target.url}")
        print("Going to API Access page...")
        await target.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
        await target.wait_for_timeout(5000)
        await target.screenshot(path=str(SHOTS / "wl-01-api-page.png"), full_page=True)
        print(f"URL: {target.url}, title: {await target.title()}")
        (SHOTS / "wl-01-api-page.html").write_text(await target.content(), encoding="utf-8")

        # Dump visible buttons / inputs for selector discovery
        btns = await target.eval_on_selector_all("button, a", "els => els.filter(e => e.offsetParent !== null).map(e => ({tag: e.tagName, text: (e.innerText || '').trim().slice(0, 60), href: e.href || ''})).filter(o => o.text && o.text.length < 60).slice(0, 40)")
        print("Visible buttons/links (first 40):")
        for b in btns:
            print(f"  {b}")

        inputs = await target.eval_on_selector_all("input, textarea", "els => els.filter(e => e.offsetParent !== null).map(e => ({tag: e.tagName, name: e.name, type: e.type, id: e.id, placeholder: e.placeholder, value: (e.value || '').slice(0,40)}))")
        print(f"Visible inputs: {inputs}")

asyncio.run(main())
