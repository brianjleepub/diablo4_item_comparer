"""
Direct API approach for Wowhead data
Wowhead has XML/JSON endpoints for individual items
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


class WowheadAPIScraper:
    """Scraper using Wowhead's API endpoints"""

    BASE_URL = "https://www.wowhead.com/diablo-4"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    def __init__(self, rate_limit_seconds: float = 2.0):
        self.rate_limit = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page"""
        self._rate_limit_wait()
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_item_ids_from_listing(self, url: str) -> List[int]:
        """
        Extract item IDs from the listing page HTML
        Even if data isn't in JSON, we can get the IDs from links
        """
        print(f"Fetching item IDs from {url}...")
        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        item_ids = []

        # Look for links to items (format: /diablo-4/item/123 or data-id attributes)
        # Try different patterns
        patterns = [
            ('a', {'href': True}, 'href', r'/diablo-4/item/(\d+)'),
            ('a', {'href': True}, 'href', r'/diablo-4/items/(\d+)'),
            ('*', {'data-id': True}, 'data-id', None),
        ]

        import re

        for tag_name, attrs, attr_name, pattern in patterns:
            elements = soup.find_all(tag_name, attrs=attrs)
            for elem in elements:
                value = elem.get(attr_name, '')
                if pattern:
                    match = re.search(pattern, str(value))
                    if match:
                        item_ids.append(int(match.group(1)))
                else:
                    # Direct data-id
                    try:
                        item_ids.append(int(value))
                    except (ValueError, TypeError):
                        pass

        item_ids = list(set(item_ids))  # Remove duplicates
        print(f"Found {len(item_ids)} unique item IDs")
        return item_ids

    def get_item_xml(self, item_id: int) -> Optional[Dict]:
        """
        Fetch item data via XML endpoint
        Wowhead has: /diablo-4/item=123&xml
        """
        url = f"{self.BASE_URL}/item={item_id}&xml"
        xml_text = self._fetch_page(url)

        if not xml_text:
            return None

        try:
            root = ET.fromstring(xml_text)
            # Convert XML to dict
            item_data = {'id': item_id}
            for child in root:
                item_data[child.tag] = child.text or child.attrib
            return item_data
        except ET.ParseError as e:
            print(f"Error parsing XML for item {item_id}: {e}")
            return None

    def get_item_json(self, item_id: int) -> Optional[Dict]:
        """
        Try to get item data as JSON
        Try various endpoint patterns
        """
        endpoints = [
            f"{self.BASE_URL}/item={item_id}&json",
            f"{self.BASE_URL}/item/{item_id}?json",
            f"{self.BASE_URL}/tooltip/item/{item_id}",
            f"https://nether.wowhead.com/diablo4/tooltip/item/{item_id}",
        ]

        for url in endpoints:
            text = self._fetch_page(url)
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue

        return None

    def scrape_items_via_api(self, limit: int = 100) -> List[Dict]:
        """
        Scrape items by:
        1. Getting item IDs from listing page
        2. Fetching each item via API
        """
        # Get item IDs
        item_ids = self.get_item_ids_from_listing(f"{self.BASE_URL}/items")

        if not item_ids:
            print("Could not extract item IDs from listing")
            return []

        # Limit IDs
        item_ids = item_ids[:limit]

        # Fetch each item
        items = []
        for i, item_id in enumerate(item_ids, 1):
            print(f"Fetching item {i}/{len(item_ids)} (ID: {item_id})...")

            # Try JSON first, fall back to XML
            item_data = self.get_item_json(item_id)
            if not item_data:
                item_data = self.get_item_xml(item_id)

            if item_data:
                items.append(item_data)

        return items

    def save_to_json(self, data: List[Dict], filepath: Path):
        """Save data to JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} items to {filepath}")


def main():
    """Test the API scraper"""
    scraper = WowheadAPIScraper(rate_limit_seconds=1.0)
    data_dir = Path(__file__).parent.parent / "data" / "raw"

    # Try to scrape a small sample first
    print("=== Testing API Scraper ===")
    items = scraper.scrape_items_via_api(limit=10)

    if items:
        scraper.save_to_json(items, data_dir / "items_api_test.json")
        print(f"\nSample item:")
        print(json.dumps(items[0], indent=2))
    else:
        print("Could not scrape items via API")


if __name__ == "__main__":
    main()
