from rest_framework import routers
from django.conf.urls import url, include
from User.views import *
router = routers.DefaultRouter()
router.register('user', UserViewSet)
router.register('join',JoinViewSet)

urlpatterns = router.urls