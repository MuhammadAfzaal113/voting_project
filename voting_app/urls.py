# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskListCreateAPIView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-detail'),
    path('contestants/', views.ContestantListAPIView.as_view(), name='contestant-list'),
    # path('send-otp/', views.twilio_send_otp, name='send-otp'),
    # path('cast-vote/', views.cast_vote, name='cast_vote'),
    path('cast-vote/', views.cast_vote_using_mail, name='cast_vote'),
    path('contestants/', views.ContestantListCreateAPIView.as_view(), name='contestant-list-create'),
    path('contestants/<int:pk>/', views.ContestantRetrieveUpdateDestroyAPIView.as_view(), name='contestant-detail'),
    path('contestant-tasks/',  views.ContestantTaskListCreateAPIView.as_view(), name='contestant-task-list-create'),
    path('contestant-tasks/<int:pk>/',  views.ContestantTaskRetrieveUpdateDestroyAPIView.as_view(), name='contestant-task-detail'),
    path('detail-contestant-tasks/',  views.ContestantTaskListCreateAPIView.as_view(), name='contestant-task-list-create'),
    path('detail-contestant-tasks/<int:pk>/',  views.ContestantTaskRetrieveUpdateDestroyAPIView.as_view(), name='contestant-task-detail'),
    path('contestant-task/<int:task_id>/votes/', views.ContestantTaskVotesAPIView.as_view(), name='contestant-task-votes'),
    path('task-votes/', views.TaskVotesAPIView.as_view(), name='task-votes'),
    path('contestant-task/votes/', views.ContestantVotesPerTaskAPIView.as_view(), name='contestant-task-votes-per-task'),
    path('contestant/total-votes/', views.ContestantTotalVotesAPIView.as_view(), name='contestant-total-votes'),
    # path('all-contestant-detail/', views.ContestantDetailAPIView.as_view(), name='contestant-total-votes'),
    path('all-contestant-detail/', views.all_contestant_detail, name='contestant-total-votes'),

]
