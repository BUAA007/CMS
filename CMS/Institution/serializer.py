from rest_framework import serializers
from Institution.models import Institution

class NormalUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = Institution
		fields = '__all__'