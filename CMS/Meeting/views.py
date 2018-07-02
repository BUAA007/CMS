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
class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    '''
    def create(self, request):
        meeting_serializer=MeetingSerializer(data=request.data)
        #Institution_id = request.session['id']
        #Institution_id = request.data.get('institution_id')
        #employee_id = request.data.get('employee_id')
        #thisemployee=Employee.objects.get(id=employee_id)
        #if thisinstitution.status!=1:
        #   return Response({"errorInfo":"have not been received"}, status=status.HTTP_200_OK)
        employee_id = 1#request.session['id']
        thisinstitution=Employee.objects.get(id=employee_id).institution  
        if thisinstitution.status!=1:
            return Response({"errorInfo":"have not been received"}, status=status.HTTP_200_OK)
        title = request.data.get("title")
        intro = request.data.get("intro")
        essay_request = request.data.get("essay_request")
        ddl_date = request.data.get("ddl_date")
        result_notice_date = request.data.get("result_notice_date")
        regist_attend_date = request.data.get("regist_attend_date")
        meeting_date = request.data.get("meeting_date")
        meeting_end_date=request.data.get("meeting_end_date")
        schedule = request.data.get("schedule")
        #thisinstitution=request.data.get("institution")
        #return Response(thisinstitution.name,status=status.HTTP_200_OK)
        if meeting_serializer.is_valid():
            if (ddl_date<=result_notice_date) and (result_notice_date<=regist_attend_date) and (regist_attend_date<=meeting_date) and (meeting_date<=meeting_end_date):
                return Response("2",status=status.HTTP_200_OK)
                thisMeeting = Meeting(title = request.data.get("title"),
                    intro = request.data.get("intro"),
                    essay_request = request.data.get("essay_request"),
                    ddl_date = request.data.get("ddl_date"),
                    result_notice_date = request.data.get("result_notice_date"),
                    regist_attend_date = request.data.get("regist_attend_date"),
                    meeting_date = request.data.get("meeting_date"),
                    meeting_end_date=request.data.get("meeting_end_date"),
                    schedule = request.data.get("schedule"),
                    )
                thisMeeting.save()
                #thisinstitution.meetings.add(thisMeeting)
                return Response(thisMeeting.meeting_id, status=status.HTTP_200_OK)
            return Response("error: Meeting is not valid",status=status.HTTP_200_OK)
        return Response({"error":"Meeting is not valid"},status=status.HTTP_200_OK)
    '''
    
    def list(self, request):
        queryset = Meeting.objects.all().order_by('-meeting_id') 
        template = loader.get_template('conference_list.html')
        context = {'conference_list': queryset}
        return HttpResponse(template.render(context, request))


    def retrieve(self ,request,pk=None):
        thisMeeting=Meeting.objects.get(meeting_id=pk)
        try:
            user_id=1
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
            user_id=request.session.get['id']
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