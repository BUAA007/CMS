from django.shortcuts import render
from django.http import StreamingHttpResponse
def base(request):
    return render(request,'base.html')

def login(request):
    return render(request,'login.html')

def user_register(request):
	return render(request,'user_register.html')

def institution_register(request):
	return render(request,'institution_register.html')

def personal_info(request):
    return render(request, 'personal_info.html')

def download(request):
        def file_iterator(file_name, chunk_size=512):
                with open(file_name, "rb") as f:
                        while True:
                                c = f.read(chunk_size)
                                if c:
                                        yield c
                                else:
                                        break
        importlib.reload(sys)
        try:
                url = "/home/ubuntu/CMS/CMS/media/paper/"
                rootpath = request.path
                tmp = rootpath.split("paper/")
                url+=tmp[2]
        except:
                return Response(a, status = status.HTTP_400_BAD_REQUEST)
        if url is not None:
                response = StreamingHttpResponse(file_iterator(url))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="{0}"'.format(tmp[2])
                return response
        a = collections.OrderedDict({"errorInfo":"服务器出错，请稍后重试。"})
        return Response(a, status = status.HTTP_400_BAD_REQUEST)