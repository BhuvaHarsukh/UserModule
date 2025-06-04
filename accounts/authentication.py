from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import AccessToken, User
import time

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None

        token = token.replace('Bearer ', '')  # Remove Bearer prefix if used
        try:
            access_token = AccessToken.objects.get(token=token)
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        now = int(time.time() * 10000)
        created_time = int(access_token.created_at.timestamp() * 10000)
        if now > created_time + access_token.ttl:
            raise AuthenticationFailed("Token expired")

        return (access_token.user, None)
