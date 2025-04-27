import requests

def fetch_jamendo_tracks(genre='pop', limit=10):
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        'client_id': '684b7cdc',  # Register at https://devportal.jamendo.com/
        'format': 'json',
        'limit': limit,
        'tags': genre,
        'include': 'musicinfo',
        'audiodlformat': 'mp32',
        'order': 'popularity_total'
    }
    response = requests.get(url, params=params)
    print(response.text)
    return response.json()