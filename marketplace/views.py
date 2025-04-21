from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import Listing, Transaction, TradeOffer, TradeOfferItem
from cards.models import Card, UserCard
from accounts.models import Profile

@login_required
def marketplace(request):
    """view for the marketplace page showing all active listings"""
    listings = Listing.objects.filter(is_active=True).select_related('card', 'seller')
    
    # get the user's balance for display
    user_profile = Profile.objects.get(user=request.user)
    
    # get user's cards that aren't already listed
    user_cards = UserCard.objects.filter(
        user=request.user
    ).exclude(
        card__listings__seller=request.user,
        card__listings__is_active=True
    ).select_related('card')
    
    template_data = {
        'title': 'Marketplace',
        'active_page': 'marketplace'
    }
    
    context = {
        'listings': listings,
        'user_cards': user_cards,
        'user_balance': user_profile.coins,
        'template_data': template_data,
        'page_type': 'marketplace'  # added to identify which page type we're on
    }
    
    return render(request, 'marketplace/marketplace.html', context)

@login_required
def create_listing(request, card_id):
    """create a new listing for a card"""
    if request.method == 'POST':
        try:
            price = int(request.POST.get('price', 0))
            if price <= 0:
                messages.error(request, "Price must be greater than 0")
                return redirect('marketplace')
                
            card = get_object_or_404(Card, pk=card_id)
            
            # check if user owns this card
            user_card = UserCard.objects.filter(user=request.user, card=card).first()
            if not user_card:
                messages.error(request, "You don't own this card")
                return redirect('marketplace')
                
            # check if card is already listed by this user
            existing_listing = Listing.objects.filter(
                seller=request.user,
                card=card,
                is_active=True
            ).first()
            
            if existing_listing:
                messages.error(request, "You already have this card listed")
                return redirect('marketplace')
                
            # create new listing
            Listing.objects.create(
                seller=request.user,
                card=card,
                price=price
            )
            
            messages.success(request, f"Your {card.name} has been listed for {price} coins")
            
        except ValueError:
            messages.error(request, "Invalid price")
            
    return redirect('marketplace')

@login_required
def remove_listing(request, listing_id):
    """remove a listing from the marketplace"""
    listing = get_object_or_404(Listing, pk=listing_id, seller=request.user)
    listing.is_active = False
    listing.save()
    
    messages.success(request, f"Your listing for {listing.card.name} has been removed")
    return redirect('marketplace')

@login_required
@transaction.atomic
def purchase_card(request, listing_id):
    """purchase a card from the marketplace"""
    listing = get_object_or_404(Listing, pk=listing_id, is_active=True)
    
    # prevent buying your own card
    if listing.seller == request.user:
        messages.error(request, "You cannot buy your own card")
        return redirect('marketplace')
        
    buyer_profile = get_object_or_404(Profile, user=request.user)
    
    # check if buyer has enough coins
    if buyer_profile.coins < listing.price:
        messages.error(request, "You don't have enough coins")
        return redirect('marketplace')
        
    seller_profile = get_object_or_404(Profile, user=listing.seller)
    
    # update balances
    buyer_profile.coins = F('coins') - listing.price
    seller_profile.coins = F('coins') + listing.price
    
    # update listing status
    listing.is_active = False
    
    # create transaction record
    transaction = Transaction.objects.create(
        listing=listing,
        buyer=request.user
    )
    
    # add card to buyer's collection
    UserCard.objects.create(
        user=request.user,
        card=listing.card
    )
    
    # save all changes
    buyer_profile.save()
    seller_profile.save()
    listing.save()
    
    # refresh from database to get actual values after f() expressions
    buyer_profile.refresh_from_db()
    seller_profile.refresh_from_db()
    
    messages.success(
        request, 
        f"You purchased {listing.card.name} for {listing.price} coins. "
        f"Your new balance is {buyer_profile.coins} coins."
    )
    
    return redirect('marketplace')

