from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class CustomUser(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    last_vote_reset = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.phone_number

class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    video_link = models.URLField() 
    thumbnail = models.ImageField(upload_to='task_thumbnails', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contestant(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='contestant_photos')
    eliminated = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ContestantTask(models.Model):
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    fan_votes = models.PositiveIntegerField(default=0)
    winning_votes = models.PositiveIntegerField(default=0)
    losing_votes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('contestant', 'task')

    def __str__(self):
        return f"{self.contestant.name} - {self.task.name}"

class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contestant_task = models.ForeignKey(ContestantTask, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'contestant_task')

    def clean(self):
        if Vote.objects.filter(user=self.user, contestant_task__task=self.contestant_task.task).exists():
            raise ValidationError("You have already voted for this task.")
    
    def __str__(self):
        return f"{self.user} voted for {self.contestant_task} at {self.voted_at}"

class OTP(models.Model):
    phone_number = models.CharField(max_length=15, default=None)
    email = models.CharField(max_length=255, unique=True, default=None)
    otp = models.CharField(max_length=255, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.phone_number}"

