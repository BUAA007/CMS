from rest_framework import routers
from django.conf.urls import url, include
from .views import MeetingViewSet

router = routers.DefaultRouter()
router.register('Meeting', MeetingViewSet)
urlpatterns = router.urls 
