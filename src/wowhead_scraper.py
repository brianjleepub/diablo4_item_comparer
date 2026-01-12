"""
Wowhead Diablo 4 Database Scraper
Extracts items, affixes, and aspects from embedded JSON data
"""

import requests
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import chompjs


class WowheadScraper:
    """Scraper for Wowhead Diablo 4 database"""

    BASE_URL = "https://www.wowhead.com/diablo-4"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    def __init__(self, rate_limit_seconds: float = 2.0):
        """
        Initialize scraper with rate limiting

        Args:
            rate_limit_seconds: Seconds to wait between requests (be respectful!)
        """
        self.rate_limit = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page with rate limiting and error handling

        Args:
            url: Full URL to fetch

        Returns:
            Page HTML or None on error
        """
        self._rate_limit_wait()

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_embedded_json(self, html: str, var_name: str = "data") -> Optional[List[Dict]]:
        """
        Extract JSON data embedded in JavaScript variables

        Args:
            html: Page HTML
            var_name: JavaScript variable name containing data

        Returns:
            Parsed JSON data or None
        """
        soup = BeautifulSoup(html, 'lxml')

        # Find all script tags
        for script in soup.find_all('script'):
            if not script.string:
                continue

            # Look for variable assignment patterns
            # Pattern: var data = [...]; or const data = [...];
            pattern = rf'(?:var|const|let)\s+{var_name}\s*=\s*(\[.*?\]);'
            match = re.search(pattern, script.string, re.DOTALL)

            if match:
                try:
                    # Use chompjs to safely parse JavaScript object literals
                    json_str = match.group(1)
                    data = chompjs.parse_js_object(json_str)
                    return data
                except Exception as e:
                    print(f"Error parsing JSON with chompjs: {e}")
                    # Fallback to json.loads for valid JSON
                    try:
                        data = json.loads(json_str)
                        return data
                    except json.JSONDecodeError:
                        continue

        return None

    def scrape_items(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape items from Wowhead database

        Args:
            limit: Maximum number of items to scrape (None for all)

        Returns:
            List of item dictionaries
        """
        url = f"{self.BASE_URL}/items"
        print(f"Fetching items from {url}...")

        html = self._fetch_page(url)
        if not html:
            return []

        # Try different variable names that might contain the data
        for var_name in ['data', 'listviewitems', 'items', 'g_items']:
            items = self._extract_embedded_json(html, var_name)
            if items:
                print(f"Found {len(items)} items in variable '{var_name}'")
                if limit:
                    items = items[:limit]
                return items

        print("Could not find embedded item data")
        return []

    def scrape_affixes(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape affixes from Wowhead database

        Args:
            limit: Maximum number of affixes to scrape (None for all)

        Returns:
            List of affix dictionaries
        """
        url = f"{self.BASE_URL}/affixes"
        print(f"Fetching affixes from {url}...")

        html = self._fetch_page(url)
        if not html:
            return []

        for var_name in ['data', 'listviewaffixes', 'affixes', 'g_affixes']:
            affixes = self._extract_embedded_json(html, var_name)
            if affixes:
                print(f"Found {len(affixes)} affixes in variable '{var_name}'")
                if limit:
                    affixes = affixes[:limit]
                return affixes

        print("Could not find embedded affix data")
        return []

    def scrape_aspects(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape aspects from Wowhead database

        Args:
            limit: Maximum number of aspects to scrape (None for all)

        Returns:
            List of aspect dictionaries
        """
        url = f"{self.BASE_URL}/aspects"
        print(f"Fetching aspects from {url}...")

        html = self._fetch_page(url)
        if not html:
            return []

        for var_name in ['data', 'listviewaspects', 'aspects', 'g_aspects']:
            aspects = self._extract_embedded_json(html, var_name)
            if aspects:
                print(f"Found {len(aspects)} aspects in variable '{var_name}'")
                if limit:
                    aspects = aspects[:limit]
                return aspects

        print("Could not find embedded aspect data")
        return []

    def save_to_json(self, data: List[Dict], filepath: Path):
        """Save scraped data to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} items to {filepath}")


def main():
    """Main scraping workflow"""
    scraper = WowheadScraper(rate_limit_seconds=2.0)
    data_dir = Path(__file__).parent.parent / "data" / "raw"

    # Scrape items (limit to 100 for POC)
    print("\n=== Scraping Items ===")
    items = scraper.scrape_items(limit=100)
    if items:
        scraper.save_to_json(items, data_dir / "items_sample.json")
        print(f"\nSample item structure:")
        print(json.dumps(items[0], indent=2))

    # Scrape affixes (limit to 100 for POC)
    print("\n=== Scraping Affixes ===")
    affixes = scraper.scrape_affixes(limit=100)
    if affixes:
        scraper.save_to_json(affixes, data_dir / "affixes_sample.json")
        print(f"\nSample affix structure:")
        print(json.dumps(affixes[0], indent=2))

    # Scrape aspects (all, since there are only ~466)
    print("\n=== Scraping Aspects ===")
    aspects = scraper.scrape_aspects()
    if aspects:
        scraper.save_to_json(aspects, data_dir / "aspects_sample.json")
        print(f"\nSample aspect structure:")
        print(json.dumps(aspects[0], indent=2))

    print("\n=== Scraping Complete ===")


if __name__ == "__main__":
    main()
