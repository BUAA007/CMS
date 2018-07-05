import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMS.settings")

django.setup()
import cmsem
from User.models import *
from Meeting.models import *
from datetime import datetime

if __name__ == "__main__":
	to_list = ["572260394@qq.com", "540670802@qq.com", "490072639@qq.com"]
	to_list2 = ["572260394@qq.com", "540670802@qq.com", "490072639@qq.com"]

	allmeeting = Meeting.objects.all()
	time = datetime.now()
	sub = "收藏会议提示"
	content = "您收藏的会议即将截稿"
	sub2 = "收藏会议提示"
	content2 = "您收藏的会议即将停止注册"
	
	for meeting in allmeeting:
		if (meeting.ddl_date - time).days == 1 or (meeting.ddl_date - time).days == 0:
			for user in meeting.User_set.all():
				to_list.append(user.email)
		if (meeting.regist_attend_date - time).days == 1 or (meeting.regist_attend_date - time).days == 0:
			for user in meeting.User_set.all():
				to_list2.append(user.email)
	cmsem.send_mail(to_list, sub, content)
	cmsem.send_mail(to_list2, sub2, content2)