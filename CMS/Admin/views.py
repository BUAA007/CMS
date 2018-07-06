from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.template import loader
from django.http import HttpResponse
from Admin.models import *
from Admin.serializers import *
from Institution.models import Institution, Employee
from Institution.serializers import InstitutionSerializer


# Create your views here.

class AdminViewSet(viewsets.ModelViewSet):
	queryset = Admin.objects.all()
	serializer_class = AdminSerializer

	@action(methods=['POST'], detail=False)
	def checkinstitution(self, request):
		# user_id=request.session['id']
		institution_id = request.data.get('id')
		thisinstitution = Institution.objects.get(id=institution_id)
		thisinstitution.status = '1'
		thisinstitution.save()
		return Response({"info": "成功 "}, status=status.HTTP_200_OK)

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
	def adminCMS(self, request):  # 显示所有未通过审核机构的基本信息
		allinstitution = Institution.objects.all()
		allinstitutionse = InstitutionSerializer(allinstitution, many=True)

		template = loader.get_template('admin_list.html')
		context = {
			'institutions': allinstitution,
		}
		return render(request, "admin_list.html", context)

	@action(methods=['POST'], detail=False)
	def checkInstitution(self, request):
		# user_id=request.lsession['id']
		institution_id = request.data.get('id')
		thisInstitution = Institution.objects.get(id=institution_id)
		flag = request.data.get('flag')

		if flag == '0':  # 删除
			thisInstitution.delete()
		if flag == '1':
			thisInstitution.status = "1"
			thisInstitution.save()

		emailTitle = "CMS系统提示，机构注册状态发生修改"
		emailContent = "机构id为" + str(institution_id) + "的注册状态发生修改"
		employeeSet = thisInstitution.employee_set.all()
		emailList = []

		for employee in employeeSet:
			emailList.append(employee.email)

		return Response({"info" : "操作成功"}, content_type="application/json")

	@action(methods=['POST'], detail=False)
	def login(self, request):
		if request.method == "POST":
			username = request.data.get('username')
			password = request.data.get('password')
			try:
				admin = Admin.objects.get(username=username, password=password)
				if admin:
					request.session['is_login'] = 'true'  # 定义session信息
					request.session['username'] = username
					request.session['id'] = admin.id
					request.session['type'] = '2'  # 普通用户标记
					request.session.set_expiry(0)
					# template = loader.get_template('base.html')
					# context = {}
					return Response({"info": "管理员登陆成功"}, content_type="application/json")
			except:
				pass
		# return render(request,'base.html',status = status.HTTP_201_CREATED)                ## 登录成功就将url重定向到后台的url
		return Response({'errorInfo': '管理员用户名或密码不正确'}, content_type="application/json")
