# views.py

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Task, Contestant, ContestantTask, Vote, OTP
from .serializers import TaskSerializer, ContestantSerializer, OTPSerializer, AllContestantTaskSerializer, ContestantTaskSerializer, ContestantSerializerr
from rest_framework.response import Response
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from django.utils import timezone
from twilio.rest import Client
from django.conf import settings
from rest_framework import status


import http.client
import json
import random

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class ContestantListAPIView(generics.ListAPIView):
    serializer_class = ContestantSerializer
    def get_queryset(self):
        return Contestant.objects.filter(eliminated=False)


@api_view(['POST'])
def send_otp(request):
    phone_number = request.data.get('phone_number')

    try:
      
        user, created = CustomUser.objects.get_or_create(phone_number=phone_number)

      
        existing_otp = OTP.objects.filter(phone_number=phone_number).first()
        if existing_otp:
           
            today = timezone.now().date()
            if existing_otp.created_at.date() == today:
               
                return Response({'message': 'OTP for this number has already been generated today. You can generate OTP next day'}, status=200)

      
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)]) 

        try:
           
            conn = http.client.HTTPSConnection("5ym8yg.api.infobip.com")
            payload = json.dumps({
                "messages": [
                    {
                        "destinations": [{"to": phone_number}],
                        "from": "ServiceSMS",
                        "text": f"Your OTP is: {otp}"
                    }
                ]
            })
            headers = {
                'Authorization': 'App 2e0055abc6915300e8edc3ee5407afc7-22773704-de54-4da1-a018-4672cb0908c2',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            conn.request("POST", "/sms/2/text/advanced", payload, headers)
            res = conn.getresponse()

            
            otp_instance = OTP.objects.create(phone_number=phone_number, otp=otp)

         
            return Response({'message': 'OTP sent successfully'}, status=res.status)

        except IntegrityError:
           
            return Response({'message': 'An error occurred while processing your request'}, status=500)

    except ObjectDoesNotExist:
       
        return Response({'message': 'An error occurred while processing your request'}, status=500)


@api_view(['POST'])
def cast_vote(request):
    phone_number = request.data.get('phone_number')
    otp_entered = request.data.get('otp')

    today = datetime.now().date()

    try:
        otp_record = OTP.objects.get(phone_number=phone_number, otp=otp_entered, created_at__date=today)

        contestant_id = request.data.get('contestant_id')
        contestant = Contestant.objects.get(id=contestant_id)
        contestant.fan_vote_count += 1
        contestant.save()

    
        Vote.objects.create(user=request.user, contestant_task=contestant.task)

        otp_record.delete()

        return Response({'message': 'Vote cast successfully'}, status=200)

    except OTP.DoesNotExist:
        return Response({'message': 'Invalid phone number or OTP'}, status=400)

    except Contestant.DoesNotExist:
        return Response({'message': 'Invalid contestant ID'}, status=400)

    except Exception as e:
        return Response({'message': 'An error occurred while processing your request'}, status=500)


@api_view(['POST'])
def cast_vote(request):
    phone_number = request.data.get('phone_number')
    contestant_id = request.data.get('contestant_id')
    task_id = request.data.get('task_id')
    contestant_task_id = request.data.get('contestant_task_id')
    today = timezone.now().date()
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    time_threshold = timezone.now() - timedelta(hours=24)
    otp_record = OTP.objects.filter(phone_number=phone_number, created_at__gte=time_threshold).order_by('-created_at').first()
    if not otp_record:
        return Response({'message': 'Invalid OTP or OTP has expired'}, status=400)

    verification_check = client.verify.v2.services(otp_record.otp).verification_checks.create(
        to=phone_number, code=request.data.get('otp')
    )
    if verification_check.status != 'approved':
        return Response({'message': 'Invalid OTP'}, status=400)

    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user:
        return Response({'message': 'User not found'}, status=404)

    contestant_task = ContestantTask.objects.filter(contestant_id=contestant_id, task_id=task_id).first()
    if not contestant_task:
        return Response({'message': 'Contestant task not found'}, status=404)

    existing_vote = Vote.objects.filter(user=user, contestant_task=contestant_task, voted_at__date=today).first()
    if existing_vote:

        existing_vote.save() 
        return Response({'message': 'Your vote has been updated successfully'}, status=200)

 
    contestant_task.fan_votes += 1
    contestant_task.save()

    try:
        vote = Vote.objects.create(user=user, contestant_task=contestant_task)
    except ValidationError as e:
        return Response({'message': str(e)}, status=400)
    return Response({'message': 'Vote cast successfully'}, status=200)

class ContestantListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ContestantSerializer
    def get_queryset(self):
        return Contestant.objects.filter(eliminated=False)

class ContestantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContestantSerializer
    def get_queryset(self):
        return Contestant.objects.filter(eliminated=False)

class ContestantTaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.filter(contestant__eliminated=False)

class ContestantTaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.filter(contestant__eliminated=False)

class ContestantTaskListCreateAPIView(generics.ListAPIView):
    serializer_class = AllContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.filter(contestant__eliminated=False)


class ContestantTaskVotesAPIView(generics.ListAPIView):
    serializer_class = ContestantTaskSerializer

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return ContestantTask.objects.filter(task_id=task_id, contestant__eliminated=False)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_fan_votes = queryset.aggregate(total_fan_votes=Sum('fan_votes'))['total_fan_votes']
        total_winning_votes = queryset.aggregate(total_winning_votes=Sum('winning_votes'))['total_winning_votes']
        total_losing_votes = queryset.aggregate(total_losing_votes=Sum('losing_votes'))['total_losing_votes']
        response_data = {
            'total_fan_votes': total_fan_votes,
            'total_winning_votes': total_winning_votes,
            'total_losing_votes': total_losing_votes
        }
        return Response(response_data)
class TaskVotesAPIView(generics.ListAPIView):
    serializer_class = ContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.values('task_id').annotate(total_votes=Sum('fan_votes') + Sum('winning_votes') + Sum('losing_votes'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = [{'task_id': item['task_id'], 'total_votes': item['total_votes']} for item in queryset]
        return Response(response_data)


class ContestantVotesPerTaskAPIView(generics.ListAPIView):
    serializer_class = AllContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.all(contestant__eliminated=False)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for contestant_task in queryset:
            task_data = {
                'task_id': contestant_task.task_id,
                'contestant_id': contestant_task.contestant_id,
                'total_fan_votes': contestant_task.fan_votes,
                'total_winning_votes': contestant_task.winning_votes,
                'total_losing_votes': contestant_task.losing_votes
            }
            data.append(task_data)
        return Response(data)


class ContestantTotalVotesAPIView(generics.ListAPIView):
    serializer_class = ContestantTaskSerializer

    def get_queryset(self):
        return ContestantTask.objects.all(contestant__eliminated=False)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = {}
        for contestant_task in queryset:
            contestant_id = contestant_task.contestant_id
            if contestant_id not in data:
                data[contestant_id] = {
                    'contestant_id': contestant_id,
                    'total_fan_votes': 0,
                    'total_winning_votes': 0,
                    'total_losing_votes': 0
                }
            data[contestant_id]['total_fan_votes'] += contestant_task.fan_votes
            data[contestant_id]['total_winning_votes'] += contestant_task.winning_votes
            data[contestant_id]['total_losing_votes'] += contestant_task.losing_votes
        return Response(list(data.values()))


@api_view(['GET'])
def all_contestant_detail(request):
    queryset = Contestant.objects.all().values()
    # serializer = ContestantSerializerr(queryset, many=True)
    for contest in queryset:
        contest['photo'] = 'media/' + contest['photo']
        contest['tasks'] = ContestantTask.objects.filter(contestant_id=contest['id']).values('task', 'fan_votes', 'winning_votes', 'losing_votes').order_by('-id')
        for i in contest['tasks']:
            i['task'] = Task.objects.filter(id=i['task']).all().values('id', 'name', 'video_link', 'thumbnail')[0]
            i['task']['thumbnail'] = 'media/' + i['task']['thumbnail']
            i['total_votes'] = i['fan_votes'] + i['winning_votes'] - i['losing_votes']

    sorted_contestants = sorted(queryset, key=lambda x: x['eliminated'])
    return Response(sorted_contestants)



class ContestantDetailAPIView(generics.ListAPIView):
    serializer_class = ContestantSerializerr
    def get_queryset(self):
        return Contestant.objects.filter(eliminated=False)


@api_view(['POST'])
def twilio_send_otp(request):
    phone_number = request.data.get('phone_number')

    try:
        # Get or create CustomUser object
        user, created = CustomUser.objects.get_or_create(phone_number=phone_number)

        # Check if an OTP has already been generated today
        existing_otp = OTP.objects.filter(phone_number=phone_number).first()
        if existing_otp:
            today = timezone.now().date()
            if existing_otp.created_at.date() == today:
                return Response({'message': 'OTP for this number has already been generated today. You can generate OTP next day'}, status=status.HTTP_200_OK)

        # Generate OTP
        # otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Send OTP via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        service = client.verify.v2.services.create(friendly_name='Isarb Voting')
        # message = client.messages.create(
        #     body=f"Your OTP is: {otp}",
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=phone_number
        # )
        verification = client.verify.v2.services(service.sid).verifications.create(
            to=phone_number, channel='sms')


        # Save OTP instance to the database
        otp_instance = OTP.objects.create(phone_number=phone_number, otp=service.sid)

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': f'An error occurred while processing your request: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
