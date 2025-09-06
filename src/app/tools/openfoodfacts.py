import requests


BASE = "https://world.openfoodfacts.org"


class OpenFoodFacts:
    def search(self, query: str, page_size: int = 5):
        url = f"{BASE}/cgi/search.pl"
        params = {"search_terms": query, "search_simple": 1, "action": "process", "json": 1, "page_size": page_size}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()


    def get_barcode(self, barcode: str):
        url = f"{BASE}/api/v2/product/{barcode}.json"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()