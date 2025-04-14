import random
import requests
from abc import ABC, abstractmethod
from .models import Card

class CardFactory(ABC):
    """Abstract Card Factory base class"""
    
    @abstractmethod
    def create_card(self, data):
        """Create a card from data"""
        pass
    
    @abstractmethod
    def get_data(self, identifier):
        """Get data needed for card creation"""
        pass

class PokemonCardFactory(CardFactory):
    """Concrete factory for creating Pokémon cards from the PokéAPI"""
    
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
    
    def get_data(self, pokemon_id):
        """Fetch pokemon data from the PokéAPI"""
        url = f"{self.POKEAPI_BASE_URL}/pokemon/{pokemon_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_card(self, pokemon_data):
        """Create a Card instance from PokéAPI data"""
        if not pokemon_data:
            return None
        
        # Generate random stats for the card
        stats = self._generate_random_stats()
        
        # Get the pokemon type
        types = pokemon_data.get('types', [])
        primary_type = types[0]['type']['name'] if types else None
        
        # Create and return a new Card
        card = Card(
            pokemon_id=pokemon_data['id'],
            name=pokemon_data['name'].capitalize(),
            image_url=pokemon_data['sprites']['other']['official-artwork']['front_default'],
            type=primary_type,
            hp=stats['hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            value=stats['value']
        )
        card.save()
        return card
    
    def _generate_random_stats(self):
        """Generate random stats for a card"""
        return {
            'hp': random.randint(30, 100),
            'attack': random.randint(20, 80),
            'defense': random.randint(20, 80),
            'value': random.randint(40, 100)
        }
    
    def get_random_pokemon_ids(self, count=5, max_id=151):
        """Get a list of random pokemon IDs"""
        return random.sample(range(1, max_id + 1), count)
        
    def generate_starter_cards(self, count=5):
        """Generate a set of starter cards"""
        cards = []
        pokemon_ids = self.get_random_pokemon_ids(count)
        
        for pokemon_id in pokemon_ids:
            pokemon_data = self.get_data(pokemon_id)
            if pokemon_data:
                card = self.create_card(pokemon_data)
                if card:
                    cards.append(card)
        
        return cards 