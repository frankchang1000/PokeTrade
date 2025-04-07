from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserCard
from .factories import PokemonCardFactory

# Create your views here.

@login_required
def collection(request):
    """View to display the user's card collection"""
    user_cards = UserCard.objects.filter(user=request.user).select_related('card')
    
    template_data = {
        'title': 'My Pokémon Collection',
        'user_cards': user_cards,
    }
    
    return render(request, 'cards/collection.html', {'template_data': template_data})

@login_required
def generate_new_card(request):
    """Generate a new card using the PokemonCardFactory"""
    if request.method == 'POST':
        # Check if user has enough coins (100 per card)
        if request.user.profile.coins < 100:
            messages.error(request, "You don't have enough coins to generate a new card.")
            return redirect('collection')
        
        # Deduct coins
        request.user.profile.coins -= 100
        request.user.profile.save()
        
        # Generate a new card using the factory
        factory = PokemonCardFactory()
        pokemon_id = factory.get_random_pokemon_ids(1)[0]
        pokemon_data = factory.get_data(pokemon_id)
        
        if pokemon_data:
            card = factory.create_card(pokemon_data)
            if card:
                UserCard.objects.create(user=request.user, card=card)
                messages.success(request, f"You received a new {card.name} card!")
            else:
                # Refund coins if card creation failed
                request.user.profile.coins += 100
                request.user.profile.save()
                messages.error(request, "Failed to generate a card. Please try again.")
        else:
            # Refund coins if API call failed
            request.user.profile.coins += 100
            request.user.profile.save()
            messages.error(request, "Failed to fetch Pokémon data. Please try again.")
    
    return redirect('collection')
