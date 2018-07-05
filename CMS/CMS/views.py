from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http import HttpResponse
from django.shortcuts import render
from Institution.models import *
from User.models import *
import re,json
def base(request):
    return render(request,'base.html')

def login(request):
    return render(request,'login.html')

def user_register(request):
    return render(request,'user_register.html')

def institution_register(request):
    return render(request,'institution_register.html')

def personal_info(request):
	try:
		if request.session["type"] == '1':
			employee = Employee.objects.get(username = request.session["username"])
			email = employee.email
			tel = employee.tel
			institution = employee.institution.name
			return render(request, 'personal_info.html', {'email' : email, 'tel' : tel, 'institution' : institution})
		else :
			user = User.objects.get(username = request.session["username"])
			email = user.email
			tel = user.tel
			return render(request, 'personal_info.html', {'email' : email, 'tel' : tel})
	except:
		pass
	return render(request, 'login.html')




def download(request):
    def file_iterator(file_name, chunk_size=512):
            with open(file_name, "rb") as f:
                    while True:
                            c = f.read(chunk_size)
                            if c:
                                    yield c
                            else:
                                    break
    try:
            url = "/home/ubuntu/CMS/CMS/media/download/"
            rootpath = request.path
            tmp = rootpath.split("/")
            url+=tmp[-1]
    except:
            return Response(a, status = status.HTTP_400_BAD_REQUEST)
    if url is not None:
            response = StreamingHttpResponse(file_iterator(url))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(tmp[-1])
            return response
    a = collections.OrderedDict({"errorInfo":"服务器出错，请稍后重试。"})
    return Response(a, status = status.HTTP_400_BAD_REQUEST)

def logout(request):
	try:
		# if request.session['is_login'] != 'true':
		# 	return HttpResponse(errorInfo("登入后操作"), content_type="application/json")
		del request.session['is_login']         # 删除is_login对应的value值
		request.session.flush()                  # 删除django-session表中的对应一行记录
		return render(request, 'base.html', {'info' : '登出成功'})
	except:
		pass
	return render(request, 'base.html',{'errorInfo' : "请先登录"})

    #return render(request,'base.html')             #重定向回主页面
def info(msg):
	return json.dumps({'info': msg})

def errorInfo(msg):
	return json.dumps({'errorInfo': msg})

def release(request):
	try:
		if request.session["type"] == '1':
			return render(request, 'release_meeting.html')
		else:
			return render(request, 'login.html')
	except:
		pass
	return render(request, 'login.html')
