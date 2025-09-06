import requests


class TavilySearch:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.url = "https://api.tavily.com/search"


    def run(self, query: str, max_results: int = 5):
        payload = {"api_key": self.api_key, "query": query, "search_depth": "advanced", "max_results": max_results}
        r = requests.post(self.url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()