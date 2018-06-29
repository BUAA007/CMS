from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from User.models import *
from User.serializers import *
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer