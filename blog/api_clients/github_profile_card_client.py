import requests
import time

from django.core.cache import cache


def get_github_profile_card():
    url = "https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=TheYorouzoya&theme=nord_dark"
    cache_key = f'github_profile_card_ratnesh'
    MAX_RETRIES = 3
    ONE_DAY = 86400
    ONE_MINUTE = 60

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url) 
            response.raise_for_status()

            profile_card = response.text
            cache.set(cache_key, profile_card, ONE_DAY)

            return profile_card
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"Attempt: {attempt} | Rate limit hit while fetching github profile data")
                time.sleep(ONE_MINUTE)
            else:
                print(f"HTTP Error {response.status_code} while fethcing Github profile data")
                break
    
    print("Failed to fetch Github Profile data")
    return None