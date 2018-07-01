from rest_framework import routers
from django.conf.urls import url, include
from .views import InstitutionViewSet,EmployeeViewSet

router = routers.DefaultRouter()
router.register('Institution', InstitutionViewSet)
router.register('Employee', EmployeeViewSet)
urlpatterns = router.urls 
