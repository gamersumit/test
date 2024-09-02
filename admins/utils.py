from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import requests
import json
import base64
from django.http import JsonResponse
from django.conf import settings

def create_admin_token(admin):
    refresh = RefreshToken.for_user(admin)
    access=AccessToken.for_user(admin)
    return {
        'refresh_token': f"Bearer {str(refresh)}",
        'access_token': f"Bearer {str(access)}",
    }

def decode_access_token(access_token):
    return AccessToken(access_token)

def exchange_google_token(auth_code):
    token_url = "https://accounts.google.com/o/oauth2/token"
    payload = {
        "code": auth_code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(token_url, headers=headers, data=json.dumps(payload))
    print(response.json())
    return response

def fetch_google_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    person_fields = "names,emailAddresses,photos"
    google_profile_response = requests.get(f"https://people.googleapis.com/v1/people/me?personFields={person_fields}", headers=headers)
    if google_profile_response.status_code != 200:
        return JsonResponse({"message": google_profile_response.json()}, status=google_profile_response.status_code)
    data = google_profile_response.json()
    profile_object = {
        "name": data["names"][0]["displayName"],
        "email": data["emailAddresses"][0]["value"],
        "photo_url": data["photos"][0]["url"],
        "role": "Support"
    }
    return profile_object

def create_jwt_tokens(user_response, google_access_token, google_refresh_token):
    access_token = AccessToken.for_user(user_response)
    access_token['access_token'] = str(google_access_token)
    access_token['role'] = "Admin"
    refresh_token = RefreshToken.for_user(user_response)
    refresh_token['refresh_token'] = str(google_refresh_token)
    refresh_token['role'] = "Admin"
    jwt_access_token = str(access_token)
    jwt_refresh_token = str(refresh_token)
    return jwt_access_token, jwt_refresh_token

def parse_google_id_token(token: str) -> dict:
        parts = token.split(".")
        if len(parts) != 3:
            raise Exception("Incorrect id token format")
        payload = parts[1]
        padded = payload + '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(padded)
        return json.loads(decoded)