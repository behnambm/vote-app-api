from django.contrib import admin

from .models import Voters, Votes

admin.site.register(Votes)
admin.site.register(Voters)
