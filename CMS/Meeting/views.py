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

from django.http import HttpResponse
from django.template import loader
from User.models import * 
from Institution.models import Employee
import datetime
from datetime import *

def checkNull(msg):
    return msg

def errorInfo(msg):
    return {"errorInfo":str(msg)}

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    
    def create(self, request):
        #try:
        if request.session['type'] == '0' or request.session['is_login'] != 'true':
            return Response(errorInfo("succsss"), status=status.HTTP_200_OK)

        thisEmployee = Employee.objects.get( username = request.session['username'])
        thisInstitution= thisEmployee.institution
        #if thisinstitution.status!="1":
        #    return Response({"errorInfo":"have not been received"}, status=status.HTTP_200_OK)
        title = request.data.get("title")
        if not title:
            return HttpResponse(errorInfo("会议标题不能为空"), content_type="application/json")
        about_us = request.data.get("about_us")
        if not about_us:
            return HttpResponse(errorInfo("联系我们不能为空"), content_type="application/json")
        ddl_date=request.data.get("ddl_date"),
        if not ddl_date:
            return HttpResponse(errorInfo("请填写截稿日期"), content_type="application/json" )
        result_notice_date = request.data.get("result_notice_date"),
        if not result_notice_date:
            return HttpResponse(errorInfo("请填写论文通知日期"), content_type="application/json" )
        regist_attend_date = request.data.get("regist_attend_date"),
        if not regist_attend_date:
            return HttpResponse(errorInfo("请填写用户参会注册截止日期"), content_type="application/json" )
        meeting_date = request.data.get("meeting_date"),
        if not meeting_date:
            return HttpResponse(errorInfo("请填写会议开始日期"),content_type="application/json" )
        meeting_end_date=request.data.get("meeting_end_date"),
        if not meeting_end_date:
            return HttpResponse(errorInfo("请填写会议结束日期"),content_type="application/json" )
        receipt = request.data.get("receipt")
        if not receipt:
            return HttpResponse(errorInfo("请填写用户参会注册所需费用"), content_type="application/json" )
        intro = request.data.get("intro")
        if not intro:
            return HttpResponse(errorInfo("请填写会议简介"), content_type="application/json" )
        essay_request = request.data.get("essay_request")
        if not essay_request:
            return HttpResponse(errorInfo("请填写征文要求信息"), content_type="application/json" )
        organization = request.data.get("organization")
        if not organization:
            return HttpResponse(errorInfo("请填写会议地址"),content_type="application/json" )
        schedule = request.data.get("schedule")
        if not schedule:
            return HttpResponse(errorInfo("请填写会议日程安排"), content_type="application/json" )
        support = request.data.get("support")
        if not support:
            return HttpResponse(errorInfo("请填写住宿交通信息"), content_type="application/json" )
        #meeting_serializer = MeetingSerializer(data = request.data)
        #return HttpResponse(request.session['username']+" "+str(ddl_date))
        #if meeting_serializer.is_valid():
        if (ddl_date<=result_notice_date) and (result_notice_date<=regist_attend_date) and (regist_attend_date<=meeting_date) and (meeting_date<=meeting_end_date):
            #return HttpResponse(request.session['username'])
            thisMeeting = Meeting(
                title = title,
                organization = organization,
                ddl_date = datetime.strptime(ddl_date[0], "%Y-%m-%dT%H:%M"),
                result_notice_date = datetime.strptime(result_notice_date[0], "%Y-%m-%dT%H:%M"),
                regist_attend_date = datetime.strptime(regist_attend_date[0], "%Y-%m-%dT%H:%M"),
                meeting_date = datetime.strptime(meeting_date[0], "%Y-%m-%dT%H:%M"),
                meeting_end_date=datetime.strptime(meeting_end_date[0], "%Y-%m-%dT%H:%M"),
                receipt = receipt,
                intro = intro,
                essay_request = essay_request,
                about_us = about_us,
                schedule = schedule,
                institution = thisInstitution,
                )
            thisMeeting.save()
            return HttpResponse({"info":"meeting is created"},status=status.HTTP_200_OK)
        #return HttpResponse("时间不合法")
            #return HttpResponse(meeting_serializer.errors)
        #except:
        #    pass
        return HttpResponse(errorInfo("填写的日期不合法"),status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def list2(self, request):
        queryset = Meeting.objects.all().order_by('-meeting_id') 
        template = loader.get_template('conference_list.html')
        # def check_time(conference):
        #     now_time = datetime.datetime.now()
        #     if now_time > conference.meeting_end_date:
        #         conference.status = '已结束'
        #     elif now_time < conference.meeting_date:
        #         conference.status = '未开始'
        #     else:
        #         conference.status = '正在进行'
        # list(map(check_time, queryset))
        context = {'conference_list': queryset}
        return HttpResponse(template.render(context, request))



    def retrieve(self ,request,pk=None):
        thisMeeting=Meeting.objects.get(meeting_id=pk)
        try:
            user_id=request.session['id']
            #user_id=request.session.get['id']
            thisuser=User.objects.get(id=user_id)
            #return Response("info: contribute succsss", status=status.HTTP_200_OK)

            try:
                favorite=thisuser.favorite.get(meeting_id=thisMeeting.meeting_id)
            except:
                isfavorite = False
            else :
                isfavorite =True
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite':isfavorite
            }
            return HttpResponse(template.render(context, request))
        except:
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite': False
            }
            return HttpResponse(template.render(context, request))



    @action(methods=['GET'], detail=False)
    def showdetail(self, request):
        pk = request.query_params.get('pk',None)
        thisMeeting=Meeting.objects.get(meeting_id=pk)
        papers=thisMeeting.paper_set.all()

        try:
            user_id=request.session['id']
            #user_id=request.session.get['id']
            #user_id = request.session['id']
            thisuser=User.objects.get(id=user_id)
            try:
                favorite=thisuser.favorite.get(meeting_id=thisMeeting.meeting_id)
            except:
                isfavorite = False
            else :
                isfavorite =True
            i=0
            paper_list=list()
            serializer = MeetingSerializer(thisMeeting)
            paper_list.append(serializer.data)
            paper_info={"title":"","author":""}
            for paper in papers:
                paper_info["title"]=paper.title
                paper_info["author"]=paper.author_1
                paper_list.append(paper_info)
                i=i+1
                if i>=10:
                    break
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite':isfavorite
            }
            return HttpResponse(template.render(context, request))
        except:
            template = loader.get_template('conference.html')
            context = {
                'conference': thisMeeting,
                'isfavorite': False,
            }
            return HttpResponse(template.render(context, request))


    @action(methods=['GET'],detail=False)
    def osearch(self, request):
        queryset = Meeting.objects.all()
        word = request.query_params.get('s', None)
        if word is not None:
            queryset = Meeting.objects.filter(title__contains = word)
        serializer = MeetingSerializer(queryset, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @action(methods=['GET'],detail=False)
    def allpaper(self, request):
        pk = request.query_params.get('pk', None)
        thismeeting = Meeting.objects.get(meeting_id=pk)
        papers = thismeeting.paper_set.all()
        template = loader.get_template('judge.html')
        context = {
            'papers': papers,
        }
        return HttpResponse(template.render(context, request))

