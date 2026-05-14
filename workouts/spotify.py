import requests
import base64
from django.conf import settings
from django.core.cache import cache

def get_auth_url(host=None):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = "http://127.0.0.1:8001/spotify/callback/"
    scope = "user-modify-playback-state user-read-playback-state"
    
    url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return url

def get_token(code, host=None):
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    redirect_uri = "http://127.0.0.1:8001/spotify/callback/"
    
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        },
        headers={
            "Authorization": f"Basic {auth_header}"
        }
    )
    
    data = response.json()
    if 'access_token' in data:
        cache.set('spotify_token', data['access_token'], data['expires_in'] - 60)
        cache.set('spotify_refresh_token', data.get('refresh_token'))
        return True
    return False

def spotify_control(action):
    token = cache.get('spotify_token')
    if not token:
        # Aquí iría lógica de refresh token, pero por ahora pedimos login
        return False
        
    url = f"https://api.spotify.com/v1/me/player/{action}"
    response = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code in [204, 202]
