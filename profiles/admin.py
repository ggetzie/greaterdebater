from django.contrib import admin
from tcd.profiles.models import Profile, Forgotten

class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,          {'fields': ['user', 'score', 'newwin', 'mailok']}),
        ('spamatha',    {'fields': ['probation', 'rate']}),
        ('feedinfo',    {'fields': ['feedcoms', 'feedtops', 'feeddebs']}),
        ('following',   {'fields': ['followtops', 'followcoms']})
        ]
    
    search_fields = ['user__username', 'user__email']
    list_filter = ('probation',)
        
admin.site.register(Profile, ProfileAdmin)

admin.site.register(Forgotten)
