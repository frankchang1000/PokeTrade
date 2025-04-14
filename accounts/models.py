from django.db import models
from django.contrib.auth.models import User

# We'll use Django's built-in User model for authentication
# This Profile model extends the User model to add any additional fields we need
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.IntegerField(default=500)  # Default starter currency
    
    def __str__(self):
        return f"{self.user.username}'s profile"
