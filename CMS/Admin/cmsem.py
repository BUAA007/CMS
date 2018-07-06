import smtplib
from email.mime.text import MIMEText
mailto_list=['572260394@qq.com']           #收件人(列表)
mail_host="smtp.163.com"            #使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user="h529987"                           #用户名
mail_pass="15211009hlz"                             #密码
mail_postfix="163.com"                     #邮箱的后缀，网易就是163.com
def send_mail(to_list,sub,content):
    me="CMS团队"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain')
    msg['Subject'] = sub
    msg['From'] = me
    for to in to_list:
        msg['To'] = to                #将收件人列表以‘；’分隔
        try:
            server = smtplib.SMTP()
            server.connect(mail_host)                            #连接服务器
            server.login(mail_user,mail_pass)               #登录操作
            server.sendmail(me, to, msg.as_string())
            server.close()
        except:
            print("email error")
'''
for i in range(1):                             #发送1封，上面的列表是几个人，这个就填几
    if send_mail(mailto_list,"电话","电话是lalal"):  #邮件主题和邮件内容
        #这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
        print ("done!")
    else:
        print ("failed!")
'''
