from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from Meeting.models import Meeting
from Meeting.serializers import MeetingSerializer
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from User.models import *
from Institution.models import Employee
from django.utils import timezone
from datetime import datetime, date
from xlwt import *
import os
import collections
import sys
sys.path.append('../')
from Admin import cmsem

PAGE_MAX = 9

def checkNull(msg):
    return msg


def errorInfo(msg):
    return {"errorInfo": str(msg)}


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def create(self, request):
       # try:
       template = loader.get_template('release_meeting.html')
       context = {}
       if request.session['type'] == '0' or request.session['is_login'] != 'true':
          return render(request, "base.html")

       thisEmployee = Employee.objects.get(username=request.session['username'])
       thisInstitution = thisEmployee.institution
       # if thisinstitution.status!="1":
       #    return Response({"errorInfo":"have not been received"}, status=status.HTTP_200_OK)
       title = request.data.get("title")
       if not title:
          return HttpResponse(template.render(errorInfo("会议标题不能为空"), request))
       about_us = request.data.get("about_us")
       if not about_us:
          return HttpResponse(template.render(errorInfo("联系我们不能为空"), request))
       ddl_date = request.data.get("ddl_date"),
       if ddl_date[0] == "":
          return HttpResponse(template.render(errorInfo("请填写正确截稿日期"), request))
       result_notice_date = request.data.get("result_notice_date"),
       if result_notice_date[0] == "":
          return HttpResponse(template.render(errorInfo("请填写正确论文通知日期"), request))
       regist_attend_date = request.data.get("regist_attend_date"),
       if regist_attend_date[0] == "":
          return HttpResponse(template.render(errorInfo("请填写正确用户参会注册截止日期"), request))
       meeting_date = request.data.get("meeting_date"),
       if meeting_date[0] == "":
          return HttpResponse(template.render(errorInfo("请填写正确会议开始日期"), request))
       meeting_end_date = request.data.get("meeting_end_date"),
       if meeting_end_date[0] == "":
          return HttpResponse(template.render(errorInfo("请填写正确会议结束日期"), request))
       receipt = request.data.get("receipt")
       if not receipt:
          return HttpResponse(template.render(errorInfo("请填写正确用户参会注册所需费用"), request))
       intro = request.data.get("intro")
       if not intro:
          return HttpResponse(template.render(errorInfo("请填写会议简介"), request))
       essay_request = request.data.get("essay_request")
       if not essay_request:
          return HttpResponse(template.render(errorInfo("请填写征文要求信息"), request))
       organization = request.data.get("organization")
       if not organization:
          return HttpResponse(template.render(errorInfo("请填写会议地址"), request))
       schedule = request.data.get("schedule")
       if not schedule:
          return HttpResponse(template.render(errorInfo("请填写会议日程安排"), request))
       support = request.data.get("support")
       if not support:
          return HttpResponse(template.render(errorInfo("请填写住宿交通信息"), request))
       file = request.FILES['file']
       if not file:
          return HttpResponse(template.render(errorInfo("请填写论文模板文件"), request))
       # meeting_serializer = MeetingSerializer(data = request.data)
       # return HttpResponse(request.session['username']+" "+str(ddl_date))
       # if meeting_serializer.is_valid():
       if (ddl_date <= result_notice_date) and (result_notice_date <= regist_attend_date) and (
             regist_attend_date <= meeting_date) and (meeting_date <= meeting_end_date):
          # return HttpResponse(request.session['username'])
          thisMeeting = Meeting(
             title=title,
             organization=organization,
             ddl_date=datetime.strptime(ddl_date[0], "%Y-%m-%dT%H:%M"),
             result_notice_date=datetime.strptime(result_notice_date[0], "%Y-%m-%dT%H:%M"),
             regist_attend_date=datetime.strptime(regist_attend_date[0], "%Y-%m-%dT%H:%M"),
             meeting_date=datetime.strptime(meeting_date[0], "%Y-%m-%dT%H:%M"),
             meeting_end_date=datetime.strptime(meeting_end_date[0], "%Y-%m-%dT%H:%M"),
             receipt=receipt,
             intro=intro,
             essay_request=essay_request,
             about_us=about_us,
             schedule=schedule,
             institution=thisInstitution,
             support=support,
             template=file,
          )
          thisMeeting.save()
          return HttpResponse(template.render({'info':'登记成功'}, request))
       # return HttpResponse("时间不合法")
       # return HttpResponse(meeting_serializer.errors)
       # except:
       #    pass
       return HttpResponse(template.render(errorInfo("填写的日期不合法"), request))

    @action(methods=['GET'], detail=False)
    def list2(self, request):
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        queryset = Meeting.objects.all().order_by('-meeting_id')
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

        list(map(check_time, queryset))
        context = {'conference_list': queryset}
        if not len(queryset):
            total_page = 1
        else:
            total_page = (len(queryset) - 1) // PAGE_MAX + 1
        pages, pre_page, next_page = get_pages(total_page, page)
        queryset = queryset[PAGE_MAX * (page - 1): PAGE_MAX * page]

        context['conference_list'] = queryset
        context['page'] = page
        context['pages'] = pages
        context['pre_page'] = pre_page
        context['next_page'] = next_page
        return HttpResponse(template.render(context, request))

    def retrieve(self, request, pk=None):
        thisMeeting = Meeting.objects.get(meeting_id=pk)
        # thisMeeting = get_object_or_404(queryset, pk=pk)
        # thisMeeting=Meeting.objects.get(meeting_id=pk)
        try:
            user_id = request.session['id']
            now = timezone.now()
            thisMeeting.status1 = False
            thisMeeting.status2 = False
            thisMeeting.status3 = False
            thisMeeting.status4 = False
            thisMeeting.status5 = False

            if now >= thisMeeting.ddl_date:
              thisMeeting.status1 = True
            if now >= thisMeeting.result_notice_date:
              thisMeeting.status2 = True
            if now >= thisMeeting.regist_attend_date:
              thisMeeting.status3 = True
            if now >= thisMeeting.meeting_date:
              thisMeeting.status4 = True
            if now >= thisMeeting.meeting_end_date:
              thisMeeting.status5 = True
            print(thisMeeting.status1, thisMeeting.status2, thisMeeting.status3, thisMeeting.status4,
               thisMeeting.status5)
            thisuser = User.objects.get(id=user_id)
            if now >= thisMeeting.ddl_date:
                thisMeeting.status1 = True
            if now >= thisMeeting.result_notice_date:
                thisMeeting.status2 = True
            if now >= thisMeeting.regist_attend_date:
                thisMeeting.status3 = True
            if now >= thisMeeting.meeting_date:
                thisMeeting.status4 = True
            if now >= thisMeeting.meeting_end_date:
                thisMeeting.status5 = True
            thisuser = User.objects.get(id=user_id)

            queryset = thisuser.participate.all()
            allpaper = thisuser.paper_set.all()
            allmeeting = list()
            for paper in allpaper:
                if paper.status == 1:
                    alljoin = paper.join_set.all()
                    if alljoin != []:
                        for join in alljoin:
                            if join.meeting not in allmeeting:
                                allmeeting.append(join.meeting)
            print(queryset)
            print(allmeeting)
            listenmeeting = set(queryset)-set(allmeeting)
            print(listenmeeting)
            if thisMeeting in listenmeeting:
                islisten = True
            else:
                islisten = False

            # return Response("info: contribute succsss", status=status.HTTP_200_OK)
            try:
                favorite = thisuser.favorite.get(meeting_id=thisMeeting.meeting_id)
            except:
                isfavorite = False
            else:
                isfavorite = True
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite': isfavorite,
                'islisten':islisten,
                'map': "http://maps.baidu.com/?p=" + thisMeeting.organization
            }

            return HttpResponse(template.render(context, request))
        except:
            now = timezone.now()
            thisMeeting.status1 = False
            thisMeeting.status2 = False
            thisMeeting.status3 = False
            thisMeeting.status4 = False
            thisMeeting.status5 = False

            if now>=thisMeeting.ddl_date:
                thisMeeting.status1=True
            if now>=thisMeeting.result_notice_date:
                thisMeeting.status2=True
            if now >= thisMeeting.regist_attend_date:
                thisMeeting.status3 = True
            if now>=thisMeeting.meeting_date:
                thisMeeting.status4=True
            if now>=thisMeeting.meeting_end_date:
                thisMeeting.status5=True
            print(thisMeeting.status1, thisMeeting.status2, thisMeeting.status3, thisMeeting.status4,thisMeeting.status5)
            #print(thisMeeting.status1)
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite': False,
                'islisten':False,
                'map': "https://maps.gaode.com/search?query=" + thisMeeting.organization ,
            }
            return HttpResponse(template.render(context, request))


    @action(methods=['GET'], detail=False)
    def search(self, request):  # 根据时间搜索未写
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        queryset = Meeting.objects.all()
        word = request.GET['word']
        time1 = request.GET['time1']
        time2 = request.GET['time2']
        if word is None:
            word = ""
        # word = request.data.get('word', None)
        # time1 = request.data.get('time1',None)
        # time2 = request.data.get('time2',None)
        conditions = {}
        if word !="":
            conditions['title__contains'] = word
        if time1 !="":
            conditions['meeting_date__gte'] = time1
        if time2 !="":
            conditions['meeting_date__lte'] = time2
        result = queryset.filter(**conditions)


        template = loader.get_template('search_list.html')
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
        if not len(result):
            total_page = 1
        else:
            total_page = (len(result) - 1) // PAGE_MAX + 1
        pages, pre_page, next_page = get_pages(total_page, page)
        result = result[PAGE_MAX * (page - 1): PAGE_MAX * page]

        context = {'conference_list': result}
        context['page'] = page
        context['pages'] = pages
        context['pre_page'] = pre_page
        context['next_page'] = next_page
        context['word'] = word
        context['time1'] = time1
        context['time2'] = time2

        list(map(check_time, result))

        return HttpResponse(template.render(context, request))


    @action(methods=['GET'], detail=False)
    def allpaper(self, request):
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        user_id = request.session['id']
        type = request.session['type']
        if type == "0":
            template = loader.get_template('judge.html')
            context = {
                # 'conference': thismeeting,
                'message': '失败，不是该会议的单位用户'
            }
            return HttpResponse(template.render(context, request))
        else:
            thisemployee = Employee.objects.get(id=user_id)
            institution = thisemployee.institution
            thismeeting = institution.meeting_set.all()
            # thismeeting = Meeting.objects.get(meeting_id=pk)
            paperslist = list()
            for i in thismeeting:
                papers = i.paper_set.all()
                paperslist += papers
            template = loader.get_template('judge.html')
            context = {
                'papers': paperslist,
            }
            if not len(paperslist):
                total_page = 1
            else:
                total_page = (len(paperslist) - 1) // PAGE_MAX + 1
            pages, pre_page, next_page = get_pages(total_page, page)
            paperslist = paperslist[PAGE_MAX * (page - 1): PAGE_MAX * page]

            context['papers'] = paperslist
            context['page'] = page
            context['pages'] = pages
            context['pre_page'] = pre_page
            context['next_page'] = next_page

            return HttpResponse(template.render(context, request))

    @action(methods=['POST'], detail=False)
    def alljoin(self, request):
        pk = request.data.get('pk', None)
        if pk is not None:
            thismeeting = Meeting.objects.get(meeting_id=pk)
            joinmen = thismeeting.join_set.all()
            template = loader.get_template('judgement.html')
            context = {
                'join': joinmen,
            }
            return HttpResponse(template.render(context, request))
        return Response({"errorInfo": "会议无效，服务器错误"}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def manageList(self, request):
      try:


         if (request.session["type"] == "1"):
            try:
               page = int(request.GET["page"])
            except(KeyError,ValueError):
               page = 1
            thisEmployee = Employee.objects.get(username=request.session['username'])
            queryset = Meeting.objects.filter(institution=thisEmployee.institution).order_by('-meeting_id')
            template = loader.get_template('manage_list.html')

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

            list(map(check_time, queryset))
            manage_list = []
            for x in queryset:
               dict = {}
               count = x.User_set.all().count()
               dict["manage"] = x
               dict["count"] = count
               manage_list.append(dict)

            context = {
               'manage_list': manage_list,
            }
            if not len(manage_list):
               total_page = 1
            else:
               total_page = (len(manage_list) - 1)
            pages, pre_page, next_page = get_pages(total_page, page)
            manage_list = manage_list[PAGE_MAX * (page-1) : PAGE_MAX * page]
            context['manage_list'] = manage_list
            context['page'] = page
            context['pages'] = pages
            context['pre_page'] = pre_page
            context['next_page'] = next_page

            return HttpResponse(template.render(context, request))
      except:
         pass
      return render(request, "base.html")

    @action(methods=['GET'], detail=False)
    def manage(self, request, pk=None):

      # thisMeeting = get_object_or_404(queryset, pk=pk)
      # thisMeeting=Meeting.objects.get(meeting_id=pk)
      try:
         thisMeeting = Meeting.objects.get(meeting_id=request.GET["pk"])
         if request.session["type"] == "1":
            thisEmployee = Employee.objects.get(username=request.session["username"])
         if thisMeeting.institution == thisEmployee.institution:
            now = timezone.now()
            thisMeeting.status1 = '0'
            thisMeeting.status2 = '0'
            thisMeeting.status3 = '0'
            thisMeeting.status4 = '0'
            thisMeeting.status5 = '0'

            if now >= thisMeeting.ddl_date:
               thisMeeting.status1 = '1'
            if now >= thisMeeting.result_notice_date:
               thisMeeting.status2 = '1'
            if now >= thisMeeting.regist_attend_date:
               thisMeeting.status3 = '1'
            if now >= thisMeeting.meeting_date:
               thisMeeting.status4 = '1'
            if now >= thisMeeting.meeting_end_date:
               thisMeeting.status5 = '1'
            print(thisMeeting.status1, thisMeeting.status2, thisMeeting.status3, thisMeeting.status4,
                  thisMeeting.status5)

            # return Response("info: contribute succsss", status=status.HTTP_200_OK)
            template = loader.get_template('manage.html')
            context = {
               'conference': thisMeeting,
               'result_notice_date': thisMeeting.result_notice_date.strftime("%Y-%m-%dT%H:%M"),
               'regist_attend_date': thisMeeting.regist_attend_date.strftime("%Y-%m-%dT%H:%M"),
               'meeting_date': thisMeeting.meeting_date.strftime("%Y-%m-%dT%H:%M"),
               'meeting_end_date': thisMeeting.meeting_end_date.strftime("%Y-%m-%dT%H:%M"),
               'ddl_date': thisMeeting.ddl_date.strftime("%Y-%m-%dT%H:%M"),
            }
            return HttpResponse(template.render(context, request))
      except:
         pass
      return render(request, "base.html")

    @action(methods=['POST'], detail=False)
    def updateTemplate(self, request):
      template = loader.get_template('manage.html')
      if request.session['type'] == '0' or request.session['is_login'] != 'true':
         return render(request, "base.html")
      # try:
      thisEmployee = Employee.objects.get(username=request.session['username'])
      thisInstitution = thisEmployee.institution
      thisMeeting = Meeting.objects.get(meeting_id=int(request.data.get("meeting_id")))
      print("haha")
      print(request.FILES['file'])
      a = Meeting(
         meeting_id=thisMeeting.meeting_id,
         template=request.FILES['file'],
         title=thisMeeting.title,
         organization=thisMeeting.organization,
         ddl_date=thisMeeting.ddl_date,
         result_notice_date=thisMeeting.result_notice_date,
         regist_attend_date=thisMeeting.regist_attend_date,
         meeting_date=thisMeeting.meeting_date,
         meeting_end_date=thisMeeting.meeting_end_date,
         receipt=thisMeeting.receipt,
         intro=thisMeeting.intro,
         essay_request=thisMeeting.essay_request,
         about_us=thisMeeting.about_us,
         schedule=thisMeeting.schedule,
         institution=thisMeeting.institution,
         support=thisMeeting.support,
      )
      a.save()
      emailTitle = "CMS系统提示，会议信息发生修改"
      emailContent = "会议id为" + str(thisMeeting.meeting_id) + "的会议信息发生修改，请查看" + "http://127.0.0.1:8000/meeting/" + str(
         thisMeeting.meeting_id) + "/"
      userSet = thisMeeting.User_set.all()
      AttendeeSet = thisMeeting.Attendee_set.all()
      emailList = []
      for user in userSet:
         emailList.append(user.email)
      for user in AttendeeSet:
         emailList.append(user.email)
      cmsem.send_mail(emailList, emailTitle, emailContent)
      return HttpResponseRedirect("/meeting/manage/?pk=" + str(thisMeeting.meeting_id))
      # except:
      #    pass
      return HttpResponse(template.render(errorInfo("传输文件发生错误"), request))

    @action(methods=['POST'], detail=False)
    def updateMeeting(self, request):
      # try:
      template = loader.get_template('manage.html')
      if request.session['type'] == '0' or request.session['is_login'] != 'true':
         return render(request, "base.html")

      thisEmployee = Employee.objects.get(username=request.session['username'])
      thisInstitution = thisEmployee.institution
      thisMeeting = Meeting.objects.get(meeting_id=request.data.get("id"))

      # if thisinstitution.status!="1":
      #    return Response({"errorInfo":"have not been received"}, status=status.HTTP_200_OK)

      title = request.data.get("title")
      if not title:
         return Response(errorInfo("会议标题不能为空"), content_type="application/json")
      about_us = request.data.get("about_us")
      if not about_us:
         return Response(template.render(errorInfo("请填写住宿交通信息"), request))
      ddl_date = request.data.get("ddl_date"),

      if ddl_date[0] == "":
         return Response(errorInfo("请填写正确截稿日期"), content_type="application/json")
      result_notice_date = request.data.get("result_notice_date"),
      if result_notice_date[0] == "":
         return Response(errorInfo("请填写正确论文通知日期"), content_type="application/json")
      regist_attend_date = request.data.get("regist_attend_date"),

      if regist_attend_date[0] == "":
         return Response(errorInfo("请填写正确用户参会注册截止日期"), content_type="application/json")
      meeting_date = request.data.get("meeting_date"),
      if meeting_date[0] == "":
         return Response(errorInfo("请填写正确会议开始日期"), content_type="application/json")
      meeting_end_date = request.data.get("meeting_end_date"),

      if meeting_end_date[0] == "":
         return Response(errorInfo("请填写正确会议结束日期"), content_type="application/json")
      receipt = request.data.get("receipt")
      if not receipt:
         return Response(errorInfo("请填写正确用户参会注册所需费用"), content_type="application/json")
      intro = request.data.get("intro")

      if not intro:
         return Response(errorInfo("请填写会议简介"), content_type="application/json")
      essay_request = request.data.get("essay_request")

      if not essay_request:
         return Response(errorInfo("请填写征文要求信息"), content_type="application/json")
      organization = request.data.get("organization")

      if not organization:
         return Response(errorInfo("请填写会议地址"), content_type="application/json")
      schedule = request.data.get("schedule")

      if not schedule:
         return Response(errorInfo("请填写会议日程安排"), content_type="application/json")
      support = request.data.get("support")
      if not support:
         return Response(errorInfo("请填写住宿交通信息"), content_type="application/json")

      # meeting_serializer = MeetingSerializer(data = request.data)
      # return HttpResponse(request.session['username']+" "+str(ddl_date))
      # if meeting_serializer.is_valid():
      if (ddl_date <= result_notice_date) and (result_notice_date <= regist_attend_date) and (
            regist_attend_date <= meeting_date) and (meeting_date <= meeting_end_date):
         # return HttpResponse(request.session['username'])
         # thisMeeting.meeting_id = request.data.get("id")
         thisMeeting = Meeting(
            meeting_id=request.data.get("id"),
            title=title,
            organization=organization,
            ddl_date=datetime.strptime(ddl_date[0], "%Y-%m-%dT%H:%M"),
            result_notice_date=datetime.strptime(result_notice_date[0], "%Y-%m-%dT%H:%M"),
            regist_attend_date=datetime.strptime(regist_attend_date[0], "%Y-%m-%dT%H:%M"),
            meeting_date=datetime.strptime(meeting_date[0], "%Y-%m-%dT%H:%M"),
            meeting_end_date=datetime.strptime(meeting_end_date[0], "%Y-%m-%dT%H:%M"),
            receipt=receipt,
            intro=intro,
            essay_request=essay_request,
            about_us=about_us,
            schedule=schedule,
            institution=thisInstitution,
            support=support,

         )
         thisMeeting.save()
         # thisMeeting.support = support,
         # thisMeeting.save(update_fields=['tel'])
         # thisMeeting.save()
         emailTitle = "CMS系统提示，会议信息发生修改"
         emailContent = "会议id为" + str(
            thisMeeting.meeting_id) + "的会议信息发生修改，请查看" + "http://127.0.0.1:8000/meeting/" + str(
            thisMeeting.meeting_id) + "/"
         userSet = thisMeeting.User_set.all()
         AttendeeSet = thisMeeting.Attendee_set.all()
         emailList = []

         for user in userSet:
            emailList.append(user.email)
         for user in AttendeeSet:
            emailList.append(user.email)
         cmsem.send_mail(emailList, emailTitle, emailContent)
         return Response({'info': '已发送邮件通知'}, content_type="application/json")

      # return HttpResponse("时间不合法")
      # return HttpResponse(meeting_serializer.errors)
      # except:
      #    pass
      return Response(errorInfo("传递时间不合法"), content_type="application/json")

    @action(methods=['POST','GET'],detail=False)
    def allregistermeeting(self,request):
        user_id=request.session['id']
        thisuser=User.objects.get(id=user_id)
        allpaper=thisuser.paper_set.all()
        allmeeting=list()
        for paper in allpaper:
            if paper.status==1:
                alljoin=paper.join_set.all()
                if alljoin!=[]:
                    for join in alljoin :
                        if join.meeting not in allmeeting:
                            allmeeting.append(join.meeting)
        print(allmeeting)
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        queryset = sorted(allmeeting, key=lambda x: x.ddl_date)
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

        list(map(check_time, queryset))
        context = {'conference_list': queryset}
        if not len(queryset):
            total_page = 1
        else:
            total_page = (len(queryset) - 1) // PAGE_MAX + 1
        pages, pre_page, next_page = get_pages(total_page, page)
        queryset = queryset[PAGE_MAX * (page - 1): PAGE_MAX * page]

        context['conference_list'] = queryset
        context['page'] = page
        context['pages'] = pages
        context['pre_page'] = pre_page
        context['next_page'] = next_page
        return HttpResponse(template.render(context, request))

    @action(methods=['POST'], detail=False)
    def alljoinmeeting(self, request):
        user_id=request.session['id']
        thisuser = User.object.get(id=user_id)
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        queryset=thisuser.participate.all().order_by('-meeting_id')
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
        list(map(check_time, queryset))
        context = {'conference_list': queryset}
        if not len(queryset):
            total_page = 1
        else:
            total_page = (len(queryset) - 1) // PAGE_MAX + 1
        pages, pre_page, next_page = get_pages(total_page, page)
        queryset = queryset[PAGE_MAX * (page - 1): PAGE_MAX * page]

        context['conference_list'] = queryset
        context['page'] = page
        context['pages'] = pages
        context['pre_page'] = pre_page
        context['next_page'] = next_page
        return HttpResponse(template.render(context, request))

    @action(methods=['POST','GET'], detail=False)
    def alllistenmeeting(self, request):
        user_id = request.session['id']
        thisuser = User.objects.get(id=user_id)
        try:
            page = int(request.GET['page'])
        except (KeyError, ValueError):
            page = 1
        queryset = thisuser.participate.all().order_by('-meeting_id')
        allpaper = thisuser.paper_set.all()
        allmeeting = list()
        for paper in allpaper:
            if paper.status == 1:
                alljoin = paper.join_set.all()
                if alljoin != []:
                    for join in alljoin:
                        if join.meeting not in allmeeting:
                            allmeeting.append(join.meeting)
        listenmeeting = set(queryset) - set(allmeeting)
        queryset = sorted(listenmeeting, key=lambda x: x.ddl_date)
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
        list(map(check_time, queryset))
        context = {'conference_list': queryset}
        if not len(queryset):
            total_page = 1
        else:
            total_page = (len(queryset) - 1) // PAGE_MAX + 1
        pages, pre_page, next_page = get_pages(total_page, page)
        queryset = queryset[PAGE_MAX * (page - 1): PAGE_MAX * page]

        context['conference_list'] = listenmeeting
        context['page'] = page
        context['pages'] = pages
        context['pre_page'] = pre_page
        context['next_page'] = next_page
        return HttpResponse(template.render(context, request))

    @action(methods=['POST'], detail=False)
    def excel_export(self, request):
        """
        导出excel表格
        """
        meeting = int(request.data.get("meeting"))
        thismeeting = Meeting.objects.get(meeting_id = meeting)
        url = "excel/"+thismeeting.title+".xls"
        list_obj = thismeeting.paper_set.all()
        if list_obj:
            # 创建工作薄 投稿编号、作者、题目、单位、摘要等内容
            ws = Workbook(encoding='utf-8')
            w = ws.add_sheet(u"投稿信息")
            w.write(0, 0, u"投稿编号")
            w.write(0, 1, u"第一作者")
            w.write(0, 2, u"题目")
            w.write(0, 3, u"摘要")
            w.write(0, 4, u"关键字")
            # 写入数据
            excel_row = 1
            for obj in list_obj:
                data_id = obj.id
                data_author = obj.author_1
                data_title = obj.title
                data_abstract = obj.abstract
                dada_keyword = obj.keyword
                w.write(excel_row, 0, data_id)
                w.write(excel_row, 1, data_author)
                w.write(excel_row, 2, data_title)
                w.write(excel_row, 3, data_abstract)
                w.write(excel_row, 4, dada_keyword)
                excel_row += 1
            # 检测文件是够存在
            # 方框中代码是保存本地文件使用，如不需要请删除该代码
            ###########################
            exist_file = os.path.exists(url)
            if exist_file:
                os.remove(url)
            ws.save(url)
            ############################
        else:
            a = collections.OrderedDict({"errorInfo":"服务器出错，请稍后重试。"})
            return Response(a, status = status.HTTP_400_BAD_REQUEST)
        def file_iterator(file_name, chunk_size=512):
            with open(file_name, "rb") as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
        if url is not None:
            response = StreamingHttpResponse(file_iterator(url))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(tmp[-1])
            return response
        a = collections.OrderedDict({"errorInfo":"服务器出错，请稍后重试。"})
        return Response(a, status = status.HTTP_400_BAD_REQUEST)

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