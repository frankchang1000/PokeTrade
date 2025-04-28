from django.db import models
from django.utils import timezone
from django.conf import settings
from cards.models import Card
from django.contrib.auth.models import User


class Listing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='listings')
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.card.name} - {self.price} coins by {self.seller.username}"
    
    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    transaction_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.buyer.username} bought {self.listing.card.name} for {self.listing.price} coins"

class TradeOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ]
    
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trade_offers_sent')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trade_offers_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Trade offer from {self.proposer.username} to {self.receiver.username} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class TradeOfferItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('offered', 'Offered'),
        ('requested', 'Requested')
    ]
    
    trade_offer = models.ForeignKey(TradeOffer, on_delete=models.CASCADE, related_name='items')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.get_item_type_display()} {self.card.name} in trade #{self.trade_offer.id}"
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"