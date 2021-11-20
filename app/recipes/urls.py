from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientsViewSet)

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls))
]
