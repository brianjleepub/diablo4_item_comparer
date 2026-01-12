"""
Debug scraper to examine Wowhead page structure
"""

import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def analyze_page(url):
    """Analyze page structure and print findings"""
    print(f"\nAnalyzing: {url}\n" + "="*80)

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, 'lxml')

    # Find all script tags
    scripts = soup.find_all('script')
    print(f"Found {len(scripts)} script tags\n")

    # Analyze each script
    for i, script in enumerate(scripts):
        if not script.string:
            continue

        content = script.string[:500]  # First 500 chars

        # Look for data structures
        has_var = 'var ' in content or 'const ' in content or 'let ' in content
        has_array = '[' in content and ']' in content
        has_object = '{' in content and '}' in content
        has_data_keyword = 'data' in content.lower() or 'items' in content.lower()

        if has_var and (has_array or has_object) and has_data_keyword:
            print(f"\n--- Script {i} (Potential Data) ---")
            print(content)
            print("...")

            # Try to extract variable names
            var_pattern = r'(?:var|const|let)\s+(\w+)\s*='
            vars_found = re.findall(var_pattern, content)
            if vars_found:
                print(f"Variables: {vars_found}")

    # Look for AJAX/fetch calls
    print("\n" + "="*80)
    print("Looking for AJAX/API endpoints...")

    ajax_patterns = [
        r'fetch\(["\']([^"\']+)["\']',
        r'\.get\(["\']([^"\']+)["\']',
        r'ajax\(["\']([^"\']+)["\']',
        r'url:\s*["\']([^"\']+)["\']',
    ]

    for pattern in ajax_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f"\nFound {len(matches)} matches for pattern: {pattern}")
            for match in matches[:5]:  # Show first 5
                print(f"  - {match}")

# Analyze all three pages
analyze_page("https://www.wowhead.com/diablo-4/items")
print("\n\n")
analyze_page("https://www.wowhead.com/diablo-4/affixes")
print("\n\n")
analyze_page("https://www.wowhead.com/diablo-4/aspects")
