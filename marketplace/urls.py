from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('create-listing/<int:card_id>/', views.create_listing, name='create_listing'),
    path('remove-listing/<int:listing_id>/', views.remove_listing, name='remove_listing'),
    path('purchase/<int:listing_id>/', views.purchase_card, name='purchase_card'),
    
    path('trading/', views.trading, name='trading'),
    path('trading/propose/', views.propose_trade, name='propose_trade'),
    path('trading/add-card/', views.add_card_to_trade, name='add_card_to_trade'),
    path('trading/remove-card/', views.remove_card_from_trade, name='remove_card_from_trade'),
    path('trading/offer/<int:user_id>/', views.submit_trade_offer, name='submit_trade_offer'),
    path('trading/cancel/<int:trade_id>/', views.cancel_trade, name='cancel_trade'),
    path('trading/accept/<int:trade_id>/', views.accept_trade, name='accept_trade'),
    path('trading/reject/<int:trade_id>/', views.reject_trade, name='reject_trade'),
] 