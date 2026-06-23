"""
Bootstrap Namecheap API access and set A records for aldermere.world.

Two phases:

Phase 1 — Browser automation (Playwright + Chromium):
    Drive the Namecheap web dashboard to:
      * enable API access
      * generate an API key
      * whitelist the VPS IP
    Save the resulting key to the local DPAPI-encrypted credential cache as
    service "namecheap_api".

    Inputs: Namecheap username + password from credential cache
    (service "namecheap"), plus an optional TOTP secret.

Phase 2 — Namecheap REST API:
    Using the freshly-stored API key, call the Namecheap XML API to set the
    two A records on aldermere.world:
        @     -> 87.99.153.18
        www   -> 87.99.153.18

If phase 1 hits a CAPTCHA or 2FA wall we cannot pass, the script saves a
labeled screenshot for inspection and exits non-zero.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

VPS_IP = "87.99.153.18"
DOMAIN_SLD = "aldermere"
DOMAIN_TLD = "world"

SCRIPT_DIR = Path(__file__).parent
SHOTS = SCRIPT_DIR / "screenshots"
SHOTS.mkdir(exist_ok=True)
CRED_DIR = r"C:\Users\jhusband\.credentials"


def cache_get(service: str) -> dict:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            rf'& "{CRED_DIR}\Get-Credential.ps1" -Service {service}',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def cache_set(service: str, payload: dict) -> None:
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            rf'& "{CRED_DIR}\Set-Credential.ps1" -Service {service} -Json \'{json.dumps(payload)}\'',
        ],
        check=True,
    )


async def login_and_enable_api(creds: dict) -> dict:
    """Drive Namecheap dashboard to enable API + capture key."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        ctx = await browser.new_context()
        page = await ctx.new_page()

        try:
            await page.goto("https://www.namecheap.com/myaccount/login/", wait_until="domcontentloaded")
            await page.screenshot(path=str(SHOTS / "nc-01-login.png"), full_page=True)

            # Fill credentials; selectors current as of Namecheap UI.
            user_sel = None
            for sel in [
                'input[name="LoginUserName"]',
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                "#LoginUserName",
                "#Username",
            ]:
                try:
                    await page.fill(sel, creds["username"], timeout=3000)
                    user_sel = sel
                    print(f"Filled username via {sel}")
                    break
                except PWTimeoutError:
                    continue
            if not user_sel:
                print("Could not locate username field on Namecheap login.")
                await page.screenshot(path=str(SHOTS / "nc-02-no-user-field.png"), full_page=True)
                return {"success": False, "reason": "no username field"}

            pwd_sel = None
            for sel in [
                'input[name="LoginPassword"]',
                'input[name="password"]',
                'input[type="password"]',
                "#LoginPassword",
                "#Password",
            ]:
                try:
                    await page.fill(sel, creds["password"], timeout=3000)
                    pwd_sel = sel
                    print(f"Filled password via {sel}")
                    break
                except PWTimeoutError:
                    continue
            if not pwd_sel:
                await page.screenshot(path=str(SHOTS / "nc-02-no-pwd-field.png"), full_page=True)
                return {"success": False, "reason": "no password field"}

            await page.screenshot(path=str(SHOTS / "nc-02-filled.png"), full_page=True)

            for sel in [
                'button[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Login")',
                'input[type="submit"]',
            ]:
                try:
                    await page.click(sel, timeout=3000)
                    print(f"Submitted via {sel}")
                    break
                except PWTimeoutError:
                    continue

            await page.wait_for_load_state("networkidle", timeout=20000)
            await page.screenshot(path=str(SHOTS / "nc-03-after-login.png"), full_page=True)

            body = (await page.text_content("body")) or ""
            wall_tokens = [t for t in ("captcha", "verify", "two-factor", "2fa", "blocked") if t.lower() in body.lower()]
            print(f"Post-login URL: {page.url}, title: {await page.title()}, wall markers: {wall_tokens}")

            # If we hit 2FA prompt
            if any(t in wall_tokens for t in ("two-factor", "2fa", "verify")):
                # If we have a TOTP secret, generate the code and submit
                if creds.get("totp_secret"):
                    try:
                        import pyotp  # type: ignore
                        code = pyotp.TOTP(creds["totp_secret"]).now()
                        print(f"Generated TOTP code: {code}")
                        # Find TOTP input
                        for sel in ['input[name="code"]', 'input[type="text"]', 'input[autocomplete="one-time-code"]']:
                            try:
                                await page.fill(sel, code, timeout=3000)
                                break
                            except PWTimeoutError:
                                continue
                        for sel in ['button[type="submit"]', 'button:has-text("Verify")', 'button:has-text("Continue")']:
                            try:
                                await page.click(sel, timeout=3000)
                                break
                            except PWTimeoutError:
                                continue
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        await page.screenshot(path=str(SHOTS / "nc-04-after-totp.png"), full_page=True)
                    except ImportError:
                        return {"success": False, "reason": "TOTP required but pyotp not installed"}
                else:
                    print("2FA prompted but no TOTP secret in credentials.")
                    return {"success": False, "reason": "2FA required, no TOTP secret provided"}

            # Navigate to API access page
            await page.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(SHOTS / "nc-05-api-page.png"), full_page=True)
            print(f"API page URL: {page.url}, title: {await page.title()}")

            # The exact selectors here will be discovered on the page
            # (UI changes frequently). Print the rendered HTML for diagnosis.
            html_path = SHOTS / "nc-05-api-page.html"
            html_path.write_text(await page.content(), encoding="utf-8")
            print(f"API page HTML saved to {html_path}")

            # Stop here for now — we need to see the actual API page to know
            # how to drive it (enable toggle, key reveal, whitelist input).
            # This is the first interactive checkpoint.
            return {"success": False, "reason": "checkpoint: API page reached, need selector discovery"}

        finally:
            await ctx.close()
            await browser.close()


