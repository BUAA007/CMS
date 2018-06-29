# Create your models here.
from django.db import models
import django.utils.timezone as timezone
class Meeting(models.Model):
	meeting_id = models.AutoField(
		primary_key = True,
		)
	title = models.CharField(
		max_length = 128,
		)
	intro = models.CharField(
		max_length = 256
		)
	essay_request = models.CharField(
		max_length = 64
		)
	ddl_date = models.DateTimeField(	#截稿日期

		)
	result_notice_date = models.DateTimeField(	#录用通知日期

		)
	regist_attend_date = models.DateTimeField(	#用户注册参加会议截止日期

		)
	meeting_date = models.DateTimeField(	#会议开始日期

		)
	schedule = models.CharField(
		max_length = 128
		)
	institution = models.CharField( #组织机构
		max_length = 128
		)
	template = models.CharField( 	#论文模板url
		max_length = 64
		)
	receipt	= models.CharField(		#pdf或jpg(url)
		max_length = 64
		)
	support = models.CharField(		#住宿交通
		max_length = 128
		)
	about_us = models.CharField(
		max_length = 128
		)