from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:name>/<str:emotion>', views.emotions, name='emotions'),
    path('delete/<str:name>/<str:emotion>', views.delete_image, name='delete_image'),
    path('add/<str:name>/<str:emotion>', views.add_image, name='add_image'),
    path('new_avatar', views.new_avatar, name='new_avatar'),
    path('video', views.static_video, name='static_video'),
    # path('realtime_video', views.realtime_video, name='realtime_video'),
]