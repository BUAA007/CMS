from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from User.models import *
from User.serializers import *
from django.template import loader
from django.http import HttpResponse
import re,json
import hashlib
# Create your views here.
def checklen(pwd):
	return len(pwd)>=6

def checkContainUpper(pwd):
	pattern = re.compile('[A-Z]+')
	match = pattern.findall(pwd)

	if match:
		return True
	else:
		return False

def checkContainNum(pwd):
	pattern = re.compile('[0-9]+')
	match = pattern.findall(pwd)
	if match:
		return True
	else:
		return False

def checkContainLower(pwd):
	pattern = re.compile('[a-z]+')
	match = pattern.findall(pwd)

	if match:
		return True
	else:
		return False

def checkSymbol(pwd):
	pattern = re.compile('([^a-z0-9A-Z])+')
	match = pattern.findall(pwd)
	if match:
		return True
	else:
		return False

def checkPassword(pwd):
	#判断密码长度是否合法
	lenOK=checklen(pwd)
	#判断是否包含大写字母
	upperOK=checkContainUpper(pwd)
	#判断是否包含小写字母
	lowerOK=checkContainLower(pwd)
	#判断是否包含数字
	numOK=checkContainNum(pwd)
	#判断是否包含符号
	symbolOK=checkSymbol(pwd)
	return (lenOK and upperOK and lowerOK and numOK and symbolOK )

def checkPhonenumber(phone):
	phone_pat = re.compile('1[3458]\\d{9}')
	return re.search(phone_pat, phone)

def checkUsername(username):
	username_pat = re.compile("[a-zA-z]\\w{0,9}")
	return re.search(username_pat, username)

def md5(arg):#这是加密函数，将传进来的函数加密
	arg = str(arg)
	return hashlib.md5(arg.encode(encoding='UTF-8')).hexdigest()
	#return md5_pwd.hexdigest()#返回加密的数据

def info(msg):
	return json.dumps({'info': msg})

def errorInfo(msg):
	return json.dumps({'errorInfo': msg})

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer

	
	@action(methods = ['GET'],detail = False)
	def index(self,request):
	    return render(request,'conference.html',status = status.HTTP_201_CREATED)

	@action(methods = ['POST'],detail = False)
	def login(self, request):
	    if request.method == "POST":
	        username = request.data.get('username')
	        password = mad5( request.data.get('password') )
	        user = User.objects.filter(username=username, password=password)
	        '''
	        template = loader.get_template('index.html')
	        context = {
	            'latest_question_list': latest_question_list,
	        }
	        return HttpResponse(template.render(context, request))
	        '''
	        if user:
	            request.session['is_login'] = 'true'         #定义session信息
	            request.session['username'] = username
	            request.session.set_expiry(0)
	            return render(request,'base.html',status = status.HTTP_201_CREATED)                ## 登录成功就将url重定向到后台的url
	    return HttpResponse(errorInfo('Username/Passwd is wrong'), content_type="application/json")

	@action(methods = ['GET'],detail = False)
	def logout(self, request):
	    try:
	        del request.session['is_login']         # 删除is_login对应的value值
	        request.session.flush()                  # 删除django-session表中的对应一行记录
	    except KeyError:
	        pass
	    return render(request,'base.html')             #重定向回主页面


	@action(methods = ['POST'],detail = False)
	def register(self, request):
	    username = request.data.get("username")
	    password = request.data.get("password")
	    password2 = request.data.get("password2")
	    email = request.data.get("email")
	    tel = request.data.get("tel")
	    try:
	       if not User.objects.get(username = username):
	           return  HttpResponse(errorInfo("用户名已存在"), content_type="application/json")
	    except:
	    	pass
	    if not checkUsername(username):    #必须以字母开头，长度在10位以内
	       return  HttpResponse(errorInfo("用户名不合法"), content_type="application/json")
	    if not checkPassword(password):    #包含大写、小写、符号；长度大于等于8
	       return  HttpResponse(errorInfo("密码不合法"), content_type="application/json")
	    if not password == password2:
	       return  HttpResponse(errorInfo("确认密码不合法"), content_type="application/json")
	    if not checkPhonenumber(tel):      #手机号位数为11位；开头为1，第二位为3或4或5或8;
	       return  HttpResponse(errorInfo("电话号码不合法"), content_type="application/json")   
	    user_serializer = UserSerializer(data = request.data)
	    password = md5(password)
	    if user_serializer.is_valid():
	        thisUser = User(
	            username = username,
	            password = password,
	            email = email,
	            tel = tel,
	            ).save()
	        return render(request,'login.html',status = status.HTTP_201_CREATED)
	    return HttpResponse(errorInfo("未知原因失败，请稍后再试"), content_type="application/json")


	@action(methods=['POST'], detail=False)
	def registermeeting(self, request):
		meeting_id = request.data.get("meeting_id")
		user_id = request.data.get("user_id")
		thisuser=User.objects.get(id=user_id)
		thismeeting=Meeting.objects.get(meeting_id=meeting_id)
		thisuser.participate.add(thismeeting)
		return Response("info: register meeting succsss",status=status.HTTP_200_OK)

	@action(methods=['POST'], detail=False)
	def registermeeting(self, request):
		user_id = request.data.get("user_id")
		thisuser = User.objects.get(id=user_id)
		thispaper= 