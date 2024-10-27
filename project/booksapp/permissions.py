from rest_framework import permissions
from booksapp.models import CustomUser
from hahaton import settings
import redis

session_storage = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            ssid = request.COOKIES["session_id"]
            username = session_storage.get(ssid)
            user = CustomUser.objects.get(username = username.decode("utf-8"))
        except:
            return False
        return bool(user)