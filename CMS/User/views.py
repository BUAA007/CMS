from django.shortcuts import render
from rest_framework import viewsets, response
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from Paper.models import *
from Paper.serializers import *
from User.models import *
from User.serializers import *
from django.template import loader
from django.http import HttpResponse
import re, json
import collections
import hashlib


# Create your views here.

def checklen(pwd):
    return len(pwd) >= 6


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
    # 判断密码长度是否合法
    lenOK = checklen(pwd)
    # 判断是否包含大写字母
    upperOK = checkContainUpper(pwd)
    # 判断是否包含小写字母
    lowerOK = checkContainLower(pwd)
    # 判断是否包含数字
    numOK = checkContainNum(pwd)
    # 判断是否包含符号
    symbolOK = checkSymbol(pwd)
    return (lenOK and upperOK and lowerOK and numOK and symbolOK)


def checkPhonenumber(phone):
    phone_pat = re.compile('1[3458]\\d{9}')
    return re.search(phone_pat, phone)


def checkUsername(username):
    username_pat = re.compile("[a-zA-z]\\w{0,9}")
    return re.search(username_pat, username)


def md5(arg):  # 这是加密函数，将传进来的函数加密
    arg = str(arg)
    return hashlib.md5(arg.encode(encoding='UTF-8')).hexdigest()


# return md5_pwd.hexdigest()#返回加密的数据

def info(msg):
    return json.dumps({'info': msg})