# trading views
@login_required
def trading(request):
    """view for the trading page showing all pending trades and cards available to trade"""
    # trades offered to you
    received_trades = TradeOffer.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('proposer')
    
    # trades you've offered to others
    sent_trades = TradeOffer.objects.filter(
        proposer=request.user,
        status='pending'
    ).select_related('receiver')
    
    # get all users who have cards (excluding yourself)
    users_with_cards = User.objects.filter(
        cards__isnull=False
    ).exclude(
        id=request.user.id
    ).distinct()
    
    # get your cards
    user_cards = UserCard.objects.filter(
        user=request.user
    ).select_related('card')
    
    template_data = {
        'title': 'Trading Cards',
        'active_page': 'marketplace'
    }
    
    context = {
        'received_trades': received_trades,
        'sent_trades': sent_trades,
        'users_with_cards': users_with_cards,
        'user_cards': user_cards,
        'template_data': template_data,
        'page_type': 'trading'  # added to identify which page type we're on
    }
    
    return render(request, 'marketplace/trading.html', context)

@login_required
def propose_trade(request):
    """form for proposing a trade with another user"""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        
        if not receiver_id:
            messages.error(request, "Please select a user to trade with")
            return redirect('trading')
            
        receiver = get_object_or_404(User, pk=receiver_id)
        
        # don't allow trading with yourself
        if receiver == request.user:
            messages.error(request, "You cannot trade with yourself")
            return redirect('trading')
            
        # get the receiver's cards
        receiver_cards = UserCard.objects.filter(
            user=receiver
        ).select_related('card')
        
        # your cards
        user_cards = UserCard.objects.filter(
            user=request.user
        ).select_related('card')
        
        template_data = {
            'title': 'Propose Trade',
            'active_page': 'marketplace'
        }
        
        context = {
            'receiver': receiver,
            'receiver_cards': receiver_cards,
            'user_cards': user_cards,
            'template_data': template_data
        }
        
        return render(request, 'marketplace/propose_trade.html', context)
        
    return redirect('trading')

