from rest_framework import routers
from django.conf.urls import url, include
from .views import InstitutionViewSet

router = routers.DefaultRouter()
router.register('Institution', InstitutionViewSet)
urlpatterns = router.urls 
