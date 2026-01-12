"""
Selenium-based scraper for dynamically loaded Wowhead data
"""

import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeleniumWowheadScraper:
    """Browser automation scraper for Wowhead"""

    BASE_URL = "https://www.wowhead.com/diablo-4"

    def __init__(self, headless: bool = True):
        """
        Initialize Selenium scraper

        Args:
            headless: Run browser in headless mode
        """
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)

    def __del__(self):
        """Cleanup driver on deletion"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _wait_for_data(self, timeout: int = 15):
        """Wait for listview data to load"""
        time.sleep(5)  # Give JavaScript time to execute

    def _extract_listview_data(self):
        """Extract data from Wowhead's listview system"""
        # Try to access the global window object where Wowhead stores data
        scripts_to_try = [
            "return typeof listviewitems !== 'undefined' ? listviewitems : null;",
            "return typeof listviewaffixes !== 'undefined' ? listviewaffixes : null;",
            "return typeof listviewaspects !== 'undefined' ? listviewaspects : null;",
            "return typeof WH !== 'undefined' && WH.data ? WH.data : null;",
            "return window.listviewitems || window.listviewaffixes || window.listviewaspects || null;",
        ]

        for script in scripts_to_try:
            try:
                data = self.driver.execute_script(script)
                if data:
                    return data
            except Exception as e:
                continue

        return None

    def scrape_items(self, limit=None):
        """Scrape items from Wowhead"""
        url = f"{self.BASE_URL}/items"
        print(f"Loading {url} with Selenium...")

        self.driver.get(url)
        self._wait_for_data()

        # Check what global variables exist
        print("Checking for global variables...")
        globals_check = self.driver.execute_script("""
            var globals = [];
            for (var key in window) {
                if (key.toLowerCase().includes('item') ||
                    key.toLowerCase().includes('data') ||
                    key.toLowerCase().includes('listview')) {
                    globals.push(key);
                }
            }
            return globals;
        """)
        print(f"Found potentially relevant globals: {globals_check}")

        # Try to extract data
        data = self._extract_listview_data()

        if data:
            print(f"Found {len(data)} items")
            if limit:
                data = data[:limit]
            return data
        else:
            print("Could not extract item data")
            return []

    def scrape_affixes(self, limit=None):
        """Scrape affixes from Wowhead"""
        url = f"{self.BASE_URL}/affixes"
        print(f"Loading {url} with Selenium...")

        self.driver.get(url)
        self._wait_for_data()

        # Check globals
        globals_check = self.driver.execute_script("""
            var globals = [];
            for (var key in window) {
                if (key.toLowerCase().includes('affix') ||
                    key.toLowerCase().includes('data') ||
                    key.toLowerCase().includes('listview')) {
                    globals.push(key);
                }
            }
            return globals;
        """)
        print(f"Found potentially relevant globals: {globals_check}")

        data = self._extract_listview_data()

        if data:
            print(f"Found {len(data)} affixes")
            if limit:
                data = data[:limit]
            return data
        else:
            print("Could not extract affix data")
            return []

    def scrape_aspects(self, limit=None):
        """Scrape aspects from Wowhead"""
        url = f"{self.BASE_URL}/aspects"
        print(f"Loading {url} with Selenium...")

        self.driver.get(url)
        self._wait_for_data()

        # Check globals
        globals_check = self.driver.execute_script("""
            var globals = [];
            for (var key in window) {
                if (key.toLowerCase().includes('aspect') ||
                    key.toLowerCase().includes('data') ||
                    key.toLowerCase().includes('listview')) {
                    globals.push(key);
                }
            }
            return globals;
        """)
        print(f"Found potentially relevant globals: {globals_check}")

        data = self._extract_listview_data()

        if data:
            print(f"Found {len(data)} aspects")
            if limit:
                data = data[:limit]
            return data
        else:
            print("Could not extract aspect data")
            return []

    def save_to_json(self, data, filepath: Path):
        """Save data to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} items to {filepath}")


def main():
    """Main scraping workflow"""
    scraper = SeleniumWowheadScraper(headless=True)
    data_dir = Path(__file__).parent.parent / "data" / "raw"

    try:
        # Scrape items
        print("\n=== Scraping Items ===")
        items = scraper.scrape_items(limit=100)
        if items:
            scraper.save_to_json(items, data_dir / "items_sample.json")
            print(f"\nSample item structure:")
            print(json.dumps(items[0], indent=2))

        # Scrape affixes
        print("\n=== Scraping Affixes ===")
        affixes = scraper.scrape_affixes(limit=100)
        if affixes:
            scraper.save_to_json(affixes, data_dir / "affixes_sample.json")
            print(f"\nSample affix structure:")
            print(json.dumps(affixes[0], indent=2))

        # Scrape aspects
        print("\n=== Scraping Aspects ===")
        aspects = scraper.scrape_aspects()
        if aspects:
            scraper.save_to_json(aspects, data_dir / "aspects_sample.json")
            print(f"\nSample aspect structure:")
            print(json.dumps(aspects[0], indent=2))

        print("\n=== Scraping Complete ===")

    finally:
        del scraper


if __name__ == "__main__":
    main()
