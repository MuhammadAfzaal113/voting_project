from django.contrib import admin
from .models import CustomUser, Task, Contestant, ContestantTask, Vote, OTP



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'last_vote_reset']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'thumbnail']
  

@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    list_display = ['name', 'eliminated', 'voting_show_hide']

    def voting_show_hide(self, obj):
        return obj.show_hide

    voting_show_hide.short_description = "Voting Show/Hide"

    fieldsets = (
            (None, {
                'fields': ('name', 'photo', 'eliminated', 'show_hide'),
            }),
            ('Voting Settings', {
                'fields': ('show_hide',),
                'classes': ('collapse',),
                'description': "Voting Show/Hide",
            }),
        )


@admin.register(ContestantTask)
class ContestantTaskAdmin(admin.ModelAdmin):
    list_display = ['contestant', 'task', 'fan_votes', 'winning_votes', 'losing_votes']
  

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'contestant_task', 'voted_at']
   

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'created_at')