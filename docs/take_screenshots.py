"""Take screenshots of AutoClaims pages using Playwright."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "screenshots")
BASE_URL = "http://localhost:3010"

from playwright.sync_api import sync_playwright

def take_screenshots():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chrome_path = os.path.join(
        os.environ["USERPROFILE"],
        r"AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=chrome_path,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )

        screenshots = [
            ("dashboard", "/"),
            ("claim_detail", "/claim/6"),
            ("new_claim", "/new"),
            ("reviews", "/reviews"),
        ]

        for name, path in screenshots:
            page = None
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                url = f"{BASE_URL}{path}"
                print(f"Opening {url}...")
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(3)

                # Wait for API data
                if name == "dashboard":
                    try:
                        page.wait_for_function(
                            '() => document.body.innerText.includes("claim") || document.querySelectorAll(".grid > div").length > 4',
                            timeout=10000
                        )
                    except Exception as e:
                        print(f"  Dashboard wait: {e}")
                    time.sleep(2)
                elif name == "claim_detail":
                    try:
                        page.wait_for_function(
                            '() => document.body.innerText.includes("Intake") || document.body.innerText.includes("Frank")',
                            timeout=10000
                        )
                    except Exception as e:
                        print(f"  Claim detail wait: {e}")
                    time.sleep(2)
                elif name == "reviews":
                    try:
                        page.wait_for_function(
                            '() => document.body.innerText.includes("Review") || document.querySelector("table") !== null',
                            timeout=10000
                        )
                    except:
                        pass
                    time.sleep(2)
                elif name == "new_claim":
                    time.sleep(1)

                filepath = os.path.join(OUTPUT_DIR, f"{name}.png")
                page.screenshot(path=filepath, full_page=True)
                print(f"  Saved: {filepath}")
            except Exception as e:
                print(f"  Error on {name}: {e}")
                import traceback
                traceback.print_exc()
            finally:
                if page:
                    page.close()

        browser.close()
        print("\nAll screenshots complete!")

if __name__ == "__main__":
    take_screenshots()
