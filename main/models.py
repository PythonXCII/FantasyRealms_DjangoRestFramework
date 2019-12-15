from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    login = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.login


class Deal(models.Model):
    count = models.IntegerField(default=1, unique=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='deals')

    def __str__(self):
        return '{}, Round: {}'.format(self.game.login, self.count)


class Point(models.Model):
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='points')

    class Meta:
        unique_together = ('user', 'deal')

    def __str__(self):
        return '{} Round {} {}: {}'.format(self.deal.game.login, self.deal.count, self.user.username, self.points)