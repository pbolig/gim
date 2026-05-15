import requests
import base64
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SpotifyToken

def get_redirect_uri(host):
    if 'localhost' in host or '127.0.0.1' in host:
        return f"http://{host}/spotify/callback/"
    return f"https://{host}/spotify/callback/"

def get_auth_url(host):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = get_redirect_uri(host)
    scope = "user-modify-playback-state user-read-playback-state"
    url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return url

def get_token(code, host, user):
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    redirect_uri = get_redirect_uri(host)
    
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        },
        headers={"Authorization": f"Basic {auth_header}"}
    )
    
    data = response.json()
    if 'access_token' in data:
        expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
        SpotifyToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': data['access_token'],
                'refresh_token': data.get('refresh_token'),
                'expires_at': expires_at
            }
        )
        return True
    return False

def refresh_spotify_token(user_token):
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": user_token.refresh_token
        },
        headers={"Authorization": f"Basic {auth_header}"}
    )
    
    data = response.json()
    if 'access_token' in data:
        user_token.access_token = data['access_token']
        user_token.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
        if 'refresh_token' in data:
            user_token.refresh_token = data['refresh_token']
        user_token.save()
        return True
    return False

def spotify_control(action, user):
    if not user.is_authenticated:
        return False
        
    try:
        user_token = SpotifyToken.objects.get(user=user)
        if user_token.expires_at <= timezone.now():
            if not refresh_spotify_token(user_token):
                return False
        
        url = f"https://api.spotify.com/v1/me/player/{action}"
        response = requests.put(
            url,
            headers={"Authorization": f"Bearer {user_token.access_token}"}
        )
        return response.status_code in [204, 202]
    except SpotifyToken.DoesNotExist:
        return False
