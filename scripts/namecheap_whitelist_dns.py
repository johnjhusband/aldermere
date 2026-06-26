"""
Drive Namecheap dashboard to add IPs to the API access whitelist,
then call the Namecheap XML API to set A records on aldermere.world.

API access is assumed already enabled and an API key already stored
(service "namecheap_api" with fields api_user, api_key, client_ips).
"""

import asyncio
import json
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
        ["powershell", "-NoProfile", "-Command",
         rf'& "{CRED_DIR}\Get-Credential.ps1" -Service {service}'],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


async def fetch_namecheap_code_from_gmail(ctx) -> str | None:
    """Open Gmail (already signed in via attached Chrome) and read the latest Namecheap 2FA code."""
    gpage = await ctx.new_page()
    try:
        # Navigate to inbox sorted by date desc and search for Namecheap email
        await gpage.goto("https://mail.google.com/mail/u/0/#search/from%3Anamecheap+newer_than%3A1d", wait_until="domcontentloaded")
        await gpage.wait_for_timeout(5000)
        await gpage.screenshot(path=str(SHOTS / "nc-w-g05-gmail-inbox.png"), full_page=True)

        # Click the first email row
        try:
            await gpage.locator('tr.zA, div.zA').first.click(timeout=10000)
            await gpage.wait_for_timeout(3000)
        except PWTimeoutError:
            print("  no Namecheap email found in inbox")
            await gpage.screenshot(path=str(SHOTS / "nc-w-g06-no-email.png"), full_page=True)
            return None
        await gpage.screenshot(path=str(SHOTS / "nc-w-g07-email-open.png"), full_page=True)

        # Pull the page text and find the 6-digit code
        body = await gpage.text_content("body") or ""
        import re
        # Look for "verification code: 123456" or just a standalone 6-digit number
        m = re.search(r"verification code[^0-9]{0,40}([0-9]{6})", body, re.IGNORECASE)
        if not m:
            m = re.search(r"\b([0-9]{6})\b", body)
        if not m:
            print("  no 6-digit code found in Gmail content")
            return None
        return m.group(1)
    finally:
        await gpage.close()


async def whitelist_ips(login: dict, ips: list[str]) -> bool:
    async with async_playwright() as p:
        # Attach to John's existing Chrome via CDP — uses his existing
        # session cookies, including Gmail.
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        if browser.contexts:
            ctx = browser.contexts[0]
        else:
            ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            print("Step 1 — open login page")
            await page.goto("https://www.namecheap.com/myaccount/login/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(SHOTS / "nc-w-01-login.png"), full_page=True)

            async def first_visible(selector: str):
                locs = page.locator(selector)
                n = await locs.count()
                for i in range(n):
                    cand = locs.nth(i)
                    if await cand.is_visible():
                        return cand
                return None

            # If Namecheap session cookies are present, the login page may
            # redirect directly to /twofa/device/ — in which case skip login.
            already_at_2fa = "/twofa/" in page.url or "Device Verification" in (await page.text_content("body") or "")
            if already_at_2fa:
                print(f"  already at 2FA page (URL={page.url}) — skipping login")
            else:
                user_field = await first_visible('input[data-ncid="input-login-username"]') or \
                             await first_visible('input[name="LoginUserName"]')
                pwd_field = await first_visible('input[data-ncid="input-login-password"]') or \
                            await first_visible('input[name="LoginPassword"]')
                if user_field is None or pwd_field is None:
                    print(f"  could not find visible login fields (user={user_field}, pwd={pwd_field})")
                    await page.screenshot(path=str(SHOTS / "nc-w-02-no-fields.png"), full_page=True)
                    return False
                await user_field.fill(login["username"])
                await pwd_field.fill(login["password"])
                print("  filled visible login fields")
                await page.screenshot(path=str(SHOTS / "nc-w-02-filled.png"), full_page=True)
                await pwd_field.press("Enter")
                print("  pressed Enter to submit")
                await page.wait_for_load_state("networkidle", timeout=20000)
            await page.screenshot(path=str(SHOTS / "nc-w-03-after-login.png"), full_page=True)
            print(f"  URL now: {page.url}, title: {await page.title()!r}")

            # If we hit a 2FA page, Namecheap just emailed a code. The wrapper
            # script (run_with_mcp.ps1) reads the latest code from Gmail via
            # an MCP tool and writes it to a sentinel file. Poll for it.
            if "/twofa/" in page.url or "two" in (await page.title()).lower():
                sentinel = Path(r"C:\Users\jhusband\.credentials\namecheap_2fa_code.txt")
                trigger = Path(r"C:\Users\jhusband\.credentials\namecheap_2fa_ready.txt")
                trigger.write_text("ready", encoding="ascii")
                print("Wrote ready trigger; waiting for code in sentinel file...")

                deadline = asyncio.get_event_loop().time() + 180
                while asyncio.get_event_loop().time() < deadline:
                    await asyncio.sleep(2)
                    if "/twofa/" not in page.url:
                        print(f"  2FA cleared in browser — URL now: {page.url}")
                        break
                    if sentinel.exists():
                        code = sentinel.read_text().strip()
                        sentinel.unlink(missing_ok=True)
                        trigger.unlink(missing_ok=True)
                        print(f"  got code: {code}")
                        # Fill the email field — required by the form
                        email_input = await first_visible('input[type="email"][placeholder*="you@yours" i]') or \
                                      await first_visible('input[name="email"]:not([type=hidden])') or \
                                      await first_visible('input[type="email"]')
                        if email_input is not None:
                            gmail_creds = cache_get("gmail")
                            await email_input.fill(gmail_creds["email"])
                            print(f"  filled email: {gmail_creds['email']}")
                        code_input = await first_visible('input#codeInput') or \
                                     await first_visible('input[placeholder*="verification code" i]')
                        if code_input is None:
                            print("  could not find 2FA code input")
                            return False
                        await code_input.fill(code)
                        # Click the visible Submit button (not the login form's "Sign In")
                        submit_btn = await first_visible('button:has-text("Submit")') or \
                                     await first_visible('button[type="submit"]')
                        if submit_btn is not None:
                            await submit_btn.click()
                            print("  clicked Submit on 2FA form")
                        else:
                            await code_input.press("Enter")
                            print("  pressed Enter on code field")
                        await page.wait_for_timeout(6000)
                        if "/twofa/" not in page.url:
                            print(f"  2FA cleared — URL now: {page.url}")
                            break
                else:
                    print("  TIMED OUT waiting for 2FA")
                    return False
                await page.screenshot(path=str(SHOTS / "nc-w-03e-after-2fa.png"), full_page=True)

            title_l = (await page.title()).lower()
            body = (await page.text_content("body") or "").lower()
            if "blocked" in body or "unusual" in body:
                print("HIT bot-detection wall after login.")
                return False

            print("Step 2 — navigate to API access page")
            await page.goto("https://ap.www.namecheap.com/settings/tools/apiaccess/", wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)
            await page.screenshot(path=str(SHOTS / "nc-w-04-api-page.png"), full_page=True)
            print(f"  URL: {page.url}, title: {await page.title()!r}")

            html = await page.content()
            (SHOTS / "nc-w-04-api-page.html").write_text(html, encoding="utf-8")

            # Discover existing whitelist input(s).
            inputs = await page.eval_on_selector_all(
                "input, textarea",
                """els => els.map(e => ({tag: e.tagName, name: e.name, type: e.type, id: e.id, placeholder: e.placeholder, value: (e.value || '').slice(0,40)}))""",
            )
            print(f"  inputs on API page (first 12):")
            for i, info in enumerate(inputs[:12]):
                print(f"    [{i}] {info}")

            # Look for any "Edit" or "Manage" button to open the whitelist editor.
            buttons = await page.eval_on_selector_all(
                "button, a",
                """els => els.slice(0, 30).map(e => (e.innerText || '').trim().slice(0, 60)).filter(t => t.length > 0)""",
            )
            print(f"  visible button/link text:")
            for b in buttons[:20]:
                print(f"    - {b!r}")

            # Try common selectors for the whitelist edit / save flow.
            opened = False
            for sel in [
                'button:has-text("Edit")',
                'a:has-text("Edit")',
                'button:has-text("Manage")',
                'button:has-text("Whitelisted IPs")',
                'a:has-text("Whitelisted IPs")',
            ]:
                try:
                    await page.click(sel, timeout=2000)
                    print(f"  opened editor via {sel}")
                    opened = True
                    await page.wait_for_timeout(1500)
                    break
                except PWTimeoutError:
                    continue
            await page.screenshot(path=str(SHOTS / "nc-w-05-editor.png"), full_page=True)

            # Try to find an IP input to fill.
            ip_input_sel = None
            for sel in [
                'input[name*="ip" i]',
                'input[placeholder*="IP" i]',
                'textarea[name*="ip" i]',
                'input[type="text"]:not([readonly])',
            ]:
                try:
                    matches = await page.eval_on_selector_all(sel, "els => els.length")
                    if matches > 0:
                        ip_input_sel = sel
                        print(f"  IP input candidate selector: {sel} ({matches} match)")
                        break
                except Exception:
                    continue

            if not ip_input_sel:
                print("Could not locate an IP input field. Inspect nc-w-05-editor.png and the HTML dump.")
                return False

            for ip in ips:
                try:
                    await page.fill(ip_input_sel, ip, timeout=2000)
                    print(f"  filled IP {ip}")
                    # Look for an Add button
                    for add_sel in ['button:has-text("Add")', 'button:has-text("+")', 'button[type="submit"]']:
                        try:
                            await page.click(add_sel, timeout=1500)
                            print(f"    clicked add via {add_sel}")
                            await page.wait_for_timeout(1000)
                            break
                        except PWTimeoutError:
                            continue
                except PWTimeoutError:
                    print(f"  failed to fill {ip} via {ip_input_sel}")

            await page.screenshot(path=str(SHOTS / "nc-w-06-after-fill.png"), full_page=True)

            # Save
            for sel in ['button:has-text("Save")', 'button:has-text("Submit")', 'button[type="submit"]']:
                try:
                    await page.click(sel, timeout=2000)
                    print(f"  saved via {sel}")
                    break
                except PWTimeoutError:
                    continue

            await page.wait_for_timeout(2500)
            await page.screenshot(path=str(SHOTS / "nc-w-07-saved.png"), full_page=True)
            return True
        finally:
            # Close only the tab we opened; leave John's Chrome and other tabs alone.
            try:
                await page.close()
            except Exception:
                pass


def namecheap_set_hosts(api_user: str, api_key: str, client_ip: str) -> dict:
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
    return {"raw": body, "ok": ('Status="OK"' in body) or ("IsSuccess>true" in body)}


async def main() -> int:
    login = cache_get("namecheap")
    api = cache_get("namecheap_api")
    ips = api.get("client_ips") or [VPS_IP]

    print(f"Will whitelist these IPs at Namecheap: {ips}")
    ok = await whitelist_ips(login, ips)
    if not ok:
        print("Whitelist step did not complete successfully.")
        # Try the DNS call anyway — the IPs may already be whitelisted from a prior run.
        print("Attempting DNS set anyway to see if whitelist is already in place...")

    print("Calling namecheap.domains.dns.setHosts...")
    resp = namecheap_set_hosts(
        api_user=api["api_user"],
        api_key=api["api_key"],
        client_ip="72.224.149.206",  # this PC is the calling IP
    )
    if resp["ok"]:
        print("DNS A records set successfully on aldermere.world.")
        return 0
    print("DNS API call failed. Response:")
    print(resp["raw"])
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
