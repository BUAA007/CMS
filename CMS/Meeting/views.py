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
from django.http import HttpResponse, StreamingHttpResponse
from django.template import loader
from User.models import *
from Institution.models import Employee
from django.utils import timezone
from datetime import datetime,date
from xlwt import *
import os
import collections

PAGE_MAX = 10

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
            return Response(errorInfo("succsss"), status=status.HTTP_200_OK)

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
        if not ddl_date:
            return HttpResponse(template.render(errorInfo("请填写正确截稿日期"), request))
        result_notice_date = request.data.get("result_notice_date"),
        if not result_notice_date:
            return HttpResponse(template.render(errorInfo("请填写正确论文通知日期"), request))
        regist_attend_date = request.data.get("regist_attend_date"),
        if not regist_attend_date:
            return HttpResponse(template.render(errorInfo("请填写正确用户参会注册截止日期"), request))
        meeting_date = request.data.get("meeting_date"),
        if not meeting_date:
            return HttpResponse(template.render(errorInfo("请填写正确会议开始日期"), request))
        meeting_end_date = request.data.get("meeting_end_date"),
        if not meeting_end_date:
            return HttpResponse(template.render(errorInfo("请填写正确会议结束日期"), request))
        receipt = request.data.get("receipt")
        if not receipt:
            return HttpResponse(template.render(errorInfo("请填写正用户参会注册所需费用"), request))
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
            )
            thisMeeting.save()
            return HttpResponse(template.render({"info": "会议发布成功"}), request)
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
            print(thisMeeting.status1,thisMeeting.status2,thisMeeting.status3,thisMeeting.status4,thisMeeting.status5)
            thisuser = User.objects.get(id=user_id)
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
                'map': "http://maps.google.com.tw/maps?f=q&hl=zh-TW&geocode=&q=" + thisMeeting.organization + "&z=16&output=embed&t=",
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
                'map': "http://maps.google.com.tw/maps?f=q&hl=zh-TW&geocode=&q=" + thisMeeting.organization + "&z=16&output=embed&t=",
            }
            return HttpResponse(template.render(context, request))


    @action(methods=['POST'], detail=False)
    def search(self, request):  # 根据时间搜索未写
        queryset = Meeting.objects.all()
        word = request.data.get('search', None)
        time1 = request.data.get('time1',None)
        time2 = request.data.get('time2',None)
        conditions = {}
        if word is not None:
            conditions['title__contains'] = word
        if time1 is not None:
            conditions['meeting_date__gte'] = time1
        if time2 is not None:
            conditions['meeting_date__lte'] = time2
        result = queryset.filter(**conditions)
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
