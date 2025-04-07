from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Card(models.Model):
    # Basic Pokemon information
    pokemon_id = models.IntegerField()
    name = models.CharField(max_length=100)
    image_url = models.URLField()
    
    # Card attributes
    rarity = models.CharField(max_length=20, default="common")
    type = models.CharField(max_length=20, blank=True, null=True)
    hp = models.IntegerField(default=0)
    attack = models.IntegerField(default=0)
    defense = models.IntegerField(default=0)
    
    # Market information
    value = models.IntegerField(default=50)  # Base coin value
    for_sale = models.BooleanField(default=False)
    sale_price = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} (ID: {self.pokemon_id})"

class UserCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'card')
        
    def __str__(self):
        return f"{self.user.username}'s {self.card.name}"
