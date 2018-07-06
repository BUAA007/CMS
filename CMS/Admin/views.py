from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from Admin.models import *
from Admin.serializers import *
from Institution.models import Institution, Employee
from Institution.serializers import InstitutionSerializer

PAGE_MAX = 9
# Create your views here.

class AdminViewSet(viewsets.ModelViewSet):
	queryset = Admin.objects.all()
	serializer_class = AdminSerializer

	@action(methods=['GET'], detail=False)
	def search(self, request):
		try:
			if request.session["is_login"] == 'true' and request.session["type"] == '2':
				pk = request.GET['word']
				if pk == "":
					return HttpResponseRedirect("/myadmin/adminCMS/")

				try:
					queryset = Institution.objects.get(id=int(pk))
				except:
					return render(request, "admin_search.html", {"errorInfo" : "未查询到机构"})
				context = {
					'institution': queryset,
					'info' : "success"
				}
				return render(request, "admin_search.html", context)
		except:
			pass
		return render(request, "base.html")

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
		try:
			if request.session["is_login"] == 'true' and request.session["type"] == '2':
				try:
					page = int(request.GET["page"])
				except(KeyError, ValueError):
					page = 1
				allinstitution = Institution.objects.all()
				allinstitutionse = InstitutionSerializer(allinstitution, many=True)

				template = loader.get_template('admin_list.html')
				context = {
				'institutions': allinstitution,
				}
				if not len(allinstitution):
					total_page = 1
				else:
					total_page = (len(allinstitution) - 1)
				pages, pre_page, next_page = get_pages(total_page, page)
				allinstitution = allinstitution[PAGE_MAX * (page - 1): PAGE_MAX * page]
				context['institutions'] = allinstitution
				context['page'] = page
				context['pages'] = pages
				context['pre_page'] = pre_page
				context['next_page'] = next_page
				return render(request, "admin_list.html", context)
		except:
			pass
		return render(request, "base.html")

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

		return Response({"info": "操作成功"}, content_type="application/json")

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

def get_pages(total_page, cur_page):
	pages = [i + 1 for i in range(total_page)]
	if cur_page > 1:
		pre_page = cur_page - 1
	else:
		pre_page = 1
	if cur_page < total_page:
		next_page = cur_page + 1
	else:
		next_page = total_page
	if cur_page <= 2:
		pages = pages[:5]
	elif total_page - cur_page <= 2:
		pages = pages[-5:]
	else:
		pages = filter(lambda x: abs(x - cur_page) <= 2, pages)
	return pages, pre_page, next_page