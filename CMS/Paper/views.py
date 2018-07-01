from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from Paper.models import *
from Paper.serializers import *
# Create your views here.

class PaperViewSet(viewsets.ModelViewSet):
	queryset = Paper.objects.all()
	serializer_class = PaperSerializer
