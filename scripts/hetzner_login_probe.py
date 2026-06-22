"""
Attempt to log into the Hetzner accounts portal with Playwright,
using credentials from the local DPAPI-encrypted credential cache.

Goal: get far enough to discover whether automation can reach the
API-token page, or whether CAPTCHA / 2FA blocks us. Saves screenshots
to scripts/screenshots/ for inspection.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

SCRIPT_DIR = Path(__file__).parent
SHOTS = SCRIPT_DIR / "screenshots"
SHOTS.mkdir(exist_ok=True)


def load_hetzner_creds():
    """Pull username/password from the DPAPI-encrypted cache."""
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            r'& "C:\Users\jhusband\.credentials\Get-Credential.ps1" -Service hetzner',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


async def main():
    creds = load_hetzner_creds()
    print(f"Loaded credentials for: {creds['username']}")

    import os
    engine = os.environ.get("PW_ENGINE", "chromium")

    async with async_playwright() as p:
        engine_obj = getattr(p, engine)
        browser = await engine_obj.launch(headless=False, slow_mo=200)
        print(f"Using engine: {engine}")
        ctx = await browser.new_context()
        page = await ctx.new_page()

        try:
            await page.goto("https://accounts.hetzner.com/login", wait_until="domcontentloaded")
            await page.screenshot(path=str(SHOTS / "01-login-loaded.png"), full_page=True)
            print(f"Step 1 — URL: {page.url}")
            print(f"Step 1 — Title: {await page.title()}")

            # Hetzner uses "Heray" — its own bot-detection layer. We may land
            # on a "Security Check" (proof-of-work) page or a "Request on Hold"
            # countdown page, and either may navigate at any moment. Wait until
            # a password input shows up.
            for attempt in range(60):  # up to ~180s total
                try:
                    title = (await page.title()) or ""
                    inputs = await page.eval_on_selector_all(
                        "input[type='password']", "els => els.length"
                    )
                except Exception as e:
                    # Page navigated mid-eval. Loop and try again.
                    print(f"Step 1.{attempt} — Eval interrupted ({type(e).__name__}), retrying in 2s")
                    await page.wait_for_timeout(2000)
                    continue
                title_l = title.lower()
                if inputs > 0:
                    print(f"Step 1.{attempt} — Password field detected, proceeding")
                    break
                state = "on Heray" if (
                    "request on hold" in title_l
                    or "security check" in title_l
                    or "/_ray/" in page.url
                ) else "unknown"
                print(f"Step 1.{attempt} — {state}, title={title!r}, URL={page.url}, waiting 3s")
                await page.wait_for_timeout(3000)
            await page.screenshot(path=str(SHOTS / "01b-after-heray.png"), full_page=True)
            print(f"Step 1b — URL after Heray wait: {page.url}")
            print(f"Step 1b — Title after Heray wait: {await page.title()}")

            # Look at the form. Hetzner uses standard input names but we'll discover them.
            inputs = await page.eval_on_selector_all(
                "input",
                """els => els.map(e => ({name: e.name, type: e.type, id: e.id, placeholder: e.placeholder}))""",
            )
            print(f"Step 1 — Inputs on page: {json.dumps(inputs, indent=2)}")

            # Try common selectors
            user_filled = False
            for sel in [
                'input[name="_username"]',
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                "#username",
                "#email",
            ]:
                try:
                    await page.fill(sel, creds["username"], timeout=2000)
                    print(f"Step 2 — Filled username via selector: {sel}")
                    user_filled = True
                    break
                except PWTimeoutError:
                    continue

            pwd_filled = False
            for sel in [
                'input[name="_password"]',
                'input[name="password"]',
                'input[type="password"]',
                "#password",
            ]:
                try:
                    await page.fill(sel, creds["password"], timeout=2000)
                    print(f"Step 2 — Filled password via selector: {sel}")
                    pwd_filled = True
                    break
                except PWTimeoutError:
                    continue

            await page.screenshot(path=str(SHOTS / "02-after-fill.png"), full_page=True)

            if not (user_filled and pwd_filled):
                print("Step 2 — Could not locate username/password fields.")
                return

            # Try common submit selectors
            for sel in [
                'button[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'input[type="submit"]',
            ]:
                try:
                    await page.click(sel, timeout=2000)
                    print(f"Step 3 — Clicked submit via selector: {sel}")
                    break
                except PWTimeoutError:
                    continue

            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except PWTimeoutError:
                print("Step 3 — Network did not idle within 15s, continuing.")

            await page.screenshot(path=str(SHOTS / "03-after-submit.png"), full_page=True)
            print(f"Step 3 — URL after submit: {page.url}")
            print(f"Step 3 — Title after submit: {await page.title()}")

            body_text = (await page.text_content("body")) or ""
            tokens = []
            for needle in ("captcha", "two-factor", "2fa", "verify", "code"):
                if needle.lower() in body_text.lower():
                    tokens.append(needle)
            print(f"Step 3 — Notable page tokens: {tokens}")

            # Hold for a bit so the user (and screenshots) can capture state
            print("Holding for 20s so any 2FA / CAPTCHA can be inspected or completed...")
            await page.wait_for_timeout(20000)
            await page.screenshot(path=str(SHOTS / "04-after-hold.png"), full_page=True)
            print(f"Step 4 — URL after hold: {page.url}")

        finally:
            await ctx.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
