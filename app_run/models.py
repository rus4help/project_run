from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'Забег инициализирован'),
        ('in_progress', 'Забег начат'),
        ('finished', 'Забег закончен'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='init')

class AthleteInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.IntegerField(null=True, blank=True)
    goals = models.TextField(blank=True)

class Challenge(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.TextField(default="Сделай 10 Забегов!")