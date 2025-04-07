from django.contrib import admin
from .models import Card, UserCard

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'pokemon_id', 'type', 'rarity', 'hp', 'attack', 'defense', 'value')
    search_fields = ('name', 'pokemon_id')
    list_filter = ('type', 'rarity')

@admin.register(UserCard)
class UserCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'obtained_at')
    search_fields = ('user__username', 'card__name')
    list_filter = ('obtained_at',)
