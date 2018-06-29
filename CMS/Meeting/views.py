from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from .models import Meeting
from .serializers import MeetingSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    
    @action(methods = ["POST"], detail = False)
    def Search(self, request):
        normal_user_queryset = NormalUserViewSet().GetQueryset(request)
        normal_user_serializer = NormalUserSerializer(0)
        for user in normal_user_queryset:
            normal_user_serializer = NormalUserSerializer(user)
            resource_serializer = ResourceSerializer(user.buyresources.all())
            institution_serializer = InstitutionSerializer(user.expert.institution_set.all())
            result = resource_serializer.data+normal_user_serializer.data
        
            return Response(result)
