from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import UserCard, Card
from .factories import PokemonCardFactory
from django.db.models import Q
import json

# Create your views here.

@login_required
def collection(request):
    """View to display the user's card collection"""
    search_term = request.GET.get('search')
    sort_by = request.GET.get('sort', '')  # 'name' for A-Z, '-name' for Z-A
    
    # Get filter types from request
    filter_types = request.GET.getlist('types', [])
    
    # Base query to get user's cards
    user_cards = UserCard.objects.filter(user=request.user).select_related('card')
    
    # Apply search filter if search term is provided
    if search_term:
        user_cards = user_cards.filter(card__name__icontains=search_term)
    
    # Apply type filters if provided
    if filter_types:
        user_cards = user_cards.filter(card__type__in=filter_types)
    
    # Apply sorting if requested
    if sort_by == 'name':
        user_cards = user_cards.order_by('card__name')
    elif sort_by == '-name':
        user_cards = user_cards.order_by('-card__name')
    
    # Get all available types for the filter checkboxes
    available_types = Card.objects.values_list('type', flat=True).distinct().exclude(type__isnull=True).exclude(type='')
    
    template_data = {
        'title': 'My Pokémon Collection',
        'user_cards': user_cards,
        'search_term': search_term,
        'sort_by': sort_by,
        'filter_types': filter_types,
        'available_types': available_types,
    }
    
    return render(request, 'cards/collection.html', {'template_data': template_data})

@login_required
def search_cards(request):
    """AJAX view to search cards without page refresh"""
    search_term = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '')
    
    # Get filter types from request
    filter_types = []
    types_param = request.GET.get('types', '[]')
    try:
        filter_types = json.loads(types_param)
    except json.JSONDecodeError:
        pass
    
    # Base query to get user's cards
    user_cards = UserCard.objects.filter(user=request.user).select_related('card')
    
    # Apply search filter if search term is provided
    if search_term:
        # Search by both name and type
        user_cards = user_cards.filter(
            Q(card__name__icontains=search_term) | 
            Q(card__type__icontains=search_term)
        )
    
    # Apply type filters if provided
    if filter_types:
        user_cards = user_cards.filter(card__type__in=filter_types)
    
    # Apply sorting if requested
    if sort_by == 'name':
        user_cards = user_cards.order_by('card__name')
    elif sort_by == '-name':
        user_cards = user_cards.order_by('-card__name')
    
    # Prepare card data for JSON response
    cards_data = []
    for user_card in user_cards:
        cards_data.append({
            'id': user_card.card.id,
            'name': user_card.card.name,
            'type': user_card.card.type,
            'rarity': user_card.card.rarity,
            'image_url': user_card.card.image_url,
            'hp': user_card.card.hp,
            'attack': user_card.card.attack,
            'defense': user_card.card.defense,
            'value': user_card.card.value,
        })
    
    return JsonResponse({'cards': cards_data})

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
