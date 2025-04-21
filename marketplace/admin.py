from django.contrib import admin
from .models import Listing, Transaction, TradeOffer, TradeOfferItem

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('card', 'seller', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('card__name', 'seller__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'transaction_date')
    list_filter = ('transaction_date',)
    search_fields = ('listing__card__name', 'buyer__username')

class TradeOfferItemInline(admin.TabularInline):
    model = TradeOfferItem
    extra = 0
    readonly_fields = ('trade_offer', 'card', 'item_type')

@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'proposer', 'receiver', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('proposer__username', 'receiver__username')
    inlines = [TradeOfferItemInline]
    readonly_fields = ('created_at', 'updated_at')
