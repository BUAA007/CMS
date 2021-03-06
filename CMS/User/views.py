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
from django.http import HttpResponse, HttpResponseRedirect
import re, json
import collections
import hashlib
import sys
sys.path.append('../')
from Admin import cmsem
PAGE_MAX = 9

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


def checkEmail(email):
    email_pat = re.compile('[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$')
    return re.search(email_pat, email)


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

    @action(methods=['GET'], detail=False)
    def index(self, request):
        return render(request, 'judgement.html', status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        if request.method == "POST":
            username = request.data.get('username')
            password = md5(request.data.get('password'))
            try:
                user = User.objects.get(username=username, password=password)
                if user:
                    request.session['is_login'] = 'true'  # 定义session信息
                    request.session['username'] = username
                    request.session['id'] = user.id
                    request.session['type'] = '0'  # 普通用户标记
                    request.session.set_expiry(0)
                    # template = loader.get_template('base.html')
                    # context = {}
                    return HttpResponse(info('登陆成功'), content_type="application/json")
            except:
                pass
            # return render(request,'base.html',status = status.HTTP_201_CREATED)                ## 登录成功就将url重定向到后台的url
        return HttpResponse(errorInfo('用户名或密码不正确'), content_type="application/json")

    @action(methods=['GET'], detail=False)
    def logout(self, request):
        if request.session['is_login'] != 'true':
            return HttpResponse(errorInfo("登入后操作"), content_type="application/json")
        try:
            del request.session['is_login']  # 删除is_login对应的value值
            request.session.flush()  # 删除django-session表中的对应一行记录
            return HttpResponse(info("登出成功"), content_type="application/json")
        except KeyError:
            pass
        return HttpResponse(errorInfo("登出失败"), content_type="application/json")

    # return render(request,'base.html')             #重定向回主页面

    @action(methods=['POST'], detail=False)
    def register(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        email = request.data.get("email")
        tel = request.data.get("tel")
        try:
            if User.objects.get(username=username):
                return HttpResponse(errorInfo("该用户已存在"), content_type="application/json")
        except:
            pass
        # if not checkUsername(username):    #必须以字母开头，长度在10位以内
        #    return  HttpResponse(errorInfo("用户名不合法"), content_type="application/json")
        if not checkPassword(password):  # 包含大写、小写、符号；长度大于等于8
            return HttpResponse(errorInfo("密码必须包含大写、小写、符号且长度大于等于8"), content_type="application/json")
        if not password == password2:
            return HttpResponse(errorInfo("两次密码不一致"), content_type="application/json")
        if not checkPhonenumber(tel):  # 手机号位数为11位；开头为1，第二位为3或4或5或8;
            return HttpResponse(errorInfo("电话号码应为11位"), content_type="application/json")
        password = md5(password)
        thisUser = User(
            username=username,
            password=password,
            email=email,
            tel=tel,
        ).save()
        emailTitle = "CMS系统提示，用户注册成功"
        emailContent = "用户名为" + str(username) + "的用户信息，已经在CMS系统中注册成功" 
        emailList = []
        emailList.append(email)
        cmsem.send_mail(emailList, emailTitle, emailContent)
        return HttpResponse(info("success"), content_type="application/json")
        # return render(request,'login.html',status = status.HTTP_201_CREATED)
        return HttpResponse(errorInfo("未知原因失败，请稍后再试"), content_type="application/json")

    @action(methods=['GET'], detail=False)
    def info(self, request):
        try:
            pk = request.GET.get("username")
            thisuser = User.objects.get(username=pk)
            result = list()
            result.append(UserSerializer(thisuser).data)
            papers = thisuser.Paper_set.all()
            for paper in papers:
                result.append(PaperSerializer(paper).data)
        except:
            a = collections.OrderedDict({"errorInfo": "服务器出错，请稍后重试。"})
            return Response(a, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def updatePassword(self, request):
        try:
            thisUser = User.objects.get(username=request.session['username'])
            password = request.data.get("password")
            # return HttpResponse(errorInfo(str(password)),content_type="application/json")
            if not checkPassword(password):  # 包含大写、小写、符号；长度大于等于8
                return HttpResponse(errorInfo("密码不正确，必须包含大写、小写、符号且长度大于等于8"),
                                    content_type="application/json")
            password = md5(password)
            thisUser.password = password
            thisUser.save(update_fields=['password'])
            return HttpResponse(info("success"), content_type="application/json")
        except:
            pass
        return HttpResponse(errorInfo("查无此人"), content_type="application/json")

    @action(methods=['POST'], detail=False)
    def updateEmail(self, request):
        try:
            thisUser = User.objects.get(username=request.session['username'])
            email = request.data.get("email")
            if not checkEmail(email):  # 包含大写、小写、符号；长度大于等于8
                return HttpResponse(errorInfo("邮箱格式不合法"), content_type="application/json")
            thisUser.email = email
            thisUser.save(update_fields=['email'])
            return HttpResponse(info("success"), content_type="application/json")
        except:
            pass
        return HttpResponse(errorInfo("查无此人"), content_type="application/json")

    @action(methods=['POST'], detail=False)
    def updateTel(self, request):
        try:
            thisUser = User.objects.get(username=request.session['username'])
            tel = request.data.get("tel")
            if not checkPhonenumber(tel):  # 包含大写、小写、符号；长度大于等于8
                return HttpResponse(errorInfo("电话号码不合法"), content_type="application/json")
            thisUser.tel = tel
            thisUser.save(update_fields=['tel'])
            return HttpResponse(info("success"), content_type="application/json")
        except:
            pass
        return HttpResponse(errorInfo("查无此人"), content_type="application/json")

    @action(methods=['POST'], detail=False)
    def listentermmeting(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def contribute(self, request):
        meeting_id = request.data.get("meeting_id")
        thismeeting = Meeting.objects.get(meeting_id=meeting_id)
        try:
            user_id = request.session['id']
        except:
            template = loader.get_template('conference.html')
            context = {
                'conference': thismeeting,
                'message': '失败，请登录'
            }
            url = "../../../meeting/?message=请登录" + str(thismeeting.meeting_id)
            return HttpResponseRedirect(url)
        if timezone.now()<=thismeeting.ddl_date:
            user_type = request.session['type']
            thisuser = User.objects.get(id=user_id)

            thispaper = Paper(author_1=request.data.get("author_1"),
                          author_2=request.data.get("author_2"),
                          author_3=request.data.get("author_3"),
                          title=request.data.get("title"),
                          abstract=request.data.get("abstract"),
                          keyword=request.data.get("keyword"),
                          content=request.FILES['content'],
                          # content=request.data.get("content"),
                          status=-1,
                          owner=thisuser,
                          meeting=thismeeting,
                          )
            try:
                thispaper.save()
            # thisuser.participate.add(thismeeting) 暂时还未参加会议，需要审核和注册
                template = loader.get_template('conference.html')
                context = {
                    'conference': thismeeting,
                    'message': '成功'
                }
                url = "../../../meeting/"+ str(thismeeting.meeting_id)+"/?message=成功"
                return HttpResponseRedirect(url)
            except:
                template = loader.get_template('conference.html')
                context = {
                    'conference': thismeeting,
                    'message': '失败,填写信息错误'
                }
                url = "../../../meeting/"+ str(thismeeting.meeting_id)+"/?message=填写错误"
                return HttpResponseRedirect(url)
        else:
            template = loader.get_template('conference.html')
            context = {
                'conference': thismeeting,
                'message': '已超过投稿时间，无法投稿'
            }
            url="../../../meeting/"+ str(thismeeting.meeting_id)+"/?message=超过投稿时间"
            return HttpResponseRedirect(url)
            #return HttpResponse(template.render(context, request))
    @action(methods=['POST'], detail=False)
    def modify(self, request):
        try:
            user_id = request.session['id']
        except:
            return Response("失败，请登录",status=status.HTTP_200_OK)
            template = loader.get_template('judgement.html')
            context = {
                # 'conference': thismeeting,
                'message': '失败，请登录'
            }
            url="../allpaper/?message=请登录"
            return HttpResponseRedirect(url)

        else:
            try:
                paper_id = request.data.get("paper_id")
                thispaper = Paper.objects.get(id=paper_id)
            except:
                thisuser = User.objects.get(id=user_id)
                papers = thisuser.paper_set.all()
                template = loader.get_template('judgement.html')
                context = {
                    'papers': papers,
                    'message': '失败,填写论文编号错误'
                }
                url = "../allpaper/?message=填写编号错误"
                return HttpResponseRedirect(url)

            else:
                if timezone.now()<=thispaper.meeting.result_notice_date:
                    if thispaper.status == 0 or thispaper.status == -1:
                    # thisuser = User.objects.get(id=user_id)
                        thispaper.author_1 = request.data.get("author_1")
                        print(request.data)
                        thispaper.author_2 = request.data.get("author_2")
                        thispaper.author_3 = request.data.get("author_3")
                        thispaper.title = request.data.get("title")
                        thispaper.abstract = request.data.get("abstract")
                        thispaper.keyword = request.data.get("keyword")
                        thispaper.status = "-1"
                        thispaper.suggestion = "None"
                        thispaper.explain = request.data.get("explain")
                        thispaper.save()

                        thispaper.content = request.FILES['content']
                        thispaper.save()
                        thisuser = User.objects.get(id=user_id)
                        papers = thisuser.paper_set.all()
                        template = loader.get_template('judgement.html')
                        context = {
                            'papers': papers,
                            'message': '修改成功，请等待审核'
                        }
                        url = "../allpaper/?message=成功，请等待审核"
                        return HttpResponseRedirect(url)

                    else:
                        thisuser = User.objects.get(id=user_id)
                        # thismeeting = Meeting.objects.get(meeting_id=pk)
                        papers = thisuser.paper_set.all()
                        template = loader.get_template('judgement.html')
                        context = {
                            'papers': papers,
                            'message': '失败,该论文不可修改'
                        }
                        url = "../allpaper/?message=论文不可修改"
                        return HttpResponseRedirect(url)

                else:
                    thisuser = User.objects.get(id=user_id)
                    # thismeeting = Meeting.objects.get(meeting_id=pk)
                    papers = thisuser.paper_set.all()
                    template = loader.get_template('judgement.html')
                    context = {
                        'papers': papers,
                        'message': '失败,已超过修改稿截止日期'
                    }
                    url = "../allpaper/?message=超过修改稿截止日期"
                    return HttpResponseRedirect(url)


    @action(methods=['POST'], detail=False)
    def favorite(self, request):
        try:
            user_id = request.session['id']
        except:
            return Response({"errorInfo": "请登录"}, status=status.HTTP_200_OK)
        else:
            thisuser = User.objects.get(id=user_id)
            meeting = request.data.get("meeting_id")
            thismeeting = Meeting.objects.get(meeting_id=meeting)
            try:
                fae = thisuser.favorite.get(meeting_id=meeting)
            except:
                thisuser.favorite.add(thismeeting)
                thisuser.save()
            else:
                thisuser.favorite.remove(thismeeting)
                thisuser.save()
        finally:
            return Response({"info": "成功"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def allfavorite(self, request):
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        user_id = request.session['id']
        user_type=request.session["type"]
        if user_type=="1":
            return Response("请登录个人用户查看")
        else:
            user_id=request.session['id']
            thisuser=User.objects.get(id=user_id)
            #print(thisuser.name)
            allfavorite=thisuser.favorite.all().order_by('-meeting_id')
            #print(allfavorite)
            template = loader.get_template('conference_list.html')

            def check_time(conference):
                now = timezone.now()
                if now <= conference.ddl_date:
                    conference.status = "投稿中"
                elif now <= conference.result_notice_date:
                    conference.status = "已截稿"
                elif now <= conference.regist_attend_date:
                    conference.status = "注册中"
                elif now <= conference.meeting_date:
                    conference.status = "截止注册"
                elif now <= conference.meeting_end_date:
                    conference.status = "会议中"
                else:
                    conference.status = "会议完成"

            list(map(check_time, allfavorite))
            context = {
                'conference_list': allfavorite,
            }
            if not len(allfavorite):
                total_page = 1
            else:
                total_page = (len(allfavorite) - 1) // PAGE_MAX + 1
            pages, pre_page, next_page = get_pages(total_page, page)
            papers = allfavorite[PAGE_MAX * (page - 1): PAGE_MAX * page]

            context['conference_list'] = allfavorite
            context['page'] = page
            context['pages'] = pages
            context['pre_page'] = pre_page
            context['next_page'] = next_page
            return HttpResponse(template.render(context, request))



    @action(methods=['GET'], detail=False)
    def allpaper(self, request):
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        user_id = request.session['id']
        type = request.session['type']
        if type == "1":
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
            if not len(papers):
                total_page = 1
            else:
                total_page = (len(papers) - 1) // PAGE_MAX + 1
            pages, pre_page, next_page = get_pages(total_page, page)
            papers = papers[PAGE_MAX * (page - 1): PAGE_MAX * page]

            context['papers'] = papers
            context['page'] = page
            context['pages'] = pages
            context['pre_page'] = pre_page
            context['next_page'] = next_page
            return HttpResponse(template.render(context, request))

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


class JoinViewSet(viewsets.ModelViewSet):
    queryset = Join.objects.all()
    serializer_class = JoinSerializer

    def create(self, request):
        message  = "未知错误"
        try:
            receipt = request.FILES['file']
            type = int(request.data.get("type"))
            try:
                userid = request.session['id']
                thisuser = User.objects.get(id = userid)
            except:
                message = "账户错误"
                raise RuntimeError()
            if type == 1:
                paperid = int(request.data.get("paper"))
                try:
                    thispaper = Paper.objects.get(id=paperid)

                except:
                    message = "论文错误"
                    raise RuntimeError()
                try:
                    thismeeting = Meeting.objects.get(meeting_id=thispaper.meeting_id)
                except:
                    message = "会议错误"
                    raise RuntimeError()
                if timezone.now()>thismeeting.regist_attend_date:
                    message = "注册时间已过"
                    raise RuntimeError()
                if thispaper.status != 1:
                    message = "提交的论文未通过"
                    raise RuntimeError()
                allparticate = thisuser.participate.all()
                if thismeeting in allparticate:
                    message = "已聆听，无法注册会议"
                    raise RuntimeError()
                count = 1
                namename = "name" + str(count)
                gendername = "gender" + str(count)
                resername = "reservation" + str(count)
                emailname = "email"+str(count)
                name = request.data.get(namename)
                while name is not None:
                    gender = request.data.get(gendername)
                    reservation = request.data.get(resername)
                    email = request.data.get(emailname)
                    people = Join(
                        name=name,
                        gender=gender,
                        receipt=receipt,
                        # content=request.data.get("content"),
                        reservation=reservation,
                        email = email,
                        types=1,
                        paper=thispaper,
                        meeting=thismeeting,
                    )
                    try:
                        people.save()
                    except:
                        message = name + "数据错误"
                        raise RuntimeError()
                    count = count + 1
                    namename = "name" + str(count)
                    gendername = "gender" + str(count)
                    resername = "reservation" + str(count)
                    emailname = "email" + str(count)
                    name = request.data.get(namename)
                #thispaper.owner.participate.add(thismeeting)
                #thispaper.owner.save()
                return HttpResponseRedirect('../user/allpaper/?message=注册成功')
            meetingid = int(request.data.get("meeting"))
            try:
                thismeeting = Meeting.objects.get(meeting_id=meetingid)
            except:
                message = "会议错误"
                raise RuntimeError()
            if timezone.now()>thismeeting.regist_attend_date:
                message = "注册时间已过"
                raise RuntimeError()

            allpaper = thisuser.paper_set.all()
            allmeeting = list()
            for paper in allpaper:
                if paper.status == 1:
                    alljoin = paper.join_set.all()
                    if alljoin != []:
                        for join in alljoin:
                            if join.meeting not in allmeeting:
                                allmeeting.append(join.meeting)

            if thismeeting in allmeeting:
                message = "已注册，无法聆听"
                raise RuntimeError()
            count = 1
            namename = "name" + str(count)
            gendername = "gender" + str(count)
            resername = "reservation" + str(count)
            emailname = "email" + str(count)
            name = request.data.get(namename)
            while name is not None:
                gender = request.data.get(gendername)
                reservation = request.data.get(resername)
                email = request.data.get(emailname)
                people = Join(
                    name=name,
                    gender=gender,
                    receipt=receipt,
                    # content=request.data.get("content"),
                    reservation=reservation,
                    email = email,
                    types=2,
                    meeting=thismeeting,
                )
                try:
                    people.save()
                except:
                    message = name + "数据错误"
                    raise RuntimeError()
                count = count + 1
                namename = "name" + str(count)
                gendername = "gender" + str(count)
                resername = "reservation" + str(count)
                emailname = "email" + str(count)
                name = request.data.get(namename)
            thisuser.participate.add(thismeeting)
            thisuser.save()
            url = '../../meeting/'+str(meetingid)+'/?message=聆听成功'
            return HttpResponseRedirect(url)
        except:
            url = '../../meeting/list2/?message='+message
            return HttpResponseRedirect(url)