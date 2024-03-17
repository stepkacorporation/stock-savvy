from django.urls import path, include

from rest_framework import routers

from .views import StockViewSet

router = routers.SimpleRouter()
router.register('stocks', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
