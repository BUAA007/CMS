from rest_framework import serializers
from User.models import *

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'

class JoinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Join
		fields = '__all__'