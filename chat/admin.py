from django.contrib import admin
from .models import PrivateMessage,FriendRequest
# Register your models here.

admin.site.register(PrivateMessage)
admin.site.register(FriendRequest)