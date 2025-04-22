from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TradeOffer

@receiver(post_save, sender=TradeOffer)
def notify_on_trade_offer_change(sender, instance, created, **kwargs):
    if created:
        print(f"[Signal] New trade offer from {instance.proposer} to {instance.receiver} — Status: {instance.status}")
    else:
        print(f"[Signal] Trade offer updated — ID: {instance.id}, Status: {instance.status}")