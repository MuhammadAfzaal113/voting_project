from rest_framework import serializers
from .models import CustomUser, Task, Contestant, ContestantTask, Vote, OTP

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'last_vote_reset']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'video_link', 'created_at']

class ContestantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestant
        fields = ['id', 'name', 'photo']

class ContestantTaskSerializer(serializers.ModelSerializer):
    contestant = ContestantSerializer()
    task = TaskSerializer()

    class Meta:
        model = ContestantTask
        fields = ['id', 'contestant', 'task', 'fan_votes', 'winning_votes', 'losing_votes']

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'contestant_task', 'voted_at']


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'phone_number', 'otp', 'created_at']
        read_only_fields = ['id', 'created_at']


class AllContestantTaskSerializer(serializers.ModelSerializer):
    contestant = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = ContestantTask
        fields = ['id', 'contestant', 'task', 'fan_votes', 'winning_votes', 'losing_votes']

    def get_contestant(self, obj):
        # Serialize the contestant field
        contestant = obj.contestant
        return {'id': contestant.id, 'name': contestant.name, 'photo': contestant.photo.url}  # Customize as needed

    def get_task(self, obj):
        # Serialize the task field
        task = obj.task
        return {'id': task.id, 'name': task.name, 'description': task.description, 'video_link': task.video_link}  # Customize as needed
    

class TaskSerializerr(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'video_link']

class ContestantTaskSerializerr(serializers.ModelSerializer):
    task = TaskSerializerr()

    class Meta:
        model = ContestantTask
        fields = ['task','fan_votes', 'winning_votes', 'losing_votes']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        total_votes = instance.fan_votes + instance.winning_votes + instance.losing_votes
        representation['total_votes'] = total_votes
        return representation

class ContestantSerializerr(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    tasks = ContestantTaskSerializerr(many=True)

    class Meta:
        model = Contestant
        fields = ['id', 'name', 'photo', 'tasks','photo_url']
    
    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None