def errorInfo(msg):
    return json.dumps({'errorInfo': msg})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(methods = ['GET'],detail = False)
    def index(self,request):
        return render(request,'judgement.html',status = status.HTTP_201_CREATED)

    @action(methods = ['POST'],detail = False)
    def login(self, request):
        if request.method == "POST":
            username = request.data.get('username')
            password = md5( request.data.get('password') )
            try:
                user = User.objects.get(username=username, password=password)
                if user:
                    request.session['is_login'] = 'true'         #定义session信息
                    request.session['username'] = username
                    request.session['id'] = user.id
                    request.session['type'] = '0'   #普通用户标记
                    request.session.set_expiry(0)
                    # template = loader.get_template('base.html')
                    # context = {}
                    return HttpResponse(info('登陆成功'), content_type="application/json")
            except:
                pass
                #return render(request,'base.html',status = status.HTTP_201_CREATED)                ## 登录成功就将url重定向到后台的url
        return HttpResponse(errorInfo('用户名或密码不正确'), content_type="application/json")

    @action(methods = ['GET'],detail = False)
    def logout(self, request):
        if request.session['is_login'] != 'true':
            return HttpResponse(errorInfo("登入后操作"), content_type="application/json")
        try:
            del request.session['is_login']         # 删除is_login对应的value值
            request.session.flush()                  # 删除django-session表中的对应一行记录
            return HttpResponse(info("登出成功"), content_type="application/json")
        except KeyError:
            pass
        return HttpResponse(errorInfo("登出失败"), content_type="application/json")
        #return render(request,'base.html')             #重定向回主页面


    @action(methods = ['POST'],detail = False)
    def register(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        email = request.data.get("email")
        tel = request.data.get("tel")
        try :
            if User.objects.get(username = username):
                return HttpResponse(errorInfo("该用户已存在"),content_type="application/json")
        except:
            pass
        # if not checkUsername(username):    #必须以字母开头，长度在10位以内
        #    return  HttpResponse(errorInfo("用户名不合法"), content_type="application/json")
        if not checkPassword(password):    #包含大写、小写、符号；长度大于等于8
           return  HttpResponse(errorInfo("密码必须包含大写、小写、符号且长度大于等于8"), content_type="application/json")
        if not password == password2:
           return  HttpResponse(errorInfo("两次密码不一致"), content_type="application/json")
        if not checkPhonenumber(tel):      #手机号位数为11位；开头为1，第二位为3或4或5或8;
           return  HttpResponse(errorInfo("电话号码应为11位"), content_type="application/json")
        user_serializer = UserSerializer(data = request.data)
        password = md5(password)
        if user_serializer.is_valid():
            thisUser = User(
                username = username,
                password = password,
                email = email,
                tel = tel,
                ).save()   
            return HttpResponse(info("success"), content_type="application/json")
            #return render(request,'login.html',status = status.HTTP_201_CREATED)
        return HttpResponse(errorInfo("未知原因失败，请稍后再试"), content_type="application/json") 

    @action(methods = ['GET'],detail = False)
    def info(self, request):
        try:
            pk = request.GET.get("username")
            thisuser = User.objects.get(username = pk)
            result = list()
            result.append(UserSerializer(thisuser).data)
            papers = thisuser.Paper_set.all()
            for paper in papers:
                result.append(PaperSerializer(paper).data)
        except:
            a = collections.OrderedDict({"errorInfo":"服务器出错，请稍后重试。"})
            return Response(a, status = status.HTTP_400_BAD_REQUEST)
        return Response(result, status = status.HTTP_200_OK)

    '''
    @action(methods=['POST'], detail=False)
    def registermeeting(self, request):
        meeting_id = request.data.get("meeting_id")
        user_id = request.data.get("user_id")
        paper_id = request.data.get("paper_id")
        people_name=request.data.get("people_name")
        people_sex=request.data.get("people_sex")
        isbook=request.data.get("isbook")
<<<<<<< HEAD
        #缴费凭证pdf或者照片
        thispaper = Paper.objects.get(id=paper_id)
        print(111)
        if thispaper.status == 1:
            thisuser = User.objects.get(id=user_id)
            thismeeting = Meeting.objects.get(meeting_id=meeting_id)
            thisuser.participate.add(thismeeting)
            return Response({"info": "register meeting success"}, status=status.HTTP_200_OK)
=======
        i=0
        #缴费凭证pdf或者照片
        try:
            thispaper = Paper.objects.get(id=paper_id)
            #print(111)
            if thispaper.status == 1:
                thisuser = User.objects.get(id=user_id)
                thismeeting = Meeting.objects.get(meeting_id=meeting_id)
                for x in people_name:
                    i++

                type_participate(user=thisuser,meeting=thismeeting,people_name=people_name[str(i)],people_sex=people_sex,isbook=isbook)

                thisuser.participate.add(thismeeting)
                return Response({"info": "register meeting success"}, status=status.HTTP_200_OK)

        except:
            pass
>>>>>>> df9aca0e5741b4700138e8219b1f732080555761
        return Response({"errorInfo": "paper is not received"}, status=status.HTTP_200_OK)
    '''

    @action(methods=['POST'], detail=False)
    def listentermmeting(self,request):
        pass

    

    @action(methods=['POST'], detail=False)
    def contribute(self, request):
        meeting_id=request.data.get("meeting_id")
        thismeeting=Meeting.objects.get(meeting_id=meeting_id)
        try:
            user_id=request.session['id']
        except:
            template = loader.get_template('conference.html')
            context = {
                'conference': thismeeting,
                'message':'失败，请登录'
            }
            return HttpResponse(template.render(context, request))
        user_type=request.session['type']
        thisuser = User.objects.get(id=user_id)
        
        thispaper= Paper(author_1=request.data.get("author_1"),
            author_2=request.data.get("author_2"),
            author_3=request.data.get("author_3"),
            title=request.data.get("title"),
            abstract=request.data.get("abstract"),
            keyword=request.data.get("keyword"),
            content=request.FILES['content'],
            #content=request.data.get("content"),
            status=-1,
            owner=thisuser,
            meeting=thismeeting,
        )
        try:
            thispaper.save()
            #thisuser.participate.add(thismeeting) 暂时还未参加会议，需要审核和注册
            template = loader.get_template('conference.html')
            context = {
                'conference': thismeeting,
                'message':'成功'
            }
            return HttpResponse(template.render(context, request))
        except:
            template = loader.get_template('conference.html')
            context = {
                'conference': thismeeting,
                'message':'失败,填写信息错误'
            }
        return HttpResponse(template.render(context, request))

    @action(methods=['POST'], detail=False)
    def modify(self, request):
        paper_id = request.data.get("paper_id")
        thispaper=Paper.objects.get(id=paper_id)
        print(request.data)
        #thismeeting = Meeting.objects.get(meeting_id=meeting_id)
        try:
            user_id = request.session['id']
        except:
            template = loader.get_template('judgement.html')
            context = {
                #'conference': thismeeting,
                'message': '失败，请登录'
            }
            return HttpResponse(template.render(context, request))
        else:
            if thispaper.status==0 or thispaper.status== -1 :
                #thisuser = User.objects.get(id=user_id)
                thispaper.author_1=request.data.get("author_1")
                print(request.data)
                thispaper.author_2=request.data.get("author_2")
                thispaper.author_3=request.data.get("author_3")
                thispaper.title=request.data.get("title")
                thispaper.abstract=request.data.get("abstract")
                thispaper.keyword=request.data.get("keyword")
                      # content=request.data.get("content"),
                thispaper.status="-1"
                thispaper.suggeestion=""
                thispaper.explain=request.data.get("explain")
                thispaper.save()
                thispaper.content = request.FILES['content']
                template = loader.get_template('judgement.html')
                context = {
                    # 'conference': thismeeting,
                    'message': '修改成功，请等待审核'
                }
                return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('judgement.html')
                context = {
                    # 'conference': thismeeting,
                    'message': '失败,该论文不可修改'
                }
                return HttpResponse(template.render(context, request))

    @action(methods=['POST'], detail=False)
    def favorite(self, request):
        try:
            user_id = request.session['id']
        except:
            return Response({"errorInfo":"请登录"}, status=status.HTTP_200_OK)
        else:
            thisuser = User.objects.get(id=user_id)
            meeting=request.data.get("meeting_id")
            thismeeting = Meeting.objects.get(meeting_id=meeting)
            try:
                fae=thisuser.favorite.get(meeting_id=meeting)
            except:
                thisuser.favorite.add(thismeeting)
                thisuser.save()
            else:
                thisuser.favorite.remove(thismeeting)
                thisuser.save()
        finally:
            return Response({"info":"成功"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail = False)
    def allpaper(self,request):
        user_id = request.session['id']
        type = request.session['type']
        if type == 1:
            template = loader.get_template('judgement.html')
            context = {
                # 'conference': thismeeting,
                'message': '失败，不是个体用户'
            }
            return HttpResponse(template.render(context, request))
        else:
            thisuser = User.objects.get(id=user_id)
            # thismeeting = Meeting.objects.get(meeting_id=pk)
            papers = thisuser.paper_set.all()
            template = loader.get_template('judgement.html')
            context = {
                'papers': papers,
            }
            return HttpResponse(template.render(context, request))

class JoinViewSet(viewsets.ModelViewSet):
    queryset = Join.objects.all()
    serializer_class = JoinSerializer

    def create(self, request):
        # user_id=request.session['id']
        # thisuser = User.objects.get(id=user_id)
        # meeting_id=request.data.get("meeting_id")
        # thismeeting=Meeting.objects.get(meeting_id=meeting_id)
        namelist = request.data.get("name")
        genderlist = request.data.get("gender")
        reserlist = request.data.get("reservation")
        receipt = request.FILES['file']
        type = request.data.get("type")
        if type == 1:
            paperid = request.data.get("paper")
            thispaper = Paper.objects.get(id = paperid)
            thismeeting = Paper.meeting
            count = 0
            for name in namelist:
                people = Join(
                    name = name,
                    gender = gender[count],
                    receipt = receipt,
                    #content=request.data.get("content"),
                    reservation = reserlist[count],
                    types = 1,
                    paper = thispaper,
                    meeting = thismeeting,
                )
                people.save()
                count = count + 1
            thispaper.owner.participate.add(thispaper.meeting)
            return Response("info: join success", status=status.HTTP_200_OK)
        count = 0
        for name in namelist:
            meeting_id = request.data.get("meeting")
            thismeeting = Meeting.objects.get(meeting_id = meeting_id)
            people = Join(
                name = name,
                gender = gender[count],
                receipt = receipt,
                #content=request.data.get("content"),
                reservation = reserlist[count],
                types = 2,
                meeting = thismeeting,
            )
            people.save()
            count = count + 1
        return Response("info: listen success", status=status.HTTP_200_OK)