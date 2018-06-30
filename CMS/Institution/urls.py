from rest_framework import routers
from django.conf.urls import url, include
from .views import InstutionViewSet

router = routers.DefaultRouter()
router.register('Institution', InstitutionViewSet)
urlpatterns = router.urls 
