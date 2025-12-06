import requests
import time

from django.core.cache import cache
from config.settings import LICHESS_API_KEY


def get_lichess_puzzle_stats():
    cache_key = f'lichess_puzzle_stats_ratnesh_house'
    MAX_RETRIES = 3
    ONE_DAY = 86400
    ONE_MINUTE = 60

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                f'https://lichess.org/api/account',
                headers={'Authorization': f'Bearer {LICHESS_API_KEY}'},
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            puzzle_stats = {
                'rating': data.get('perfs', {}).get('puzzle', {}).get('rating', {}),
                'games': data.get('perfs', {}).get('puzzle', {}).get('games', {}),
            }

            cache.set(cache_key, puzzle_stats, ONE_DAY)

            return puzzle_stats
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"Attempt: {attempt} | Rate limit hit (429) while fetching Lichess puzzle data")
                # Lichess recommends retrying after a minute
                time.sleep(ONE_MINUTE)
            else:
                print(f"HTTP Error {response.status_code} while fetching Lichess puzzle data")
                # Don't retry on other errors
                break

    print(f"Failed to fetch Lichess puzzle data")
    return None