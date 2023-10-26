from django.contrib import admin

# Register your models here.
from .models import Topic, Udata, Posts

admin.site.register(Topic)
admin.site.register(Udata)
admin.site.register(Posts)
