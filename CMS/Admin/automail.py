import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMS.settings")

django.setup()

from User.models import *
from Meeting.models import *
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
mailto_list=['572260394@qq.com']           #收件人(列表)
mail_host="smtp.163.com"            #使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user="h529987"                           #用户名
mail_pass="15211009hlz"                             #密码
mail_postfix="163.com"                     #邮箱的后缀，网易就是163.com

if __name__ == "__main__":
	to_list = ["572260394@qq.com", "540670802@qq.com", "490072639@qq.com"]
	to_list2 = ["572260394@qq.com", "540670802@qq.com", "490072639@qq.com"]
	me="CMS团队"+"<"+mail_user+"@"+mail_postfix+">"
	msg['From'] = me
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
	server = smtplib.SMTP()
	server.connect(mail_host)                            #连接服务器
	server.login(mail_user,mail_pass)
	
	msg = MIMEText(content,_subtype='plain')
	msg['Subject'] = sub
	msg['To'] = ";".join(to_list)                #将收件人列表以‘；’分隔
	server.sendmail(me, to_list, msg.as_string())
	msg = MIMEText(content2,_subtype='plain')
	msg['Subject'] = sub2
	msg['To'] = ";".join(to_list2)                #将收件人列表以‘；’分隔
	server.sendmail(me, to_list2, msg.as_string())
	server.close()