@login_required
def add_card_to_trade(request):
    """ajax endpoint to add a card to the trade session"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        card_id = request.POST.get('card_id')
        card_type = request.POST.get('card_type')  # 'offered' or 'requested'
        
        if not card_id or not card_type:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'})
            
        # initialize session trade if not exists
        if 'trade_cards' not in request.session:
            request.session['trade_cards'] = {'offered': [], 'requested': []}
            
        # add card to session if not already there
        card = get_object_or_404(Card, pk=card_id)
        
        if card_id not in request.session['trade_cards'][card_type]:
            request.session['trade_cards'][card_type].append(card_id)
            request.session.modified = True
            return JsonResponse({
                'status': 'success', 
                'message': f'{card.name} added to trade',
                'card_id': card_id,
                'card_name': card.name
            })
        
        return JsonResponse({'status': 'error', 'message': 'Card already in trade'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def remove_card_from_trade(request):
    """ajax endpoint to remove a card from the trade session"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        card_id = request.POST.get('card_id')
        card_type = request.POST.get('card_type')  # 'offered' or 'requested'
        
        if not card_id or not card_type:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'})
            
        # remove card from session if exists
        if 'trade_cards' in request.session and card_id in request.session['trade_cards'][card_type]:
            request.session['trade_cards'][card_type].remove(card_id)
            request.session.modified = True
            return JsonResponse({'status': 'success', 'message': 'Card removed from trade'})
        
        return JsonResponse({'status': 'error', 'message': 'Card not in trade'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
@transaction.atomic
def submit_trade_offer(request, user_id):
    """submit a trade offer to another user"""
    if request.method == 'POST':
        receiver = get_object_or_404(User, pk=user_id)
        
        if receiver == request.user:
            messages.error(request, "You cannot trade with yourself")
            return redirect('trading')
            
        # check if trade cards are in session
        if 'trade_cards' not in request.session:
            messages.error(request, "No cards selected for trade")
            return redirect('trading')
            
        offered_card_ids = request.session['trade_cards'].get('offered', [])
        requested_card_ids = request.session['trade_cards'].get('requested', [])
        
        # ensure there's at least one card on each side
        if not offered_card_ids or not requested_card_ids:
            messages.error(request, "You must offer and request at least one card each")
            return redirect('trading')
            
        # verify that proposer owns the offered cards
        for card_id in offered_card_ids:
            if not UserCard.objects.filter(user=request.user, card_id=card_id).exists():
                messages.error(request, "You don't own one of the cards you're offering")
                return redirect('trading')
                
        # verify that receiver owns the requested cards
        for card_id in requested_card_ids:
            if not UserCard.objects.filter(user=receiver, card_id=card_id).exists():
                messages.error(request, "The other user doesn't own one of the cards you're requesting")
                return redirect('trading')
                
        # create trade offer
        trade_offer = TradeOffer.objects.create(
            proposer=request.user,
            receiver=receiver,
            status='pending'
        )
        
        # add offered cards
        for card_id in offered_card_ids:
            TradeOfferItem.objects.create(
                trade_offer=trade_offer,
                card_id=card_id,
                item_type='offered'
            )
            
        # add requested cards
        for card_id in requested_card_ids:
            TradeOfferItem.objects.create(
                trade_offer=trade_offer,
                card_id=card_id,
                item_type='requested'
            )
            
        # clear trade from session
        if 'trade_cards' in request.session:
            del request.session['trade_cards']
            
        messages.success(request, f"Trade offer sent to {receiver.username}")
        return redirect('trading')
        
    return redirect('trading')

@login_required
def cancel_trade(request, trade_id):
    """cancel a pending trade you've proposed"""
    trade = get_object_or_404(
        TradeOffer, 
        pk=trade_id, 
        proposer=request.user, 
        status='pending'
    )
    
    trade.status = 'cancelled'
    trade.save()
    
    messages.success(request, "Trade offer cancelled")
    return redirect('trading')

@login_required
def reject_trade(request, trade_id):
    """reject a trade offer you've received"""
    trade = get_object_or_404(
        TradeOffer, 
        pk=trade_id, 
        receiver=request.user, 
        status='pending'
    )
    
    trade.status = 'rejected'
    trade.save()
    
    messages.success(request, "Trade offer rejected")
    return redirect('trading')

@login_required
@transaction.atomic
def accept_trade(request, trade_id):
    """accept a trade offer and exchange cards"""
    trade = get_object_or_404(
        TradeOffer, 
        pk=trade_id, 
        receiver=request.user, 
        status='pending'
    )
    
    # get all cards involved in the trade
    offered_items = trade.items.filter(item_type='offered')
    requested_items = trade.items.filter(item_type='requested')
    
    # verify that proposer still owns the offered cards
    for item in offered_items:
        if not UserCard.objects.filter(user=trade.proposer, card=item.card).exists():
            messages.error(request, "The other user no longer owns one of the offered cards")
            return redirect('trading')
            
    # verify that receiver still owns the requested cards
    for item in requested_items:
        if not UserCard.objects.filter(user=trade.receiver, card=item.card).exists():
            messages.error(request, "You no longer own one of the requested cards")
            return redirect('trading')
    
    # transfer offered cards from proposer to receiver
    for item in offered_items:
        # remove card from proposer's collection
        UserCard.objects.filter(user=trade.proposer, card=item.card).first().delete()
        
        # add card to receiver's collection
        UserCard.objects.create(user=trade.receiver, card=item.card)
        
    # transfer requested cards from receiver to proposer
    for item in requested_items:
        # remove card from receiver's collection
        UserCard.objects.filter(user=trade.receiver, card=item.card).first().delete()
        
        # add card to proposer's collection
        UserCard.objects.create(user=trade.proposer, card=item.card)
        
    # update trade status
    trade.status = 'accepted'
    trade.save()
    
    messages.success(request, "Trade completed successfully!")
    return redirect('trading')
