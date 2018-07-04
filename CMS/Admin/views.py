from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from Admin.models import *
from Admin.serializers import *
from Institution.models import Institution,Employee
from Institution.serializers import InstitutionSerializer
# Create your views here.

class AdminViewSet(viewsets.ModelViewSet):
	queryset = Admin.objects.all()
	serializer_class = AdminSerializer

	@action(methods = ['POST'],detail = False)
	def checkinstitution(self,request):
		#user_id=request.session['id']
		institution_id=request.data.get('id')
		thisinstitution=Institution.objects.get(id=institution_id)
		thisinstitution.status=1
		thisinstitution.save()
		return Response( "成功 ",status = status.HTTP_200_OK)

	'''
	def retrive(self,request,pk=None):#显示某一未通过审核的机构的法人信息？渲染到那个网页？institution/intitution/2/
		queryset=Institution.objects.all()
		thisinstitution=Institution.objects.get(queryset,id=pk)
		allinstitutionse = InstitutionSerializer(thisinstitution, many=True)
		return Response(allinstitutionse.data, status=status.HTTP_200_OK)
		template = loader.get_template('conference.html')
		context = {
		    'institution': thisinstitution,
		}
		return HttpResponse(template.render(context, request))
		#NEED MODIFY
	'''
	@action(methods=['GET'], detail=False)
	def allinstitution(self, request):  # 显示所有未通过审核机构的基本信息
		allinstitution = Institution.objects.filter(status="0")
		allinstitutionse = InstitutionSerializer(allinstitution, many=True)
		return Response(allinstitutionse.data,status=status.HTTP_200_OK)

		template = loader.get_template('conference.html')
		context = {
			'institution': allinstitution,
		}
		return HttpResponse(template.render(context, request))