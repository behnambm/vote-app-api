from django.contrib import admin

from .models import Votes, Voters

admin.site.register(Votes)
admin.site.register(Voters)
