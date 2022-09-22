from django.contrib import admin

from .models import Profile, Post, LikePost, Followerscount
# Register your models here.

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(Followerscount)