def namecheap_set_hosts(api_user: str, api_key: str, client_ip: str) -> dict:
    """Call namecheap.domains.dns.setHosts to set the two A records."""
    params = {
        "ApiUser": api_user,
        "ApiKey": api_key,
        "UserName": api_user,
        "ClientIp": client_ip,
        "Command": "namecheap.domains.dns.setHosts",
        "SLD": DOMAIN_SLD,
        "TLD": DOMAIN_TLD,
        "HostName1": "@",
        "RecordType1": "A",
        "Address1": VPS_IP,
        "TTL1": 1800,
        "HostName2": "www",
        "RecordType2": "A",
        "Address2": VPS_IP,
        "TTL2": 1800,
    }
    url = "https://api.namecheap.com/xml.response?" + urlencode(params)
    with urlopen(url) as resp:
        body = resp.read().decode("utf-8")
    return {"raw": body, "ok": ("Status=\"OK\"" in body or "IsSuccess>true" in body)}


async def main() -> int:
    try:
        nc_login = cache_get("namecheap")
    except subprocess.CalledProcessError:
        print("ERROR: No 'namecheap' credential in cache. Store username/password first.")
        return 2

    # Try to use an existing namecheap_api key if present
    try:
        nc_api = cache_get("namecheap_api")
        print(f"Found existing namecheap_api credentials for {nc_api.get('api_user')}.")
    except subprocess.CalledProcessError:
        nc_api = None

    if nc_api is None:
        print("Driving Namecheap dashboard to enable API access...")
        result = await login_and_enable_api(nc_login)
        if not result.get("success"):
            print(f"FAILED to enable Namecheap API automatically: {result.get('reason')}")
            print("Screenshots in scripts/screenshots/ for review.")
            return 3

    # Phase 2: set the DNS records
    print("Setting A records via Namecheap API...")
    api_creds = cache_get("namecheap_api")
    resp = namecheap_set_hosts(
        api_user=api_creds["api_user"],
        api_key=api_creds["api_key"],
        client_ip=api_creds.get("client_ip", VPS_IP),
    )
    if resp["ok"]:
        print("DNS records set successfully.")
        return 0
    print("DNS API call failed. Response:")
    print(resp["raw"])
    return 4


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
