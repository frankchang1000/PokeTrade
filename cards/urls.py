from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.collection, name='collection'),
    path('generate-card/', views.generate_new_card, name='generate_card'),
    path('search-cards/', views.search_cards, name='search_cards'),
] 