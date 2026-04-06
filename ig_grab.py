from pathlib import Path
from urllib.parse import urlparse
import re
import time
import requests
from playwright.sync_api import sync_playwright


PROFILE_URL = "https://www.instagram.com/coffeeoutsidedurham/"
OUTPUT_DIR = Path("media/instagram")
MAX_IMAGES = 56

# Use a persistent browser profile folder so your Instagram login can persist.
USER_DATA_DIR = Path(".playwright_profile")


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", name)


def pick_filename(url: str, index: int) -> str:
    path = urlparse(url).path
    raw_name = Path(path).name or f"image_{index:03d}.jpg"
    raw_name = raw_name.split("?")[0]
    if "." not in raw_name:
        raw_name += ".jpg"
    return f"{index:03d}"


def download_image(url: str, out_path: Path) -> bool:
    try:
        r = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.instagram.com/",
            },
            stream=True,
        )
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def collect_image_urls(page, max_images: int) -> list[str]:
    seen = set()
    stagnant_rounds = 0
    last_count = 0

    while len(seen) < max_images and stagnant_rounds < 8:
        # Gather image URLs currently visible on the profile page.
        urls = page.eval_on_selector_all(
            "img",
            """
            els => els
                .map(img => img.src)
                .filter(Boolean)
                .filter(src => src.startsWith("http"))
            """,
        )

        # Keep only likely post images, not tiny UI assets.
        for url in urls:
            if "cdninstagram" in url or "fbcdn.net" in url:
                seen.add(url)

        print(f"Found {len(seen)} candidate image URLs...")

        if len(seen) == last_count:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
            last_count = len(seen)

        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(1500)

    return list(seen)[:max_images]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 1000},
        )

        page = browser.new_page()
        page.goto(PROFILE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        print()
        print("If Instagram asks you to log in, do it in the opened browser window.")
        print("Then press Enter here in the terminal to continue scraping.")
        input()

        page.goto(PROFILE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        image_urls = collect_image_urls(page, MAX_IMAGES)

        print(f"\nDownloading {len(image_urls)} images...\n")
        success_count = 0

        for i, url in enumerate(image_urls, start=1):
            filename = pick_filename(url, i)
            out_path = OUTPUT_DIR / filename
            if download_image(url, out_path):
                success_count += 1
                print(f"Saved {out_path}")

        browser.close()

    print()
    print(f"Done. Downloaded {success_count} images to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
