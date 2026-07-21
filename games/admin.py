from django.contrib import admin
from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "id", "attacker", "defender",
        "attacker_card", "defender_card",
        "status", "winner", "created_at",
    )
    list_filter = ("status",)