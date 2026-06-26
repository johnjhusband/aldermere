"""Namecheap whitelist + DNS via fresh Chromium routed through VPS SOCKS proxy."""
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

VPS_IP = "87.99.153.18"
LOCAL_IP = "72.224.149.206"
SCRIPT_DIR = Path(__file__).parent
SHOTS = SCRIPT_DIR / "screenshots"
SHOTS.mkdir(exist_ok=True)
CRED_DIR = r"C:\Users\jhusband\.credentials"


def cache_get(service: str) -> dict:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         rf'& "{CRED_DIR}\Get-Credential.ps1" -Service {service}'],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def code_from_latest_email(after_iso: str) -> str | None:
    """Search for fresh Namecheap codes after a given timestamp; ask Claude
    (this process is single-shot — codes are passed in via sentinel file)."""
    sentinel = Path(rf"{CRED_DIR}\namecheap_2fa_code.txt")
    trigger = Path(rf"{CRED_DIR}\namecheap_2fa_ready.txt")
    trigger.write_text(after_iso, encoding="ascii")
    deadline = asyncio.get_event_loop().time() + 180
    while asyncio.get_event_loop().time() < deadline:
        if sentinel.exists():
            code = sentinel.read_text().strip()
            sentinel.unlink(missing_ok=True)
            trigger.unlink(missing_ok=True)
            return code
        # synchronous-ish sleep
        import time
        time.sleep(2)
    return None


async def run() -> int:
    login = cache_get("namecheap")
    api = cache_get("namecheap_api")
    ips = api.get("client_ips") or [VPS_IP]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=150,
            proxy={"server": "socks5://localhost:1080"},
        )
        ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            # Confirm exit IP first
            await page.goto("https://api.ipify.org?format=json", wait_until="domcontentloaded")
            body = await page.text_content("body") or ""
            print(f"Playwright exit IP via proxy: {body}")

            await page.goto("https://www.namecheap.com/myaccount/login/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(SHOTS / "vps-01-login.png"), full_page=True)

            async def first_visible(selector: str):
                locs = page.locator(selector)
                n = await locs.count()
                for i in range(n):
                    cand = locs.nth(i)
                    if await cand.is_visible():
                        return cand
                return None

            if "/twofa/" in page.url:
                print("Already at 2FA (cookies?) — skipping login.")
            else:
                user_field = await first_visible('input[data-ncid="input-login-username"]') or \
                             await first_visible('input[name="LoginUserName"]')
                pwd_field = await first_visible('input[data-ncid="input-login-password"]') or \
                            await first_visible('input[name="LoginPassword"]')
                if not user_field or not pwd_field:
                    print("Login fields not found")
                    await page.screenshot(path=str(SHOTS / "vps-02-no-fields.png"), full_page=True)
                    return 1
                await user_field.fill(login["username"])
                await pwd_field.fill(login["password"])
                await pwd_field.press("Enter")
                await page.wait_for_load_state("networkidle", timeout=20000)
                await page.screenshot(path=str(SHOTS / "vps-03-after-submit.png"), full_page=True)
                print(f"After login URL: {page.url}, title: {await page.title()}")

            if "/twofa/" in page.url:
                from datetime import datetime, timezone
                start_iso = datetime.now(timezone.utc).isoformat()
                print(f"At 2FA. Requesting fresh code via sentinel (start={start_iso}).")
                code = code_from_latest_email(start_iso)
                if not code:
                    print("No code received via sentinel")
                    return 2
                print(f"Got code: {code}")
                gmail = cache_get("gmail")
                email_input = await first_visible('input[type="email"][placeholder*="you@yours" i]') or \
                              await first_visible('input[name="email"]:not([type=hidden])') or \
                              await first_visible('input[type="email"]')
                if email_input:
                    await email_input.fill(gmail["email"])
                code_input = await first_visible('input#codeInput') or \
                             await first_visible('input[placeholder*="verification code" i]')
                if not code_input:
                    print("No code input field")
                    return 3
                await code_input.fill(code)
                submit_btn = await first_visible('button:has-text("Submit")') or \
                             await first_visible('button[type="submit"]')
                if submit_btn:
                    await submit_btn.click()
                else:
                    await code_input.press("Enter")
                await page.wait_for_timeout(6000)
                await page.screenshot(path=str(SHOTS / "vps-04-after-2fa.png"), full_page=True)
                print(f"After 2FA submit URL: {page.url}")
                if "/twofa/" in page.url:
                    print("2FA still failing.")
                    return 4

            print("Navigating to API access page")
            await page.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            await page.screenshot(path=str(SHOTS / "vps-05-api-page.png"), full_page=True)
            print(f"API page URL: {page.url}")
            (SHOTS / "vps-05-api-page.html").write_text(await page.content(), encoding="utf-8")

            # Look for whitelisted IP edit
            for btn_text in ["Edit", "Manage", "Whitelisted IPs"]:
                try:
                    await page.locator(f'button:has-text("{btn_text}"), a:has-text("{btn_text}")').first.click(timeout=2000)
                    print(f"Clicked {btn_text!r}")
                    await page.wait_for_timeout(2000)
                    break
                except PWTimeoutError:
                    continue

            await page.screenshot(path=str(SHOTS / "vps-06-editor.png"), full_page=True)

            # Try common selectors for IP input
            for ip in ips:
                filled = False
                for sel in ['input[name*="ip" i]', 'input[placeholder*="IP" i]', 'textarea[name*="ip" i]']:
                    try:
                        await page.fill(sel, ip, timeout=2000)
                        filled = True
                        print(f"  filled IP {ip} via {sel}")
                        for add_sel in ['button:has-text("Add")', 'button:has-text("+")']:
                            try:
                                await page.click(add_sel, timeout=1500)
                                print(f"  clicked add")
                                await page.wait_for_timeout(1000)
                                break
                            except PWTimeoutError:
                                continue
                        break
                    except PWTimeoutError:
                        continue
                if not filled:
                    print(f"  could not fill IP {ip}")

            for sel in ['button:has-text("Save")', 'button[type="submit"]']:
                try:
                    await page.click(sel, timeout=2000)
                    print(f"  saved via {sel}")
                    break
                except PWTimeoutError:
                    continue
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(SHOTS / "vps-07-saved.png"), full_page=True)
            return 0
        finally:
            await ctx.close()
            await browser.close()


def namecheap_set_hosts(api_user: str, api_key: str, client_ip: str) -> dict:
    params = {
        "ApiUser": api_user, "ApiKey": api_key, "UserName": api_user,
        "ClientIp": client_ip, "Command": "namecheap.domains.dns.setHosts",
        "SLD": "aldermere", "TLD": "world",
        "HostName1": "@", "RecordType1": "A", "Address1": VPS_IP, "TTL1": 1800,
        "HostName2": "www", "RecordType2": "A", "Address2": VPS_IP, "TTL2": 1800,
    }
    url = "https://api.namecheap.com/xml.response?" + urlencode(params)
    body = urlopen(url).read().decode("utf-8")
    return {"raw": body, "ok": ('Status="OK"' in body) or ("IsSuccess>true" in body)}


def main() -> int:
    rc = asyncio.run(run())
    if rc != 0:
        print(f"Whitelist step exit code {rc}; attempting DNS anyway.")
    api = cache_get("namecheap_api")
    resp = namecheap_set_hosts(api["api_user"], api["api_key"], LOCAL_IP)
    print(resp["raw"])
    return 0 if resp["ok"] else 5


if __name__ == "__main__":
    sys.exit(main())
