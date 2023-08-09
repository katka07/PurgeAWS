from django.contrib import admin
from .models import AWSUser, Resource

admin.site.register(AWSUser)
admin.site.register(Resource)
