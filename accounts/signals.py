from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from cards.factories import PokemonCardFactory
from cards.models import UserCard

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile with 500 coins
        profile = Profile.objects.create(user=instance)
        
        # Use the factory to create starter Pokémon cards
        factory = PokemonCardFactory()
        starter_cards = factory.generate_starter_cards(5)
        
        # Assign the cards to the user
        for card in starter_cards:
            UserCard.objects.create(user=instance, card=card)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save() 